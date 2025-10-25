# main.py — النواة الذكية (FastAPI) مع تعلّم من الرسالة مباشرة
from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.brain import chat_answer
from core.memory import init_db, add_fact
from core.learn_loop import run_once as autolearn_run_once

app = FastAPI(title="AI Core Engine", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def api_chat(request: Request):
    try:
        data = await request.json()
        msg = (data.get("message") or "").strip()
        if not msg:
            return {"ok": False, "error": "empty_message"}

        # أوامر سريعة داخل الرسالة (تعلم يدوي/ذاتي)
        norm = msg.replace("أ","ا").replace("إ","ا").replace("آ","ا")
        if norm.startswith("اضف") or norm.startswith("اضيف") or "اضف هذه المعلومه" in norm:
            # مثال: "أضف هذه المعلومة: بسام الشيمي هو صاحب التطبيق"
            text = msg.split(":", 1)[1].strip() if ":" in msg else msg[3:].strip()
            if text:
                add_fact(text, source="manual")
                return {"ok": True, "reply": "تم حفظ المعلومة في الذاكرة ✅", "sources": []}

        if "تعلمي" in norm or "تعلمي" in norm or "تعلمى" in norm or "تشغيل التعل" in norm:
            added = autolearn_run_once()
            return {"ok": True, "reply": f"تم التعلّم الذاتي. أُضيفت {added} جملة معرفة.", "sources": []}

        reply, sources = chat_answer(msg)
        return {"ok": True, "reply": reply, "sources": sources}

    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": "internal_error", "detail": str(e)[:300]})

@app.get("/ping")
def ping():
    return {"status": "alive", "message": "نظام النواة يعمل ✅"}
