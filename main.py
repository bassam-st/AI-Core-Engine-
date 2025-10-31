# main.py
from __future__ import annotations
import os
from pathlib import Path
from urllib.parse import quote, urlparse

import httpx
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
    Response,
    FileResponse,
    StreamingResponse,
)
from starlette.staticfiles import StaticFiles

APP_DIR = Path(__file__).parent.resolve()
STATIC_DIR = APP_DIR / "static"

app = FastAPI(title="AI Core Engine")

# ----------------------[ CORS ]----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# ----------------------[ STATIC ]--------------------
# /static -> مجلد static (اختياري إن كنت تستخدم css/js)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ----------------------[ HEALTH ]--------------------
@app.get("/healthz")
async def healthz():
    return {"ok": True}

# ----------------------[ UI /xtream ]----------------
# يدعم وجود xtream-screen.html في static/ أو في جذر المشروع
@app.get("/ui/xtream", response_class=HTMLResponse)
async def ui_xtream():
    # تفضيل الموجود داخل static/
    cand = STATIC_DIR / "xtream-screen.html"
    if cand.exists():
        return FileResponse(str(cand), media_type="text/html; charset=utf-8")
    root_one = APP_DIR / "xtream-screen.html"
    if root_one.exists():
        return FileResponse(str(root_one), media_type="text/html; charset=utf-8")
    # صفحة بسيطة في حال لم يجد الملف
    html = """<!doctype html><meta charset="utf-8">
    <title>Xtream UI</title><h2>لم يتم العثور على xtream-screen.html</h2>
    ضع الملف داخل <code>static/xtream-screen.html</code> أو بجانب <code>main.py</code>.
    """
    return HTMLResponse(html)

@app.get("/", include_in_schema=False)
async def root():
    # توجيه للـ UI
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/ui/xtream">')

# ====================================================
#           تشغيل القنوات عبر خادمك (Proxy)
# ====================================================
# الفكرة:
# 1) /xplay يرجّع لك ملف m3u8 بعد "إعادة الكتابة" لكل سطر غير تعليقي
#    بحيث يصبح رابط القطعة عبر خادمك /xproxy?url=...
# 2) /xproxy يقوم بتمرير أي رابط (m3u8/ts) مع ترويسات صحيحة
#    وبدون CORS مشاكل.

# -------- Helper: عميل HTTP مشترك --------
def _client() -> httpx.AsyncClient:
    # follow_redirects مهم لأن بعض السيرفرات تعيد توجيه
    return httpx.AsyncClient(follow_redirects=True, timeout=None)

# -------- /xplay : يرجع m3u8 مُعاد كتابته --------
@app.get("/xplay")
async def xplay(
    host: str = Query(..., description="host:port مثل mhiptv.info:2095"),
    u: str = Query(..., description="اسم المستخدم"),
    p: str = Query(..., description="كلمة المرور"),
    stream: str = Query(..., description="رقم القناة/stream_id"),
    type: str = Query("m3u8", description="m3u8 أو m3u8_index ..."),
):
    # عنوان قائمة التشغيل الأصلية
    ext = type or "m3u8"
    upstream_m3u8 = f"http://{host}/live/{u}/{p}/{stream}.{ext}"

    async with _client() as client:
        r = await client.get(upstream_m3u8)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=f"Cannot fetch playlist: {upstream_m3u8}")

        text = r.text or ""
        # مسار الأساس للقطع إن كانت نسبيّة
        base = f"http://{host}/live/{u}/{p}/{stream}/"

        rewritten_lines = []
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                rewritten_lines.append(line)
                continue

            # إن كان الرابط مطلقًا نلفّه كما هو، وإلا نُكوّن رابطًا كاملاً عبر base
            if s.startswith("http://") or s.startswith("https://"):
                target = s
            else:
                target = base + s

            proxied = f"/xproxy?url={quote(target, safe='')}"
            rewritten_lines.append(proxied)

        rewritten = "\n".join(rewritten_lines) + "\n"

    # مهم: Content-Type المناسب للـ HLS
    return Response(
        content=rewritten,
        media_type="application/vnd.apple.mpegurl; charset=utf-8",
        headers={
            # السماح بالتخزين المؤقت البسيط يحسن السلاسة أحيانًا
            "Cache-Control": "no-cache"
        },
    )

# -------- /xproxy : يمرر m3u8/ts/… كما هو --------
@app.get("/xproxy")
async def xproxy(url: str = Query(..., description="الرابط المطلق للملف (m3u8 أو ts)")):
    # أمان بسيط: يسمح فقط بـ http/https
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Only http/https are allowed")

    async def streamer():
        async with _client() as client:
            async with client.stream("GET", url) as resp:
                if resp.status_code != 200:
                    raise HTTPException(status_code=resp.status_code, detail=f"Upstream error for {url}")
                async for chunk in resp.aiter_bytes():
                    yield chunk

    # تحديد نوع المحتوى حسب الامتداد أو ترويسة المصدر
    guessed = "application/octet-stream"
    path = parsed.path.lower()
    if path.endswith(".m3u8"):
        guessed = "application/vnd.apple.mpegurl"
    elif path.endswith(".ts"):
        guessed = "video/mp2t"

    return StreamingResponse(streamer(), media_type=guessed, headers={"Cache-Control": "no-cache"})
