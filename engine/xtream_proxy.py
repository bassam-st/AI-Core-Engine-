# engine/xtream_proxy.py
# ——————————————————————————————————————————
# وكيل Xtream مع تصحيح تلقائي (HTTP/2→HTTP/1) + إعادة محاولات
# ويوفّر مسارات API: /api/xtream/info , /api/xtream/channels , /api/xtream/stream
# ——————————————————————————————————————————

from __future__ import annotations
import os
import time
import random
from urllib.parse import urljoin, quote

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# ========= إعدادات البيئة =========
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER = os.getenv("XTREAM_USER", "")
XTREAM_PASS = os.getenv("XTREAM_PASS", "")

# ========= ترويسة ذكية + تبديل تلقائي بروتوكول =========
try:
    import h2  # noqa: F401
    _HTTP2_OK = True
except Exception:
    _HTTP2_OK = False

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0 Safari/537.36"),
    "Accept": "*/*",
    "Connection": "keep-alive",
}

def _make_client(force_http1: bool = False) -> httpx.Client:
    return httpx.Client(
        headers=HEADERS,
        http2=(False if force_http1 else _HTTP2_OK),
        timeout=httpx.Timeout(connect=10, read=25),
        follow_redirects=True,
        verify=False,  # بعض سيرفرات Xtream بدون شهادة سليمة
    )

CLIENT = _make_client()

def _get(url: str, tries: int = 3) -> httpx.Response:
    last = None
    client = CLIENT
    for i in range(1, tries + 1):
        try:
            r = client.get(url)
            # أحياناً 403 مع HTTP/2 — جرّب HTTP/1
            if r.status_code == 403 and client is CLIENT:
                client = _make_client(force_http1=True)
                r = client.get(url)
            r.raise_for_status()
            return r
        except Exception as e:
            last = e
            time.sleep(0.6 * i + random.random() * 0.4)
    raise last

# ========= أدوات =========
def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    """
    يبني رابط بث مباشر:
      http://host:port/live/user/pass/stream_id.m3u8
    لو البيئة ناقصة لا نُسقط التطبيق—نرجع سبب واضح.
    """
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        return f"#missing-env?need=XTREAM_BASE,XTREAM_USER,XTREAM_PASS&id={quote(str(stream_id))}"
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

def _require_env():
    if not XTREAM_BASE or not XTREAM_USER or not XTREAM_PASS:
        raise HTTPException(
            status_code=200,
            detail="Xtream غير مفعّل: املأ XTREAM_BASE / XTREAM_USER / XTREAM_PASS في Render."
        )

# ========= مسارات API =========
router = APIRouter(prefix="/api/xtream", tags=["xtream"])

@router.get("/info")
def xtream_info():
    _require_env()
    url = f"{XTREAM_BASE}/player_api.php?username={XTREAM_USER}&password={XTREAM_PASS}"
    r = _get(url, tries=2)
    data = r.json()
    # نُعيد ملخصاً مفيداً ولا نُسقط أي شيء
    return JSONResponse({
        "ok": True,
        "user": data.get("user_info", {}),
        "server": data.get("server_info", {}),
        "base": XTREAM_BASE
    })

@router.get("/channels")
def xtream_channels(q: str | None = None, category_id: str | None = None):
    """
    يرجع قائمة القنوات (stream_id, name, category, logo).
    - q: نص بحث اختياري
    - category_id: تصنيف اختياري
    """
    _require_env()
    url = (f"{XTREAM_BASE}/player_api.php?username={XTREAM_USER}"
           f"&password={XTREAM_PASS}&action=get_live_streams")
    r = _get(url, tries=2)
    raw = r.json()
    items = []
    for ch in raw if isinstance(raw, list) else []:
        it = {
            "id": ch.get("stream_id"),
            "name": ch.get("name"),
            "category_id": ch.get("category_id"),
            "logo": ch.get("stream_icon"),
            "m3u8": build_live_url(ch.get("stream_id")),
        }
        items.append(it)

    # فلاتر بسيطة
    if category_id:
        items = [x for x in items if str(x.get("category_id")) == str(category_id)]
    if q:
        ql = q.strip().lower()
        items = [x for x in items if ql in str(x.get("name", "")).lower()]

    return {"ok": True, "count": len(items), "items": items}

@router.get("/stream")
def xtream_stream(stream_id: str):
    """
    لا نُمرّر الفيديو عبر الخادم (توفيراً للموارد). فقط نبني رابطاً صالحاً.
    """
    url = build_live_url(stream_id)
    if url.startswith("#missing-env"):
        raise HTTPException(status_code=200, detail=url)
    return {"ok": True, "url": url}
