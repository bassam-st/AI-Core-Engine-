# engine/xtream_proxy.py  — Advanced Xtream Proxy (Render-friendly)
from __future__ import annotations
import os, time, re, base64
from urllib.parse import urljoin, urlparse, urlunparse, quote, unquote
from typing import Dict, Any, List, Tuple, Optional

import httpx
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse, PlainTextResponse, JSONResponse

# ====== الإعدادات من البيئة ======
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER = os.getenv("XTREAM_USER", "")
XTREAM_PASS = os.getenv("XTREAM_PASS", "")
XTREAM_SECRET = os.getenv("XTREAM_SECRET", "")  # اختياري: نفس SECRET_KEY

if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
    print("⚠️ XTREAM_* vars are missing. Set XTREAM_BASE / XTREAM_USER / XTREAM_PASS on Render.")

UA = (
    "Mozilla/5.0 (Linux; Android 13; SM-S928B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36"
)

client = httpx.Client(timeout=20, headers={
    "User-Agent": UA,
    "Accept": "*/*",
    "Connection": "keep-alive",
})

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# ====== كاش بسيط بالذاكرة ======
_cache: Dict[str, Tuple[float, Any]] = {}
def cache_get(key: str, ttl: int = 60):
    rec = _cache.get(key)
    if not rec: return None
    ts, val = rec
    if time.time() - ts > ttl:
        _cache.pop(key, None)
        return None
    return val

def cache_set(key: str, value: Any):
    _cache[key] = (time.time(), value)

# ====== أدوات مساعدة ======
def _api(path: str, **params) -> str:
    base = f"{XTREAM_BASE}/player_api.php"
    qs = "&".join([f"username={quote(XTREAM_USER)}", f"password={quote(XTREAM_PASS)}"])
    if params:
        extra = "&".join([f"{k}={quote(str(v))}" for k,v in params.items()])
        qs = f"{qs}&{extra}"
    return f"{base}?{qs}"

def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    """الرابط الأصلي لدى المزود"""
    return urljoin(XTREAM_BASE + "/", f"live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}")

def _absolute(base_url: str, rel: str) -> str:
    # يحول الروابط داخل m3u8 إلى مطلقة بناءً على الـ base_url
    if rel.startswith("http://") or rel.startswith("https://"):
        return rel
    b = urlparse(base_url)
    if rel.startswith("/"):
        return urlunparse((b.scheme, b.netloc, rel, "", "", ""))
    # مسار نسبي
    prefix = b.path.rsplit("/", 1)[0] + "/"
    return urlunparse((b.scheme, b.netloc, prefix + rel, "", "", ""))

def _encode(u: str) -> str:
    return base64.urlsafe_b64encode(u.encode()).decode()

def _decode(s: str) -> str:
    return base64.urlsafe_b64decode(s.encode()).decode()

# ====== خدمات أساسية: معلومات + قوائم ======
def _safe_json(url: str) -> Any:
    try:
        r = client.get(url)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(502, f"Upstream error: {e}")

@router.get("/info")
def info():
    data = _safe_json(_api(""))
    ui = data.get("user_info", {})
    si = data.get("server_info", {})
    return {
        "ok": True,
        "user": {
            "username": ui.get("username"),
            "status": ui.get("status"),
            "max_connections": ui.get("max_connections"),
            "active_cons": ui.get("active_cons"),
            "allowed_output_formats": ui.get("allowed_output_formats"),
            "exp_date": ui.get("exp_date"),
        },
        "server": {
            "url": si.get("url"),
            "port": si.get("port"),
            "https_port": si.get("https_port"),
            "tz": si.get("timezone"),
        },
    }

def _live_streams_raw() -> List[Dict[str, Any]]:
    cache_key = "live_streams"
    cached = cache_get(cache_key, ttl=120)
    if cached is not None:
        return cached
    data = _safe_json(_api("", action="get_live_streams"))
    cache_set(cache_key, data)
    return data

@router.get("/streams")
def streams(q: Optional[str] = None, cat_id: Optional[str] = None):
    """قائمة القنوات المباشرة (مع رابط تشغيل بروكسي جاهز)"""
    raw = _live_streams_raw()
    items = []
    for ch in raw:
        if cat_id and str(ch.get("category_id")) != str(cat_id): 
            continue
        name = str(ch.get("name", ""))
        if q and q.strip():
            if q.lower() not in name.lower():
                continue
        sid = str(ch.get("stream_id"))
        logo = ch.get("stream_icon") or ""
        items.append({
            "id": sid,
            "name": name,
            "category_id": ch.get("category_id"),
            "logo": logo,
            "play": f"/api/xtream/play/{sid}.m3u8",   # نشغّل من داخل تطبيقك
            "direct": build_live_url(sid),           # رابط المزود الأصلي (إن احتجته)
        })
    return {"ok": True, "count": len(items), "items": items}

@router.get("/categories")
def categories():
    data = _safe_json(_api("", action="get_live_categories"))
    cats = [{"id": c.get("category_id"), "name": c.get("category_name")} for c in data]
    return {"ok": True, "items": cats}

# ====== تشغيل عبر بروكسي: m3u8 + القطع ======
def _fetch(url: str) -> httpx.Response:
    # ترويسات تساعد على تجاوز بعض الحمايات
    headers = {
        "User-Agent": UA,
        "Accept": "*/*",
        "Origin": XTREAM_BASE,
        "Referer": XTREAM_BASE + "/",
    }
    r = client.get(url, headers=headers, follow_redirects=True)
    r.raise_for_status()
    return r

def _rewrite_m3u8(master_text: str, base_url: str, stream_id: str) -> str:
    """
    يعيد كتابة كل الروابط داخل m3u8 لتصبح عبر بروكسي التطبيق:
      - قوائم فرعية/جودات: -> /api/xtream/play/{id}.m3u8?u=ENC(url)
      - القطع TS/M4S:      -> /api/xtream/seg/{id}?u=ENC(url)
    """
    lines = []
    for line in master_text.splitlines():
        L = line.strip()
        if not L or L.startswith("#"):
            lines.append(L)
            continue
        absu = _absolute(base_url, L)
        if absu.lower().endswith(".m3u8"):
            lines.append(f"/api/xtream/play/{stream_id}.m3u8?u={_encode(absu)}")
        else:
            lines.append(f"/api/xtream/seg/{stream_id}?u={_encode(absu)}")
    return "\n".join(lines) + "\n"

@router.get("/play/{stream_id}.m3u8")
def play(stream_id: str, u: Optional[str] = None):
    """
    إذا u=None: نجلب قائمة m3u8 الأصلية للستريم id من المزود ثم نعيد كتابتها.
    إذا u=.. : نجلب m3u8 الفرعي (جودة/تراك) ونعيد كتابته أيضاً.
    """
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, "XTREAM variables not set.")
    src = _decode(u) if u else build_live_url(stream_id, "m3u8")
    r = _fetch(src)
    text = r.text
    rewritten = _rewrite_m3u8(text, src, stream_id)
    return PlainTextResponse(rewritten, media_type="application/vnd.apple.mpegurl")

@router.get("/seg/{stream_id}")
def seg(stream_id: str, u: str):
    """بروكسي لقطع TS/M4S"""
    try:
        src = _decode(u)
    except Exception:
        raise HTTPException(400, "Bad segment url")
    r = _fetch(src)
    media_type = r.headers.get("Content-Type", "video/mp2t")
    return StreamingResponse(iter([r.content]), media_type=media_type)

# ====== مساعد للبحث بالفرق/الدوري، يستخدمه قسم المباريات ======
def find_stream_id_by_teams(home: str, away: str, league: str = "") -> Optional[str]:
    """
    يحاول مطابقة أسماء الفرق/الدوري داخل أسماء القنوات.
    يعيد stream_id عند العثور.
    """
    try:
        raw = _live_streams_raw()
        needles = [s.lower() for s in [home, away, league] if s]
        for ch in raw:
            name = str(ch.get("name", "")).lower()
            if any(n and n in name for n in needles):
                return str(ch.get("stream_id"))
    except Exception as e:
        print("find_stream_id_by_teams:", e)
    return None
