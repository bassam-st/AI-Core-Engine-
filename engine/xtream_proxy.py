# engine/xtream_proxy.py
from __future__ import annotations
import os
from typing import Any, Dict, List
from urllib.parse import urljoin
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# === إعدادات Xtream ===
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")  # مثال: http://mhiptv.info:2095
XTREAM_USER = os.getenv("XTREAM_USER", "")  # مثال: 47482
XTREAM_PASS = os.getenv("XTREAM_PASS", "")  # مثال: 395847

UA = "IPTVSmarterPlayer/1.0 (Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Mobile"
HEADERS = {
    "User-Agent": UA,
    "Accept": "*/*",
    "Connection": "keep-alive"
}
TIMEOUT = httpx.Timeout(25.0)

# === أدوات داخلية ===
def _assert_env():
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, detail="XTREAM env vars missing")

def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, http2=False, follow_redirects=True)

def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    _assert_env()
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

# === API رئيسي ===
@router.get("/info")
async def xtream_info():
    _assert_env()
    url = f"{XTREAM_BASE}/player_api.php"
    params = {"username": XTREAM_USER, "password": XTREAM_PASS}
    async with _client() as c:
        r = await c.get(url, params=params)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    return JSONResponse({"ok": True, "info": data})

@router.get("/channels")
async def xtream_channels():
    _assert_env()
    url = f"{XTREAM_BASE}/player_api.php"
    params = {"username": XTREAM_USER, "password": XTREAM_PASS, "action": "get_live_streams"}
    async with _client() as c:
        r = await c.get(url, params=params)
    try:
        data = r.json()
    except Exception:
        raise HTTPException(500, detail="Invalid JSON response from Xtream server")

    channels: List[Dict[str, Any]] = []
    raw = data if isinstance(data, list) else data.get("available_channels") or data.get("streams") or []
    for ch in raw:
        channels.append({
            "stream_id": ch.get("stream_id"),
            "name": ch.get("name"),
            "category": ch.get("category_name") or ch.get("category_id"),
            "logo": ch.get("stream_icon"),
        })
    return {"ok": True, "count": len(channels), "channels": channels}

@router.get("/m3u8/{stream_id}")
async def xtream_m3u8(stream_id: int):
    url = build_live_url(stream_id, "m3u8")
    return {"ok": True, "url": url}

# === تجاوز الحجب (Proxy) ===
@router.get("/stream/{stream_id}.m3u8")
async def proxy_m3u8(stream_id: str):
    _assert_env()
    src = urljoin(XTREAM_BASE + "/", f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}/{stream_id}.m3u8".lstrip("/"))
    async with _client() as c:
        r = await c.get(src)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text[:200])

    text = r.text.replace(f"{stream_id}.ts", f"/api/xtream/seg/{stream_id}/{stream_id}.ts")
    return Response(content=text, media_type="application/vnd.apple.mpegurl")

@router.get("/seg/{stream_id}/{seg_name}")
async def proxy_segment(stream_id: str, seg_name: str):
    _assert_env()
    src = urljoin(XTREAM_BASE + "/", f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}/{seg_name}".lstrip("/"))
    async with _client() as c:
        r = await c.get(src)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail="segment fetch error")
    return Response(content=r.content, media_type="video/MP2T")
