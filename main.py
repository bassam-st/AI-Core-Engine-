# main.py
from __future__ import annotations
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from pathlib import Path

# استيراد الوحدات الداخلية للنواة
from engine.config import cfg
from engine.retriever import Retriever
from engine.summarizer import Summarizer
from engine.generator import AnswerSynthesizer
from engine.intent import IntentModel
from engine.sentiment import SentimentAnalyzer
from engine.memory import ConversationMemory, init_db
from engine.ingest import ingest_file
from engine.xtream_proxy import router as xtream_router  # ✅ دمج بروكسي القنوات Xtream

# إعداد البيئة والمسارات
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="نواة بسّام الذكية – Bassam Core Engine", version="3.1")

# تفعيل القوالب والملفات الثابتة
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# إعداد CORS لتشغيل الواجهة من أي مكان
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تهيئة قاعدة الذاكرة
init_db()

# كائنات التشغيل للنواة
retriever = Retriever()
summarizer = Summarizer()
generator = AnswerSynthesizer()
intent_model = IntentModel()
sentiment_analyzer = SentimentAnalyzer()
memory = ConversationMemory()

# 🧩 تضمين راوتر Xtream
app.include_router(xtream_router)

# -------------------------------------------------------------------
# 🧠 الواجهة الرئيسية للنواة
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ui", response_class=HTMLResponse)
async def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------------------------------------------------
# 📺 واجهة عرض القنوات Xtream
@app.get("/ui/xtream", response_class=HTMLResponse)
async def ui_xtream(request: Request):
    return templates.TemplateResponse("xtream.html", {"request": request})

# -------------------------------------------------------------------
# ⚡ فحص الصحة
@app.get("/health")
async def health():
    return {"status": "ok", "version": "3.1"}

# -------------------------------------------------------------------
# 🧾 تحميل ملفات معرفية داخل النظام
@app.post("/api/ingest")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    path = BASE_DIR / "data" / file.filename
    with open(path, "wb") as f:
        f.write(contents)
    await ingest_file(path)
    return {"ok": True, "filename": file.filename}

# -------------------------------------------------------------------
# 🧩 إدخال سؤال ذكي والحصول على إجابة
class Question(BaseModel):
    text: str

@app.post("/api/ask")
async def ask(q: Question):
    text = q.text.strip()
    if not text:
        return {"error": "النص فارغ"}

    # تحليل النية والمشاعر
    intent = intent_model.predict(text)
    sentiment = sentiment_analyzer.analyze(text)
    retrieved = retriever.retrieve(text)

    # التلخيص والرد النهائي
    summary = summarizer.summarize(retrieved)
    answer = generator.generate(text, summary, intent=intent, sentiment=sentiment)

    # حفظ الذاكرة
    memory.save_turn(user=text, bot=answer)

    return {
        "user_input": text,
        "intent": intent,
        "sentiment": sentiment,
        "retrieved": retrieved,
        "summary": summary,
        "answer": answer,
    }

# -------------------------------------------------------------------
# 💬 ذاكرة المحادثة
@app.get("/api/memory")
async def get_memory():
    return {"history": memory.history()}

@app.get("/api/memory/clear")
async def clear_memory():
    memory.clear()
    return {"ok": True}

# -------------------------------------------------------------------
# 🧠 صفحة وثائق Swagger
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return templates.TemplateResponse("swagger.html", {"request": {}})

# -------------------------------------------------------------------
# 🚀 تشغيل السيرفر
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
