# engine/xtream_proxy.py
from __future__ import annotations
import os
from typing import Any, Dict, List
from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# ـــــــــ إعدادات البيئة ـــــــــ
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")        # مثال: http://mhiptv.info:2095
XTREAM_USER = os.getenv("XTREAM_USER", "")                    # مثال: 47482
XTREAM_PASS = os.getenv("XTREAM_PASS", "")                    # مثال: 395847

UA = "Mozilla/5.0 (Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Mobile Safari"
HEADERS = {"User-Agent": UA, "Accept": "application/json, text/plain, */*"}
TIMEOUT = 20  # ثواني

def _assert_env():
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, detail="XTREAM env vars missing")

# عميل متزامن (للاستدعاءات السريعة)
def _client() -> httpx.Client:
    # http2=False لتفادي h2 في Render المجاني
    return httpx.Client(headers=HEADERS, timeout=TIMEOUT, http2=False, follow_redirects=True)

# عميل لا تزامني (للميديا m3u8/ts)
def _aclient() -> httpx.AsyncClient:
    return httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, http2=False, follow_redirects=True)

# يبني رابط مباشر على سيرفر Xtream
def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    _assert_env()
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

# يستدعي player_api.php
def _player_api(params: Dict[str, Any]) -> Dict[str, Any]:
    _assert_env()
    url = f"{XTREAM_BASE}/player_api.php"
    q = {"username": XTREAM_USER, "password": XTREAM_PASS, **params}
    with _client() as c:
        r = c.get(url, params=q)
        if r.status_code == 403:
            # بعض السيرفرات تمنع رندر/سيرفرات خارجية
            raise HTTPException(403, detail="403 from upstream (Xtream). افتح BASE من المتصفح للتأكد من السماح.")
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}

# معلومات اشتراك
@router.get("/info")
def xtream_info():
    data = _player_api({})
    return JSONResponse({"ok": True, "info": data})

# قائمة القنوات الحية
@router.get("/channels")
def xtream_channels():
    data = _player_api({"action": "get_live_streams"})
    channels: List[Dict[str, Any]] = []
    raw: List[Dict[str, Any]] = []
    if isinstance(data, list):
        raw = data
    else:
        raw = data.get("available_channels") or data.get("streams") or []
    for ch in raw:
        channels.append({
            "stream_id": ch.get("stream_id"),
            "name": ch.get("name"),
            "category": ch.get("category_name") or ch.get("category_id"),
            "logo": ch.get("stream_icon"),
        })
    return {"ok": True, "count": len(channels), "channels": channels}

# نُرجِع رابط m3u8 المباشر (بدون بروكسي) للاستخدام الاختياري
@router.get("/m3u8/{stream_id}")
def xtream_m3u8(stream_id: int):
    url = build_live_url(stream_id, "m3u8")
    return {"ok": True, "url": url}

# ـــــــــ بروكسي آمن لتمرير m3u8 وملفات TS عبر التطبيق ـــــــــ

def _live_path(stream_id: str, file: str) -> str:
    return f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}/{file}"

@router.get("/stream/{stream_id}.m3u8")
async def proxy_m3u8(stream_id: str):
    _assert_env()
    # مثال المصدر: http://host:port/live/user/pass/22/22.m3u8 أو أحيانًا .../22.m3u8
    # نغطي الحالتين:
    src1 = urljoin(XTREAM_BASE + "/", _live_path(stream_id, f"{stream_id}.m3u8").lstrip("/"))
    src2 = build_live_url(stream_id, "m3u8")  # /live/user/pass/22.m3u8

    async with _aclient() as client:
        r = await client.get(src1)
        if r.status_code >= 400:
            # جرّب الشكل الثاني
            r = await client.get(src2)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text[:200])

    # نعيد المانيفست مع تحويل روابط القطع لتذهب عبر بروكسينا
    manifest = r.text

    # بعض السيرفرات تُرجع روابط نسبية مثل "22.ts" أو "index0.ts" أو مسارات أطول
    # نحول أي سطر ينتهي بـ .ts ليصبح على شكل /api/xtream/seg/{stream_id}/{seg_name}
    new_lines: List[str] = []
    for line in manifest.splitlines():
        ln = line.strip()
        if ln and not ln.startswith("#") and ln.endswith(".ts"):
            seg_name = ln.split("/")[-1]
            new_lines.append(f"/api/xtream/seg/{stream_id}/{seg_name}")
        else:
            new_lines.append(line)
    patched = "\n".join(new_lines)

    return Response(content=patched, media_type="application/vnd.apple.mpegurl")

@router.get("/seg/{stream_id}/{seg_name}")
async def proxy_segment(stream_id: str, seg_name: str):
    _assert_env()
    # مثال: http://host:port/live/user/pass/22/xxxxx.ts
    src = urljoin(XTREAM_BASE + "/", _live_path(stream_id, seg_name).lstrip("/"))
    async with _aclient() as client:
        r = await client.get(src)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail="segment fetch error")
    return Response(content=r.content, media_type="video/MP2T")
