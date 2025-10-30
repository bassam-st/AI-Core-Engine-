# engine/xtream_proxy.py
from __future__ import annotations
import os
from typing import Any, Dict, List
from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# بيئة
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER = os.getenv("XTREAM_USER", "")
XTREAM_PASS = os.getenv("XTREAM_PASS", "")
UA = "Mozilla/5.0 (Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Mobile Safari"
HEADERS = {"User-Agent": UA, "Accept": "application/json, text/plain, */*"}

def _assert_env():
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, detail="XTREAM env vars missing")

def _client() -> httpx.Client:
    # http2=False لتفادي خطأ h2 على Render، مع مهلة افتراضية
    return httpx.Client(headers=HEADERS, timeout=20, http2=False, follow_redirects=True)

def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    _assert_env()
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

def _player_api(params: Dict[str, Any]) -> Dict[str, Any]:
    _assert_env()
    url = f"{XTREAM_BASE}/player_api.php"
    q = {"username": XTREAM_USER, "password": XTREAM_PASS, **params}
    with _client() as c:
        r = c.get(url, params=q)
        if r.status_code == 403:
            # بعض السيرفرات تمنع رندر: نُرجِع رسالة واضحة
            raise HTTPException(403, detail="403 from upstream (Xtream). جرب فتح BASE من المتصفح للتأكد من السماح.")
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            # بعض السيرفرات ترجع نصًا — نحاول ثانية بطلب action مخصص
            return {"raw": r.text}

@router.get("/info")
def xtream_info():
    data = _player_api({})
    return JSONResponse({"ok": True, "info": data})

@router.get("/channels")
def xtream_channels():
    # نجلب القنوات الحية
    data = _player_api({"action": "get_live_streams"})
    channels: List[Dict[str, Any]] = []
    # بعض السيرفرات ترجع مصفوفة مباشرة
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

@router.get("/m3u8/{stream_id}")
def xtream_m3u8(stream_id: int):
    # لا نمرّر الفيديو عبر Render (لأنها خطة مجانية/قد تُغلق)، فقط نعيد رابطًا مباشرًا
    url = build_live_url(stream_id, "m3u8")
    # نُعيده كـ JSON لتستخدمه واجهة الفيديو
    return {"ok": True, "url": url}
