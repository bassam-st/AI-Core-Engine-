# main.py — نواة بسّام الذكية: واجهة + دردشة + فريق إنشاء المشاريع
from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.brain import chat_answer
from core.memory import init_db, add_fact
from core.code_team import build_project  # ✅ الصحيح: code_team

app = FastAPI(title="AI Core Engine — Bassam", version="1.2.0")

# مجلد static (اختياري) + قوالب HTML
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# تهيئة قاعدة البيانات
init_db()

# الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# دردشة الذكاء
@app.post("/api/chat")
async def api_chat(request: Request):
    try:
        data = await request.json()
        msg = (data.get("message") or "").strip()
        if not msg:
            return {"ok": False, "error": "empty_message"}
        reply, sources = chat_answer(msg)
        return {"ok": True, "reply": reply, "sources": sources}
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={"ok": False, "error": "internal_error", "detail": str(e)[:300]},
        )

# حفظ معلومة يدويًا (اختياري)
@app.post("/api/learn")
async def api_learn(request: Request):
    try:
        data = await request.json()
        txt = (data.get("text") or "").strip()
        src = (data.get("source") or "manual").strip()
        if not txt:
            return {"ok": False, "error": "empty_text"}
        add_fact(txt, source=src)
        return {"ok": True, "added": 1}
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={"ok": False, "error": "internal_error", "detail": str(e)[:300]},
        )

# فريق الإنشاء: يخطّط/يبحث/ينتج ملفات
@app.post("/api/team/build")
async def api_team_build(request: Request):
    try:
        data = await request.json()
        goal = (data.get("goal") or "").strip()
        # urls = data.get("urls") or []  # متروك للنسخات المستقبلية إن أردت تمرير مصادر
        if not goal:
            return {"ok": False, "error": "empty_goal"}
        result = build_project(goal)  # ✅ دالة الفريق تستقبل وصف الهدف فقط
        return result
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={"ok": False, "error": "internal_error", "detail": str(e)[:300]},
        )

# اختبار
@app.get("/ping")
def ping():
    return {"status": "alive", "message": "نظام النواة يعمل ✅"}

# تشغيل محلي
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
