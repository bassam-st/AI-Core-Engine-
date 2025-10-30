# engine/xtream_proxy.py
from __future__ import annotations
import os, time, re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse

# ========= إعدادات من البيئة =========
XTREAM_BASE  = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER  = os.getenv("XTREAM_USER", "")
XTREAM_PASS  = os.getenv("XTREAM_PASS", "")
XTREAM_SECRET = os.getenv("XTREAM_SECRET", os.getenv("SECRET_KEY", "bassam-secret"))

if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
    print("⚠️ XTREAM_BASE/USER/PASS غير مضبوطة في البيئة.")

# ========= جلسة HTTP مع ترويسات تحاكي IPTV Smarters =========
HEADERS = {
    "User-Agent": "IPTV-Smarters-Player/3.1 (Android) ExoPlayer",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Language": "ar,en;q=0.9",
    "Referer": XTREAM_BASE or "http://localhost",
}
CLIENT = httpx.Client(headers=HEADERS, timeout=20)

# ========= كاش بسيط في الذاكرة =========
_cache: Dict[str, Dict[str, Any]] = {}
def _cache_get(key: str, ttl: int = 60) -> Optional[Any]:
    entry = _cache.get(key)
    if not entry: 
        return None
    if time.time() - entry["t"] > ttl:
        _cache.pop(key, None)
        return None
    return entry["v"]

def _cache_set(key: str, value: Any):
    _cache[key] = {"v": value, "t": time.time()}

# ========= أدوات مساعدة =========
def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise RuntimeError("XTREAM env vars are missing")
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

def _api_url(params: Dict[str, Any] = {}) -> str:
    q = {"username": XTREAM_USER, "password": XTREAM_PASS}
    q.update(params or {})
    return f"{XTREAM_BASE}/player_api.php?{urlencode(q)}"

def _normalize_name(s: str) -> str:
    s = re.sub(r"[\s\u200f\u200e]+", " ", s or "").strip()
    return s

# ========= الراوتر =========
router = APIRouter(prefix="/api/xtream", tags=["xtream"])

@router.get("/info")
def xtream_info():
    """معلومة الحساب والسيرفر (يُنفع للتشخيص)."""
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, "لم تضبط XTREAM_BASE/USER/PASS")
    key = "info"
    cached = _cache_get(key, ttl=60)
    if cached:
        return cached
    try:
        r = CLIENT.get(_api_url())
        r.raise_for_status()
        data = r.json()
        _cache_set(key, data)
        return data
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Upstream error: {e}") from e

@router.get("/channels")
def xtream_channels(q: str = Query(default="", description="بحث (اختياري)")):
    """يرجع قائمة القنوات الحية (stream_id, name, category)."""
    key = f"channels:{q}"
    cached = _cache_get(key, ttl=60)
    if cached:
        return cached

    url = _api_url({"action": "get_live_streams"})
    try:
        r = CLIENT.get(url)
        r.raise_for_status()
        arr = r.json()
    except httpx.HTTPError as e:
        # كثير من السيرفرات تُرجع 403 إذا شمت رائحة متصفح — هذه الجلسة تقللها جدًا.
        raise HTTPException(502, f"Upstream error: {e}") from e
    except Exception:
        arr = []

    out: List[Dict[str, Any]] = []
    for it in arr or []:
        try:
            sid = it.get("stream_id")
            nm  = _normalize_name(it.get("name", ""))
            cat = str(it.get("category_id", "")) or ""
            if not sid or not nm:
                continue
            if q and q.strip():
                qq = q.strip().lower()
                if qq not in nm.lower():
                    continue
            out.append({
                "stream_id": str(sid),
                "name": nm,
                "category": cat,
                "m3u8": build_live_url(sid, "m3u8"),
            })
        except Exception:
            continue

    res = {"count": len(out), "items": out}
    _cache_set(key, res)
    return res

@router.get("/play/{stream_id}")
def xtream_play(stream_id: str, ext: str = "m3u8"):
    """
    يعيد رابط m3u8 النهائي (أو يعمل كتمرير/بروكسي مستقبلاً).
    الآن نُرجع الرابط كنص صريح لتستخدمه واجهة الفيديو.
    """
    try:
        url = build_live_url(stream_id, ext)
    except Exception as e:
        raise HTTPException(500, str(e))
    return PlainTextResponse(url)

@router.get("/search_by_teams")
def search_by_teams(home: str, away: str, league: str = ""):
    """
    محاولة ذكية لإيجاد قناة عبر الكلمات (home/away/league) داخل أسماء القنوات.
    """
    chans = xtream_channels().get("items", [])
    keyw = [home, away, league]
    keyw = [k.lower() for k in keyw if k and len(k) > 1]

    for ch in chans:
        name = ch["name"].lower()
        if any(k in name for k in keyw):
            ch["match"] = True
            return ch
    return {"match": False}
