# engine/xtream_proxy.py
from fastapi import APIRouter, Query, HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse
import os, httpx, asyncio

router = APIRouter(prefix="/api/xtream", tags=["xtream"])

def get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()

def resolve_params(
    host: str | None, u: str | None, p: str | None
) -> tuple[str, str, str]:
    host = (host or get_env("XTREAM_HOST")).strip()
    u    = (u    or get_env("XTREAM_U")).strip()
    p    = (p    or get_env("XTREAM_P")).strip()
    if not (host and u and p):
        raise HTTPException(status_code=400, detail="XTREAM credentials missing")
    return host, u, p

def proxy_base() -> str:
    base = get_env("BASE_PROXY", "")
    if not base:
        raise HTTPException(status_code=500, detail="BASE_PROXY not set")
    return base.rstrip("/")

@router.get("/ping")
def ping():
    return {
        "ok": True,
        "base_proxy": get_env("BASE_PROXY"),
        "host": get_env("XTREAM_HOST"),
        "u_set": bool(get_env("XTREAM_U")),
        "p_set": bool(get_env("XTREAM_P")),
    }

@router.get("/categories")
async def get_categories(
    host: str | None = None, u: str | None = None, p: str | None = None
):
    host, u, p = resolve_params(host, u, p)
    qs = f"host={host}&u={u}&p={p}&endpoint=player_api.php&action=get_live_categories"
    url = f"{proxy_base()}/xtream?{qs}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        return JSONResponse(r.json())

@router.get("/streams")
async def get_streams(
    category_id: str,
    host: str | None = None, u: str | None = None, p: str | None = None
):
    host, u, p = resolve_params(host, u, p)
    qs = (
        f"host={host}&u={u}&p={p}"
        f"&endpoint=player_api.php&action=get_live_streams&category_id={category_id}"
    )
    url = f"{proxy_base()}/xtream?{qs}"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url)
        r.raise_for_status()
        return JSONResponse(r.json())

@router.get("/stream/{stream_id}.m3u8")
async def hls_m3u8(
    stream_id: str,
    host: str | None = None, u: str | None = None, p: str | None = None
):
    host, u, p = resolve_params(host, u, p)
    qs = f"host={host}&u={u}&p={p}&stream={stream_id}&type=m3u8"
    url = f"{proxy_base()}/xplay?{qs}"

    async def gen():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url) as r:
                r.raise_for_status()
                async for chunk in r.aiter_bytes():
                    yield chunk

    return StreamingResponse(gen(), media_type="application/vnd.apple.mpegURL")

# اختياري: تحويل MPEG-TS (بعض القنوات لا تملك HLS)
@router.get("/stream/{stream_id}.ts")
async def ts_mpeg(
    stream_id: str,
    host: str | None = None, u: str | None = None, p: str | None = None
):
    host, u, p = resolve_params(host, u, p)
    qs = f"host={host}&u={u}&p={p}&stream={stream_id}&type=ts"
    url = f"{proxy_base()}/xplay?{qs}"

    async def gen():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url) as r:
                r.raise_for_status()
                async for chunk in r.aiter_bytes():
                    yield chunk

    return StreamingResponse(gen(), media_type="video/MP2T")
