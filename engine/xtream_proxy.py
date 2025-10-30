# engine/xtream_proxy.py
from __future__ import annotations
import os, re, asyncio
from typing import Any, Dict, List
from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response, PlainTextResponse, RedirectResponse

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# =======================
# إعدادات وعميل HTTP
# =======================
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")          # مثال: http://mhiptv.info:2095
XTREAM_USER = os.getenv("XTREAM_USER", "")                      # مثال: 47482
XTREAM_PASS = os.getenv("XTREAM_PASS", "")                      # مثال: 395847

UA = "IPTVSmartersPlayer/1.0 (Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Mobile"
HEADERS = {
    "User-Agent": UA,
    "Accept": "*/*",
    "Connection": "keep-alive",
}
TIMEOUT = httpx.Timeout(25.0)

def _assert_env():
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, detail="XTREAM env vars missing")

def _live_path(stream_id: str, tail: str) -> str:
    """
    يبني المسار النسبي داخل Xtream: /live/user/pass/<stream_id>/<tail>
    أمثلة tail: 'index.m3u8' أو 'fileSequence0.ts'
    """
    return f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}/{tail}"

def build_live_url(stream_id: int | str, file_or_ext: str = "m3u8") -> str:
    """
    إن أُعطي امتدادًا -> يعيد .../<id>.m3u8
    وإن أُعطي اسم ملف -> يعيد .../<id>/<file>
    """
    _assert_env()
    if "." in file_or_ext or "/" in file_or_ext:
        path = _live_path(str(stream_id), file_or_ext)
    else:
        path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{file_or_ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

def _client() -> httpx.AsyncClient:
    # http2=False تجنبًا لمشكلة h2 في Render المجاني
    return httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, http2=False, follow_redirects=True)

# =======================
# استعلامات API الأساسية
# =======================
async def _player_api(params: Dict[str, Any]) -> Dict[str, Any] | List[Dict[str, Any]]:
    _assert_env()
    url = f"{XTREAM_BASE}/player_api.php"
    q = {"username": XTREAM_USER, "password": XTREAM_PASS, **params}
    async with _client() as c:
        r = await c.get(url, params=q)
        if r.status_code == 403:
            # السيرفر يمنع مصدر الطلب (Render/متصفح). سنستخدم البروكسي للمشاهدة لاحقًا.
            raise HTTPException(403, detail="403 from upstream (Xtream).")
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}

@router.get("/info")
async def xtream_info():
    data = await _player_api({})
    return JSONResponse({"ok": True, "info": data})

@router.get("/channels")
async def xtream_channels():
    """
    يجلب قنوات البث المباشر مهما اختلف شكل الاستجابة (available_channels / streams / list)
    """
    data = await _player_api({"action": "get_live_streams"})
    channels: List[Dict[str, Any]] = []

    def _norm_one(ch: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "stream_id": ch.get("stream_id") or ch.get("num") or ch.get("id"),
            "name": ch.get("name") or ch.get("stream_display_name"),
            "category": ch.get("category_name") or ch.get("category_id"),
            "logo": ch.get("stream_icon") or ch.get("logo"),
        }

    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        raw = data.get("available_channels") or data.get("streams") or data.get("live") or []
        # في بعض السيرفرات "live" تكون قاموس تصنيفات
        if isinstance(raw, dict):
            all_list: List[Dict[str, Any]] = []
            for v in raw.values():
                if isinstance(v, list):
                    all_list.extend(v)
            raw = all_list
    else:
        raw = []

    for ch in raw:
        try:
            norm = _norm_one(ch)
            if norm["stream_id"] and norm["name"]:
                channels.append(norm)
        except Exception:
            pass

    return {"ok": True, "count": len(channels), "channels": channels}

# =======================
# مشغل بروكسي HLS (m3u8 + TS)
# =======================
# /api/xtream/m3u8/<id> يعيد رابط مباشر (للتطبيقات الخارجية)
@router.get("/m3u8/{stream_id}")
async def xtream_m3u8_link(stream_id: str):
    return {"ok": True, "url": build_live_url(stream_id, "m3u8")}

# /api/xtream/stream/<id>.m3u8 يعيد ملف m3u8 مُعاد الكتابة ليمر عبر البروكسي
@router.get("/stream/{stream_id}.m3u8")
async def proxy_m3u8(stream_id: str):
    _assert_env()
    # بعض السيرفرات تعيد index.m3u8 داخل مجلد باسم الـid، وأخرى تعيد <id>.m3u8 مباشرة.
    # نجرب الاحتمالين بالترتيب.
    candidates = [
        build_live_url(stream_id, f"{stream_id}.m3u8"),
        build_live_url(stream_id, "index.m3u8"),
        build_live_url(stream_id, f"{stream_id}/index.m3u8"),
    ]
    text = None
    async with _client() as c:
        for src in candidates:
            r = await c.get(src)
            if r.status_code < 400 and (r.headers.get("content-type","").lower().find("mpegurl") >= 0 or r.text.startswith("#EXTM3U")):
                text = r.text
                break
        if text is None:
            raise HTTPException(404, detail="m3u8 not found/upstream")

    # إعادة كتابة كل الروابط النسبية داخل m3u8 (ملفات .ts وm3u8 الثانوية) إلى بروكسينا
    # أمثلة روابط داخلية قد تكون:
    # fileSequence0.ts
    # chunklist_w123456.m3u8
    # أو مسارات أعمق مثل 12345/fileSequence1.ts
    def _rewrite(line: str) -> str:
        l = line.strip()
        if not l or l.startswith("#"):
            return line
        if l.startswith("http://") or l.startswith("https://"):
            # نحول أي مطلق إلى مجرد اسم نسبي ثم نمرره على /seg
            # لكن أسلم: نترك المطلق كما هو (بعض السيرفرات تعطي مطلق ولن يقبل التحويل)
            return f"/api/xtream/raw?u={l}"
        # نسبي → حوله إلى /seg/<id>/<relative>
        return f"/api/xtream/seg/{stream_id}/{l}"

    rewritten = []
    for line in text.splitlines():
        if line.startswith("#"):
            rewritten.append(line)
        else:
            rewritten.append(_rewrite(line))

    out_text = "\n".join(rewritten)
    return Response(content=out_text, media_type="application/vnd.apple.mpegurl")

# /api/xtream/seg/<id>/<path> لجلب مقاطع TS أو قوائم فرعية
@router.get("/seg/{stream_id}/{path:path}")
async def proxy_segment(stream_id: str, path: str):
    _assert_env()
    upstream = build_live_url(stream_id, path)
    async with _client() as c:
        r = await c.get(upstream)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail="segment fetch error")
        ct = r.headers.get("content-type","").lower()
        if ".m3u8" in path or "mpegurl" in ct:
            # m3u8 فرعي → أعد كتابته أيضًا
            text = r.text

            def _rw(line: str) -> str:
                l = line.strip()
                if not l or l.startswith("#"): return line
                if l.startswith("http://") or l.startswith("https://"):
                    return f"/api/xtream/raw?u={l}"
                return f"/api/xtream/seg/{stream_id}/{l}"

            out = "\n".join(_rw(ln) for ln in text.splitlines())
            return Response(content=out, media_type="application/vnd.apple.mpegurl")

        # TS/MP2T أو بايتات عامة
        media = "video/MP2T" if path.endswith(".ts") else ct or "application/octet-stream"
        return Response(content=r.content, media_type=media)

# تمرير أي رابط مطلق من داخل m3u8 (كحل لبعض السيرفرات)
@router.get("/raw")
async def passthrough(u: str):
    async with _client() as c:
        r = await c.get(u)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail="raw fetch error")
        return Response(content=r.content, media_type=r.headers.get("content-type","application/octet-stream"))

# رابط قصير يوجّه المشغّل إلى m3u8 المُعاد كتابته
@router.get("/play/{stream_id}")
async def play_redirect(stream_id: str):
    return RedirectResponse(url=f"/api/xtream/stream/{stream_id}.m3u8")
