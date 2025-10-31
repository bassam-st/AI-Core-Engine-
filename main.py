# main.py — AI-Core-Engine (Xtream Inside App)
from __future__ import annotations
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx

APP_TITLE = "النواة الذكية الاحترافية – Bassam"
app = FastAPI(title=APP_TITLE)

# ====== STATIC ======
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ====== CORS ======
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== Home ======
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html lang="ar" dir="rtl"><head>
      <meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
      <title>{APP_TITLE}</title>
      <style>body{{font-family:system-ui,Segoe UI,Arial;margin:40px;background:#0f172a;color:#e2e8f0}}
      a{{color:#93c5fd;text-decoration:none}}</style>
    </head><body>
      <h2>🧠 {APP_TITLE}</h2>
      <p>تشغيل Xtream من داخل التطبيق.</p>
      <p><a href="/ui/xtream">📺 فتح شاشة Xtream</a></p>
    </body></html>
    """

# ====== UI: Xtream Screen ======
@app.get("/ui/xtream")
def ui_xtream():
    file_path = STATIC_DIR / "xtream-screen.html"
    return FileResponse(file_path)

# ====== Proxy: /xplay  (يشغّل القناة داخليًا) ======
@app.get("/xplay")
async def xplay(request: Request):
    """
    استعمال:
      /xplay?host=HOST:PORT&u=USER&p=PASS&stream=STREAM_ID&type=m3u8
    - يعيد ملف m3u8 بعد تعديل الروابط بداخله لتكون مطلقة (Absolute)
      كي يستطيع المشغل تحميل الشرائح (ts) مباشرة من مصدر Xtream.
    """
    host = request.query_params.get("host")
    u = request.query_params.get("u")
    p = request.query_params.get("p")
    stream_id = request.query_params.get("stream")
    ext = request.query_params.get("type", "m3u8")

    if not host or not u or not p or not stream_id:
        return Response(
            content='{"ok":false,"message":"حقول مطلوبة: host, u, p, stream (ويمكن type=m3u8)"}',
            media_type="application/json",
            status_code=400,
        )

    # رابط الـ m3u8 الأصلي من Xtream
    src = f"http://{host}/live/{u}/{p}/{stream_id}.{ext}"

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(src)
            if r.status_code != 200:
                return Response(
                    content=f'#EXTM3U\n# Error {r.status_code} fetching source',
                    media_type="application/vnd.apple.mpegurl",
                    status_code=200,
                )

            text = r.text

            # نعيد كتابة أي سطر ليس تعليقًا (#) وليس رابط http ليصبح مطلقًا
            # بعض السيرفرات تُرجع خطوطًا نسبيّة لأجزاء .ts
            base_ts = f"http://{host}/live/{u}/{p}/"
            fixed_lines = []
            for line in text.splitlines():
                ln = line.strip()
                if not ln or ln.startswith("#") or ln.startswith("http://") or ln.startswith("https://"):
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(base_ts + ln)
            fixed = "\n".join(fixed_lines)

            return Response(
                content=fixed.encode("utf-8"),
                media_type="application/vnd.apple.mpegurl",
                status_code=200,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                },
            )
    except Exception as e:
        return Response(
            content=f'#EXTM3U\n# Proxy error: {e}',
            media_type="application/vnd.apple.mpegurl",
            status_code=200,
        )

# ====== Health ======
@app.get("/ping")
def ping():
    return {"ok": True, "service": "xtream-inside", "version": 1}
