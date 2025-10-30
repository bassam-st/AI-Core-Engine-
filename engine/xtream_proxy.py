# engine/xtream_proxy.py
from __future__ import annotations
import os, re
from typing import Any, Dict, List, Tuple
from urllib.parse import urljoin, quote

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# === إعدادات البيئة ===
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER = os.getenv("XTREAM_USER", "")
XTREAM_PASS = os.getenv("XTREAM_PASS", "")

UA = "Mozilla/5.0 (Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Mobile Safari"
HEADERS = {"User-Agent": UA, "Accept": "*/*", "Connection": "keep-alive"}
TIMEOUT = httpx.Timeout(25.0)

def _assert_env():
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise HTTPException(500, detail="XTREAM env vars missing")

def _ac() -> httpx.AsyncClient:
    # http2=False لتفادي أخطاء h2 على Render
    return httpx.AsyncClient(headers=HEADERS, timeout=TIMEOUT, http2=False, follow_redirects=True)

def build_live_url(stream_id: int | str, file_or_ext: str = "m3u8") -> str:
    """
    أمثلة:
      - build_live_url(22) -> http://host:port/live/u/p/22.m3u8
      - build_live_url(22, "22.m3u8") -> http://.../live/u/p/22.m3u8 (إذا أردت تمرير اسم الملف كاملًا)
    """
    _assert_env()
    if file_or_ext.endswith(".m3u8") or file_or_ext.endswith(".ts"):
        path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{file_or_ext}"
    else:
        path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{file_or_ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

async def _player_api(params: Dict[str, Any]) -> Dict[str, Any] | List[Dict[str, Any]]:
    _assert_env()
    url = f"{XTREAM_BASE}/player_api.php"
    q = {"username": XTREAM_USER, "password": XTREAM_PASS, **params}
    async with _ac() as c:
        r = await c.get(url, params=q)
        if r.status_code == 403:
            # بعض اللوحات تحجب عناوين Render
            raise HTTPException(403, detail="403 from Xtream (IP blocked?)")
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}

async def _fetch_m3u_text() -> str:
    """قراءة ملف M3U (fallback إذا API محجوب أو يرجّع قائمة فاضية)"""
    _assert_env()
    # m3u_plus يحتوي أسماء أوضح
    url = f"{XTREAM_BASE}/get.php?username={XTREAM_USER}&password={XTREAM_PASS}&type=m3u_plus&output=ts"
    async with _ac() as c:
        r = await c.get(url)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, detail="cannot fetch M3U")
        return r.text

def _parse_m3u(text: str) -> List[Dict[str, Any]]:
    """
    نفكّك #EXTINF ثم السطر التالي (URL). نستخرج stream_id من نهاية الرابط.
    أمثلة روابط: .../live/u/p/12345.ts  أو  .../live/u/p/12345.m3u8
    """
    channels: List[Dict[str, Any]] = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for i, ln in enumerate(lines):
        if not ln.startswith("#EXTINF"):
            continue
        # الاسم بعد الفاصلة
        name = ln.split(",", 1)[-1].strip() if "," in ln else "Channel"
        if i + 1 >= len(lines):
            continue
        url = lines[i + 1]
        # استخرج stream_id
        m = re.search(r"/live/[^/]+/[^/]+/(\d+)\.(?:ts|m3u8)", url)
        if not m:
            continue
        sid = int(m.group(1))
        channels.append({"stream_id": sid, "name": name, "category": None, "logo": None})
    return channels

# -------- API --------

@router.get("/info")
async def xtream_info():
    data = await _player_api({})
    return JSONResponse({"ok": True, "info": data})

@router.get("/channels")
async def xtream_channels():
    """
    نجرب player_api -> وإذا فاضي/محجوب، نستخدم M3U fallback.
    """
    channels: List[Dict[str, Any]] = []

    # محاولة عبر API
    try:
        data = await _player_api({"action": "get_live_streams"})
        raw: Any
        if isinstance(data, list):
            raw = data
        else:
            raw = data.get("available_channels") or data.get("streams") or data.get("live") or []
        for ch in raw:
            sid = ch.get("stream_id")
            if not sid:
                continue
            channels.append({
                "stream_id": int(sid),
                "name": ch.get("name") or f"CH {sid}",
                "category": ch.get("category_name") or ch.get("category_id"),
                "logo": ch.get("stream_icon"),
            })
    except HTTPException as e:
        # 403 غالبًا حجب IP -> نتابع لـ M3U fallback
        if e.status_code != 403:
            raise

    # Fallback إلى M3U إذا القائمة فاضية
    if not channels:
        try:
            m3u = await _fetch_m3u_text()
            channels = _parse_m3u(m3u)
        except Exception:
            channels = []

    return {"ok": True, "count": len(channels), "channels": channels}

@router.get("/m3u8/{stream_id}")
async def xtream_m3u8(stream_id: int):
    """
    نعيد الرابط المباشر (للاختبار أو مشغلات خارجية). في الواجهة نستخدم البروكسي أدناه.
    """
    return {"ok": True, "url": build_live_url(stream_id, "m3u8")}

@router.get("/stream/{stream_id}.m3u8")
async def proxy_playlist(stream_id: int):
    """
    بروكسي لقائمة m3u8 مع إعادة كتابة كل المسارات لتعدي Mixed Content
    وأيضًا تمرير المقاطع عبر /api/xtream/pull?u=...
    """
    src = build_live_url(stream_id, "m3u8")
    async with _ac() as c:
        r = await c.get(src)
    if r.status_code >= 400:
        raise HTTPException(r.status_code, detail=f"upstream m3u8 error: {r.text[:200]}")
    text = r.text

    out_lines: List[str] = []
    base_for_rel = src  # لو وجِدت مسارات نسبية
    for ln in text.splitlines():
        t = ln.strip()
        if not t or t.startswith("#"):
            out_lines.append(ln)
            continue
        # مسار مقطع/قائمة فرعية
        if t.startswith("http://") or t.startswith("https://"):
            full = t
        else:
            full = urljoin(base_for_rel, t)
        out_lines.append(f"/api/xtream/pull?u={quote(full, safe='')}")

    out_text = "\n".join(out_lines)
    return Response(content=out_text, media_type="application/vnd.apple.mpegurl")

@router.get("/pull")
async def proxy_pull(u: str):
    """
    يسحب أي ملف (ts/m3u8) من السيرفر الأصلي ويعيده للمشغّل.
    نقيّد أنه يجب أن يبدأ بالرابط الأساسي لزيادة الأمان.
    """
    _assert_env()
    if not u.startswith(XTREAM_BASE):
        raise HTTPException(400, detail="forbidden upstream")
    async with _ac() as c:
        r = await c.get(u)
    if r.status_code >= 400:
        raise HTTPException(r.status_code, detail="upstream pull error")
    # نوع المحتوى كما هو من المصدر (ts أو m3u8)
    mt = r.headers.get("content-type") or "application/octet-stream"
    return Response(content=r.content, media_type=mt)
