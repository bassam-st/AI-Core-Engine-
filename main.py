# main.py
from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# نواة مشروعك (ابقها كما هي إن وُجدت)
from engine.xtream_proxy import router as xtream_router

APP_TITLE = "النواة الذكية الاحترافية – Bassam"
app = FastAPI(title=APP_TITLE)

# ملفات ثابتة (اختياري إن عندك exports أو static)
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(f"""
<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{APP_TITLE}</title>
<body style="font-family:system-ui;direction:rtl;text-align:center;padding:24px">
  <h2>🧠 {APP_TITLE}</h2>
  <p>بحث وتوليد… مع شاشة قنوات Xtream مدمجة.</p>
  <p>
    <a href="/ui/xtream">📺 شاشة Xtream</a> |
    <a href="/docs">Swagger</a>
  </p>
</body>
""")

# صفحة واجهة Xtream – نقرأ ملف الجذر إن وُجد، وإلا نعطي نسخة مضمنة
@app.get("/ui/xtream", response_class=HTMLResponse)
def ui_xtream():
    fp = Path("xtream-screen.html")
    if fp.exists():
        return HTMLResponse(fp.read_text(encoding="utf-8"))
    # نسخة احتياطية قصيرة
    return HTMLResponse("""
<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>قنوات Xtream</title>
<body style="font-family:system-ui;direction:rtl;padding:20px;background:#0f172a;color:#e2e8f0">
  <h3>قنوات Xtream</h3>
  <p>الملف xtream-screen.html غير موجود في الجذر؛ أضفه لواجهة كاملة.</p>
</body>""")

# ربط راوتر Xtream
app.include_router(xtream_router)
