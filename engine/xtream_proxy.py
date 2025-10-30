# engine/xtream_proxy.py
from __future__ import annotations
import os
from urllib.parse import urljoin
from typing import Optional, Dict, Any, List

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# إعدادات من البيئة
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER = os.getenv("XTREAM_USER", "")
XTREAM_PASS = os.getenv("XTREAM_PASS", "")

TIMEOUT = httpx.Timeout(15.0, connect=10.0, read=25.0)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0 Safari/537.36",
    "Accept": "*/*",
}

def _assert_env():
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(status_code=500, detail="XTREAM_BASE/USER/PASS غير مُضبوطة.")

def _player_api_url(action: Optional[str] = None) -> str:
    base = f"{XTREAM_BASE}/player_api.php?username={XTREAM_USER}&password={XTREAM_PASS}"
    return f"{base}&action={action}" if action else base

def build_live_url(stream_id: str | int, ext: str = "m3u8") -> str:
    _assert_env()
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

async def _fetch_json(url: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(
            headers=HEADERS, timeout=TIMEOUT, follow_redirects=True, http2=False
        ) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

@router.get("/info")
async def xtream_info():
    """اختبار سريع: يتصل بالحساب ويرجع معلومات المستخدم/الخادم."""
    _assert_env()
    data = await _fetch_json(_player_api_url())
    return JSONResponse(
        {
            "ok": True,
            "user": {
                "username": data.get("user_info", {}).get("username"),
                "status": data.get("user_info", {}).get("status"),
                "exp_date": data.get("user_info", {}).get("exp_date"),
                "auth": data.get("user_info", {}).get("auth"),
                "conns": data.get("user_info", {}).get("active_cons"),
            },
            "server": {
                "url": data.get("server_info", {}).get("url"),
                "port": data.get("server_info", {}).get("port"),
                "https_port": data.get("server_info", {}).get("https_port"),
                "protocol": data.get("server_info", {}).get("server_protocol"),
            },
        }
    )

@router.get("/channels")
async def xtream_channels(q: str | None = Query(default=None)):
    """
    يرجع قائمة مبسّطة بالقنوات الحيّة: id, name, category, logo, live_url.
    يدعم فلترة نصية بسيطة عبر ?q=
    """
    _assert_env()
    data = await _fetch_json(_player_api_url("get_live_streams"))

    rows: List[Dict[str, Any]] = []
    for ch in data if isinstance(data, list) else []:
        name = str(ch.get("name", ""))
        stream_id = str(ch.get("stream_id", ""))
        cat = ch.get("category_name") or ch.get("category_id") or ""
        logo = ch.get("stream_icon") or ""
        row = {
            "id": stream_id,
            "name": name,
            "category": cat,
            "logo": logo,
            "live_url": build_live_url(stream_id),
        }
        rows.append(row)

    if q:
        lq = q.strip().lower()
        rows = [r for r in rows if lq in r["name"].lower() or lq in str(r["category"]).lower()]

    return {"count": len(rows), "channels": rows}

@router.get("/live-url/{stream_id}")
async def xtream_live_url(stream_id: str):
    """يرجع رابط m3u8 النهائي لقناة معيّنة."""
    return {"url": build_live_url(stream_id)}

@router.get("/open/{stream_id}")
async def xtream_open(stream_id: str):
    """
    يعيد توجيه 302 مباشرة إلى m3u8 (تنفع لفتح الرابط خارجياً).
    ملاحظة: قد يحجب المزوّد الطلب من المتصفح؛ جرّب عبر مشغل داخلي.
    """
    return RedirectResponse(build_live_url(stream_id), status_code=302)
