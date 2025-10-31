from __future__ import annotations
from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse, Response
from typing import Optional, List
import httpx, os, re
from urllib.parse import urlencode, quote, urljoin

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

# ضع هنا رابط الworker بعد إنشائه (أو أضفه كمتغير بيئة RELAY_BASE)
RELAY_BASE = os.getenv("RELAY_BASE", "").rstrip("/")  # مثال: https://your-relay.workers.dev

COMMON_HEADERS = {
    # UA طبيعي لتفادي الحظر
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

def base_urls(host: str) -> List[str]:
    h = (host or "").strip().replace(" ", "")
    return [f"http://{h}", f"https://{h}"]  # نجرب HTTP ثم HTTPS

def wrap_relay(url: str) -> str:
    return f"{RELAY_BASE}?url={quote(url, safe=':/?&=%')}" if RELAY_BASE else url

async def fetch_first_ok(urls: List[str], headers: dict | None = None, via_relay_also: bool = True):
    """
    يحاول مباشرة، ثم عبر Relay إذا فشل أو كان محجوبًا.
    يعيد Response حتى لو لم تكن 200 (لنعاين النص عند الخطأ).
    """
    H = {**COMMON_HEADERS, **(headers or {})}
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        # مباشر
        for u in urls:
            try:
                r = await client.get(u, headers=H)
                if r.status_code == 200:
                    return r
                last = r
            except Exception:
                last = None
                continue
        # عبر relay
        if via_relay_also and RELAY_BASE:
            for u in urls:
                try:
                    r = await client.get(wrap_relay(u), headers=H)
                    if r.status_code == 200:
                        return r
                    last = r
                except Exception:
                    last = None
                    continue
    raise RuntimeError("all attempts failed (direct + relay)")

def player_api_urls(host: str, u: str, p: str, action: str, **params) -> List[str]:
    q = {"username": u, "password": p, "action": action}
    q.update(params)
    return [f"{b}/player_api.php?{urlencode(q)}" for b in base_urls(host)]

@router.get("/categories")
async def categories(host: str, u: str, p: str):
    try:
        r = await fetch_first_ok(player_api_urls(host, u, p, "get_live_categories"))
        if r.status_code != 200:
            return JSONResponse({"ok": False, "status": r.status_code, "text": r.text[:400]}, status_code=502)
        return r.json()
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"categories failed: {e}"}, status_code=502)

@router.get("/streams")
async def streams(host: str, u: str, p: str, category_id: str):
    try:
        r = await fetch_first_ok(player_api_urls(host, u, p, "get_live_streams", category_id=category_id))
        if r.status_code != 200:
            return JSONResponse({"ok": False, "status": r.status_code, "text": r.text[:400]}, status_code=502)
        data = r.json()
        for item in data or []:
            item.setdefault("name", item.get("stream_display_name") or item.get("name"))
            item.setdefault("stream_id", item.get("stream_id"))
        return data
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"streams failed: {e}"}, status_code=502)

@router.get("/proxy")
async def proxy(url: str = Query(...), range: Optional[str] = Header(default=None)):
    headers = {}
    if range:
        headers["Range"] = range

    # جرّب مباشر ثم Relay
    urls = [url]
    if RELAY_BASE:
        urls.append(wrap_relay(url))

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        for u in urls:
            try:
                r = await client.get(u, headers={**COMMON_HEADERS, **headers})
                if r.status_code != 200:
                    continue
                ct = r.headers.get("content-type", "application/octet-stream")
                content = r.content

                # m3u8: أعد كتابة الروابط الفرعية لتمر عبر نفس /proxy
                if "application/vnd.apple.mpegurl" in ct or url.lower().endswith(".m3u8"):
                    text = content.decode("utf-8", "ignore")

                    def rewrite(line: str) -> str:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            return line
                        base = url.rsplit("/", 1)[0] + "/"
                        if not re.match(r"^https?://", line, flags=re.I):
                            line = urljoin(base, line)
                        prox = f"/api/xtream/proxy?url={quote(line, safe=':/?&=%')}"
                        return prox

                    new_text = "\n".join(rewrite(l) for l in text.splitlines())
                    return Response(new_text, media_type="application/vnd.apple.mpegurl")

                # ملفات TS و MP4 إلخ
                return Response(content, media_type=ct, headers={"Accept-Ranges": "bytes"})
            except Exception:
                continue

    return JSONResponse({"ok": False, "error": "proxy failed (direct + relay)"}, status_code=502)

def stream_urls(host: str, u: str, p: str, stream_id: str, ext: str) -> List[str]:
    return [f"{b}/live/{u}/{p}/{stream_id}.{ext}" for b in base_urls(host)]

@router.get("/stream/{stream_id}.m3u8")
async def stream_m3u8(stream_id: str, host: str, u: str, p: str):
    for up in stream_urls(host, u, p, stream_id, "m3u8"):
        resp = await proxy(url=up)  # type: ignore
        if not isinstance(resp, JSONResponse):
            return resp
    return JSONResponse({"ok": False, "error": "no reachable m3u8"}, status_code=502)

@router.get("/stream/{stream_id}.ts")
async def stream_ts(stream_id: str, host: str, u: str, p: str, range: Optional[str] = Header(default=None)):
    for up in stream_urls(host, u, p, stream_id, "ts"):
        resp = await proxy(url=up, range=range)  # type: ignore
        if not isinstance(resp, JSONResponse):
            return resp
    return JSONResponse({"ok": False, "error": "no reachable ts"}, status_code=502)
