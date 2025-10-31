from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()

@app.get("/xplay")
async def xplay(
    host: str = Query(...),
    u: str = Query(...),
    p: str = Query(...),
    stream: str = Query(...),
    type: str = Query("m3u8")
):
    # 🔹 توليد رابط القناة الأصلي من Xtream
    ext = "m3u8" if not type else type
    full_url = f"http://{host}/live/{u}/{p}/{stream}.{ext}"

    async def proxy_stream():
        async with httpx.AsyncClient(follow_redirects=True, timeout=None) as client:
            async with client.stream("GET", full_url) as resp:
                if resp.status_code != 200:
                    raise HTTPException(status_code=resp.status_code, detail=f"Stream fetch error from {full_url}")
                async for chunk in resp.aiter_bytes():
                    yield chunk

    # 🔹 نعيده كـ HLS stream
    return StreamingResponse(proxy_stream(), media_type="application/vnd.apple.mpegurl")
