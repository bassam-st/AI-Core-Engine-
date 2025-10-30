# engine/xtream_proxy.py — Xtream Proxy (متوافق مع main.py + تجاوز 403 + كاش)
from __future__ import annotations
import os, time, re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse

# ========= إعدادات من البيئة =========
XTREAM_BASE  = os.getenv("XTREAM_BASE", "").rstrip("/")   # مثال: http://mhiptv.info:2095
XTREAM_USER  = os.getenv("XTREAM_USER", "")
XTREAM_PASS  = os.getenv("XTREAM_PASS", "")
XTREAM_SECRET = os.getenv("XTREAM_SECRET", os.getenv("SECRET_KEY", "bassam-secret"))

if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
    print("⚠️ XTREAM_BASE/USER/PASS غير مضبوطة في البيئة.")

# ========= جلسة HTTP مع ترويسات تحاكي IPTV Smarters لتخطي 403 =========
HEADERS = {
    "User-Agent": "IPTV-Smarters-Player/3.1 (Android) ExoPlayer",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Language": "ar,en;q=0.9",
    "Referer": XTREAM_BASE or "http://localhost",
    "Origin": XTREAM_BASE or "http://localhost",
}
CLIENT = httpx.Client(headers=HEADERS, timeout=25, follow_redirects=True, http2=True)

# ========= كاش بسيط في الذاكرة =========
_cache: Dict[str, Dict[str, Any]] = {}
def _cache_get(key: str, ttl: int = 90) -> Optional[Any]:
    rec = _cache.get(key)
    if not rec: return None
    if time.time() - rec["t"] > ttl:
        _cache.pop(key, None)
        return None
    return rec["v"]

def _cache_set(key: str, value: Any):
    _cache[key] = {"v": value, "t": time.time()}

# ========= أدوات مساعدة =========
def _require_conf():
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, "لم تضبط XTREAM_BASE/USER/PASS")

def _api_url(params: Dict[str, Any] | None = None) -> str:
    q = {"username": XTREAM_USER, "password": XTREAM_PASS}
    if params:
        q.update(params)
    return f"{XTREAM_BASE}/player_api.php?{urlencode(q)}"

def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    _require_conf()
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

def _normalize_name(s: str) -> str:
    s = re.sub(r"[\s\u200f\u200e]+", " ", s or "").strip()
    return s

# ========= الراوتر =========
router = APIRouter(prefix="/api/xtream", tags=["xtream"])

@router.get("/info")
def xtream_info():
    """معلومات الحساب والسيرفر (للتشخيص)."""
    _require_conf()
    key = "xtream:info"
    c = _cache_get(key, ttl=60)
    if c: return c
    try:
        r = CLIENT.get(_api_url())
        r.raise_for_status()
        data = r.json()
        _cache_set(key, data)
        return data
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Upstream error: {e}")

@router.get("/channels")
def xtream_channels(q: str = Query(default="", description="بحث (اختياري)")):
    """
    يُرجع قائمة القنوات بصيغة متوافقة مع /ui/xtream في main.py:
    { count, items: [{stream_id, name, category, m3u8}] }
    """
    _require_conf()
    key = f"xtream:channels:{q or ''}"
    c = _cache_get(key, ttl=60)
    if c: return c

    url = _api_url({"action": "get_live_streams"})
    try:
        r = CLIENT.get(url)
        r.raise_for_status()
        arr = r.json() if r.headers.get("content-type","").startswith("application/json") else []
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Upstream error: {e}")

    out: List[Dict[str, Any]] = []
    ql = (q or "").strip().lower()
    for it in arr or []:
        try:
            sid = it.get("stream_id")
            nm  = _normalize_name(it.get("name", ""))
            cat = str(it.get("category_id", "") or "")
            if not sid or not nm:
                continue
            if ql and ql not in nm.lower():
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
    واجهة بسيطة تُرجع رابط البث النهائي كنص (لاستخدامه مباشرة في مشغّل /ui/sports_player).
    مثال: /api/xtream/play/22  -> يُرجع http://.../live/user/pass/22.m3u8
    """
    try:
        url = build_live_url(stream_id, ext)
        return PlainTextResponse(url)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search_by_teams")
def search_by_teams(home: str, away: str, league: str = ""):
    """
    بحث ذكي يطابق أسماء الفرق/الدوري داخل أسماء القنوات ويُرجع أول قناة مطابقة.
    """
    try:
        data = xtream_channels().get("items", [])
    except Exception:
        data = []
    needles = [s.lower() for s in [home, away, league] if s]
    for ch in data:
        name = ch["name"].lower()
        if any(n and n in name for n in needles):
            ch["match"] = True
            return ch
    return {"match": False}
