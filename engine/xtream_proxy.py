
from __future__ import annotations
from fastapi import APIRouter, Query, Header
from fastapi.responses import JSONResponse, Response
from typing import Optional
import httpx, re
from urllib.parse import urlencode, quote, urljoin

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

def build_player_api(host: str, u: str, p: str, action: str, **params):
    base = f"http://{host}/player_api.php"
    q = {"username": u, "password": p, "action": action}
    q.update(params)
    return f"{base}?{urlencode(q)}"

async def fetch_json(url: str):
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()

@router.get("/categories")
async def categories(host: str, u: str, p: str):
    url = build_player_api(host, u, p, "get_live_categories")
    try:
        data = await fetch_json(url)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=502)
    return data

@router.get("/streams")
async def streams(host: str, u: str, p: str, category_id: str):
    url = build_player_api(host, u, p, "get_live_streams", category_id=category_id)
    try:
        data = await fetch_json(url)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=502)
    for item in data or []:
        item.setdefault("name", item.get("stream_display_name") or item.get("name"))
        item.setdefault("stream_id", item.get("stream_id"))
    return data

@router.get("/proxy")
async def xtream_proxy(url: str = Query(...), range: Optional[str] = Header(default=None)):
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

@router.get("/stream/{stream_id}.m3u8")
async def stream_m3u8(stream_id: str, host: str, u: str, p: str):
    upstream = f"http://{host}/live/{u}/{p}/{stream_id}.m3u8"
    return await xtream_proxy(url=upstream)  # type: ignore

@router.get("/stream/{stream_id}.ts")
async def stream_ts(stream_id: str, host: str, u: str, p: str, range: Optional[str] = Header(default=None)):
    upstream = f"http://{host}/live/{u}/{p}/{stream_id}.ts"
    return await xtream_proxy(url=upstream, range=range)  # type: ignore
