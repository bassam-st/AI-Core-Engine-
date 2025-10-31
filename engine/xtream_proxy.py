# engine/xtream_proxy.py — Final
from __future__ import annotations
import os
from typing import Any, Dict, List
from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# بيئة
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER = os.getenv("XTREAM_USER", "")
XTREAM_PASS = os.getenv("XTREAM_PASS", "")
TIMEOUT = 20

UA = "Mozilla/5.0 (Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Mobile Safari"
HEADERS = {
    "User-Agent": UA,
    "Accept": "application/json, text/plain, */*",
}

def _assert_env():
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, detail="XTREAM env vars missing (XTREAM_BASE/USER/PASS)")

def _client() -> httpx.Client:
    # http2=False لتفادي مشاكل h2 على بعض البنى
    return httpx.Client(headers=HEADERS, timeout=TIMEOUT, http2=False, follow_redirects=True)

def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    _assert_env()
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

def _player_api(params: Dict[str, Any]) -> Dict[str, Any] | List[Dict[str, Any]]:
    _assert_env()
    url = f"{XTREAM_BASE}/player_api.php"
    q = {"username": XTREAM_USER, "password": XTREAM_PASS, **params}
    with _client() as c:
        r = c.get(url, params=q)
        if r.status_code == 403:
            raise HTTPException(403, detail="403 from upstream (Xtream). افتح BASE من المتصفح للتحقق.")
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}

@router.get("/info")
def xtream_info():
    data = _player_api({})
    return JSONResponse({"ok": True, "info": data})

@router.get("/channels")
def xtream_channels():
    # نحاول جلب كل القنوات الحية
    data = _player_api({"action": "get_live_streams"})
    raw = []
    if isinstance(data, list):
        raw = data
    else:
        raw = data.get("available_channels") or data.get("streams") or []
    channels: List[Dict[str, Any]] = []
    for ch in raw:
        channels.append({
            "stream_id": ch.get("stream_id"),
            "name": ch.get("name"),
            "category": ch.get("category_name") or ch.get("category_id"),
            "logo": ch.get("stream_icon"),
        })
    return {"ok": True, "count": len(channels), "channels": channels}

@router.get("/m3u8/{stream_id}")
def xtream_m3u8(stream_id: int):
    # يُعيد رابط m3u8 المباشر (بدون تمرير عبر الخادم)
    url = build_live_url(stream_id, "m3u8")
    return {"ok": True, "url": url}

# ====== بروكسي m3u8 + المقاطع (لتجاوز Mixed Content) ======

def _live_path(stream_id: str, file: str) -> str:
    # بعض السيرفرات تستخدم مجلد باسم stream_id للمقاطع
    # إن لم يكن كذلك فسنحاول المسار الرئيسي
    return f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}/{file}"

@router.get("/stream/{stream_id}.m3u8")
async def proxy_m3u8(stream_id: str):
    _assert_env()
    # نحاول أولًا manifest داخل مجلد stream_id
    src1 = urljoin(XTREAM_BASE + "/", _live_path(stream_id, f"{stream_id}.m3u8").lstrip("/"))
    # بديل: مباشرة بدون مجلد
    src2 = build_live_url(stream_id, "m3u8")
    async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
        r = await client.get(src1)
        if r.status_code >= 400 or "#EXTM3U" not in r.text:
            r = await client.get(src2)
            if r.status_code >= 400:
                raise HTTPException(status_code=r.status_code, detail=r.text[:200])

    # إعادة كتابة روابط المقاطع لتسير عبر بروكسي أيضًا
    text = r.text
    # استبدال أي اسم .ts ليذهب لمسار /seg/
    text = text.replace(f"{stream_id}.ts", f"/api/xtream/seg/{stream_id}/{stream_id}.ts")
    return Response(content=text, media_type="application/vnd.apple.mpegurl")

@router.get("/seg/{stream_id}/{seg_name}")
async def proxy_segment(stream_id: str, seg_name: str):
    _assert_env()
    # نجرب المسار داخل المجلد:
    src = urljoin(XTREAM_BASE + "/", _live_path(stream_id, seg_name).lstrip("/"))
    async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
        r = await client.get(src)
    if r.status_code >= 400 or not r.content:
        # بديل: مباشرة بدون مجلد
        alt = urljoin(XTREAM_BASE + "/", f"live/{XTREAM_USER}/{XTREAM_PASS}/{seg_name}")
        async with httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, follow_redirects=True) as client:
            r = await client.get(alt)
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail="segment fetch error")
    return Response(content=r.content, media_type="video/MP2T")
