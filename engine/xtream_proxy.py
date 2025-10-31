from __future__ import annotations
from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse, Response
from typing import Optional, List
import httpx, re
from urllib.parse import urlencode, quote, urljoin

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

def normalize_host(host: str) -> str:
    host = (host or "").strip().replace(" ", "")
    # يُسمح بإدخال host:port فقط – لا تضف http هنا
    return host

def base_urls(host: str) -> List[str]:
    h = normalize_host(host)
    # جرّب HTTP ثم HTTPS
    return [f"http://{h}", f"https://{h}"]

async def get_first_ok(urls: List[str], headers: dict | None = None):
    last_exc = None
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        for u in urls:
            try:
                r = await client.get(u, headers=headers or {})
                r.raise_for_status()
                return r
            except Exception as e:
                last_exc = e
                continue
    raise last_exc or RuntimeError("all attempts failed")

def player_api_urls(host: str, u: str, p: str, action: str, **params) -> List[str]:
    q = {"username": u, "password": p, "action": action}
    q.update(params)
    urls = []
    for b in base_urls(host):
        urls.append(f"{b}/player_api.php?{urlencode(q)}")
    return urls

@router.get("/categories")
async def categories(host: str, u: str, p: str):
    try:
        r = await get_first_ok(player_api_urls(host, u, p, "get_live_categories"))
        return r.json()
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"categories failed: {e}"}, status_code=502)

@router.get("/streams")
async def streams(host: str, u: str, p: str, category_id: str):
    try:
        r = await get_first_ok(player_api_urls(host, u, p, "get_live_streams", category_id=category_id))
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
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        r = await client.get(url, headers=headers)
    ct = r.headers.get("content-type", "application/octet-stream")
    content = r.content
    if "application/vnd.apple.mpegurl" in ct or url.lower().endswith(".m3u8"):
        text = content.decode("utf-8", "ignore")
        def rewrite(line: str) -> str:
            line = line.strip()
            if not line or line.startswith("#"):
                return line
            base = url.rsplit("/", 1)[0] + "/"
            if not re.match(r"^https?://", line, flags=re.I):
                line = urljoin(base, line)
            return "/api/xtream/proxy?url=" + quote(line, safe=":/?&=%")
        new_text = "\n".join(rewrite(l) for l in text.splitlines())
        return Response(new_text, media_type="application/vnd.apple.mpegurl")
    return Response(content, media_type=ct, headers={"Accept-Ranges": "bytes"})

def stream_urls(host: str, u: str, p: str, stream_id: str, ext: str) -> List[str]:
    urls = []
    for b in base_urls(host):
        urls.append(f"{b}/live/{u}/{p}/{stream_id}.{ext}")
    return urls

@router.get("/stream/{stream_id}.m3u8")
async def stream_m3u8(stream_id: str, host: str, u: str, p: str):
    # جرّب http ثم https تلقائيًا
    for up in stream_urls(host, u, p, stream_id, "m3u8"):
        try:
            return await proxy(url=up)  # type: ignore
        except Exception:
            continue
    return JSONResponse({"ok": False, "error": "no reachable m3u8"}, status_code=502)

@router.get("/stream/{stream_id}.ts")
async def stream_ts(stream_id: str, host: str, u: str, p: str, range: Optional[str] = Header(default=None)):
    for up in stream_urls(host, u, p, stream_id, "ts"):
        try:
            return await proxy(url=up, range=range)  # type: ignore
        except Exception:
            continue
    return JSONResponse({"ok": False, "error": "no reachable ts"}, status_code=502)
