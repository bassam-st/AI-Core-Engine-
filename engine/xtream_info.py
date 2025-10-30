# engine/xtream_info.py
from __future__ import annotations
import os, json, time, hmac, hashlib, base64
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse

# === إعدادات ومسارات التخزين ===
DATA_DIR = os.getenv("DATA_DIR", "data")
STORE_FILE = Path(DATA_DIR) / "xtream_store.json"
STORE_FILE.parent.mkdir(parents=True, exist_ok=True)

XTREAM_SECRET = os.getenv("XTREAM_SECRET") or os.getenv("SECRET_KEY")
if not XTREAM_SECRET:
    raise RuntimeError("XTREAM_SECRET not set in env (.env or Render env vars).")

def _load_store() -> Dict[str, Any]:
    if STORE_FILE.exists():
        try:
            return json.loads(STORE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save_store(data: Dict[str, Any]) -> None:
    STORE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# === مساعدة: توقيع/تحقق توكين وقتي لعدم كشف البيانات ===
def _sign(payload: str, exp_sec: int = 300) -> str:
    exp = int(time.time()) + exp_sec
    msg = f"{payload}:{exp}".encode()
    sig = hmac.new(XTREAM_SECRET.encode(), msg, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(sig + b"." + str(exp).encode()).decode()
    return token

def _verify(payload: str, token: str) -> bool:
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        sig, exp = raw.split(b".", 1)
        if int(exp) < int(time.time()):
            return False
        msg = f"{payload}:{int(exp)}".encode()
        good = hmac.new(XTREAM_SECRET.encode(), msg, hashlib.sha256).digest()
        return hmac.compare_digest(sig, good)
    except Exception:
        return False

# === بناء روابط Xtream ===
def _api_url(server: str, username: str, password: str, q: str) -> str:
    server = server.rstrip("/")
    return f"{server}/player_api.php?username={username}&password={password}&{q}"

def _m3u8_url(server: str, username: str, password: str, stream_id: str) -> str:
    server = server.rstrip("/")
    return f"{server}/live/{username}/{password}/{stream_id}.m3u8"

# === راوتر FastAPI ===
xtream_router = APIRouter()

@xtream_router.post("/config")
async def set_config(body: Dict[str, str]):
    """
    body = { "server": "http://host:port", "username": "...", "password": "..." }
    """
    for k in ("server", "username", "password"):
        if not body.get(k):
            raise HTTPException(400, f"missing field: {k}")
    store = _load_store()
    store.update({
        "server": body["server"].strip(),
        "username": body["username"].strip(),
        "password": body["password"].strip()
    })
    _save_store(store)
    return {"ok": True, "saved": ["server", "username", "password"]}

@xtream_router.get("/status")
async def status():
    st = _load_store()
    if not all(st.get(k) for k in ("server","username","password")):
        return {"ok": False, "configured": False}
    url = _api_url(st["server"], st["username"], st["password"], "action=user_info")
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(502, "xtream status error")
        data = r.json()
    # معلومات مختصرة مفيدة
    info = data.get("user_info", {})
    server_info = data.get("server_info", {})
    return {
        "ok": True, "configured": True,
        "user_info": {
            "status": info.get("status"),
            "active_cons": info.get("active_cons"),
            "max_connections": info.get("max_connections"),
            "exp_date": info.get("exp_date"),
        },
        "server": {
            "url": st["server"],
            "url_time": server_info.get("url_time"),
        }
    }

@xtream_router.get("/live/categories")
async def live_categories():
    st = _load_store()
    if not all(st.get(k) for k in ("server","username","password")):
        raise HTTPException(400, "xtream not configured")
    url = _api_url(st["server"], st["username"], st["password"], "action=get_live_categories")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        cats = r.json() or []
    # ترتيب مبسّط
    cats = sorted(cats, key=lambda c: (c.get("category_name") or "").lower())
    return {"ok": True, "count": len(cats), "categories": cats}

@xtream_router.get("/live/streams")
async def live_streams(category_id: Optional[str] = None, search: Optional[str] = None):
    st = _load_store()
    if not all(st.get(k) for k in ("server","username","password")):
        raise HTTPException(400, "xtream not configured")
    q = "action=get_live_streams"
    if category_id:
        q += f"&category_id={category_id}"
    url = _api_url(st["server"], st["username"], st["password"], q)
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url)
        r.raise_for_status()
        items = r.json() or []
    # تصفية/بحث اختياري
    if search:
        s = search.strip().lower()
        items = [x for x in items if s in (x.get("name","").lower())]
    # إضافة رابط تشغيل محمي بتوكين
    for x in items:
        sid = str(x.get("stream_id"))
        token = _sign(sid, exp_sec=300)
        x["play_url"] = f"/xtream/hls/{sid}.m3u8?token={token}"
    return {"ok": True, "count": len(items), "streams": items}

@xtream_router.get("/hls/{stream_id}.m3u8")
async def proxy_hls(stream_id: str, token: str):
    """
    يمرر ملف الـ m3u8 عبر الخادم مع توكين مؤقت حتى لا تظهر بيانات الاشتراك.
    """
    if not _verify(stream_id, token):
        raise HTTPException(401, "invalid or expired token")
    st = _load_store()
    if not all(st.get(k) for k in ("server","username","password")):
        raise HTTPException(400, "xtream not configured")
    src = _m3u8_url(st["server"], st["username"], st["password"], stream_id)
    async with httpx.AsyncClient(timeout=60, headers={"User-Agent":"Mozilla/5.0"}) as client:
        r = await client.get(src)
        r.raise_for_status()
        content = r.content
    # لا نعيد كتابة المسارات الداخلية هنا؛ أغلب السيرفرات تعطي روابط مطلقة.
    return Response(content, media_type="application/vnd.apple.mpegurl")

@xtream_router.get("/segment")
async def proxy_segment(url: str):
    """
    ممرّ عام لتجزئات TS/TSV أو m4s إذا احتجنا (اختياري).
    استدعِه عند الحاجة بفك تشفير الروابط داخل m3u8 إن كانت نسبية.
    """
    async with httpx.AsyncClient(timeout=60, headers={"User-Agent":"Mozilla/5.0"}) as client:
        async with client.stream("GET", url) as r:
            r.raise_for_status()
            return StreamingResponse(r.aiter_bytes(), media_type=r.headers.get("Content-Type","video/mp2t"))

@xtream_router.delete("/config")
async def clear_config():
    _save_store({})
    return {"ok": True, "cleared": True}
