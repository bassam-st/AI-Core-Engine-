# main.py — النواة الذكية المتكاملة (واجهة + API + ذاكرة + بحث)
from __future__ import annotations
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.brain import chat_answer
from core.memory import init_db

# ========= التهيئة =========
app = FastAPI(title="AI Core Engine", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ========= قاعدة البيانات =========
init_db()

# ========= الصفحة الرئيسية =========
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ========= API: محادثة =========
@app.post("/api/chat")
async def api_chat(request: Request):
    try:
        data = await request.json()
        q = data.get("message", "").strip()
        if not q:
            return {"ok": False, "error": "empty_message"}

        reply, sources = chat_answer(q)
        return {"ok": True, "reply": reply, "sources": sources}

    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={"ok": False, "error": "internal_error", "detail": str(e)[:300]},
        )

# ========= API: اختبار سريع =========
@app.get("/ping")
def ping():
    return {"status": "alive", "message": "نظام النواة يعمل ✅"}

# ========= تشغيل محلي =========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
