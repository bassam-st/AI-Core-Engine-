from __future__ import annotations
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import List
import os

from engine.config import cfg
from engine.retriever import Retriever
from engine.summarizer import Summarizer
from engine.generator import AnswerSynthesizer
from engine.intent import IntentModel
from engine.sentiment import SentimentAnalyzer
from engine.memory import ConversationMemory, init_db
from engine.ingest import Ingestor
from engine.trainer import AutoTrainer
from engine.web import web_search, wiki_summary_ar

APP_TITLE = "النواة الذكية الاحترافية - Bassam"
app = FastAPI(title=APP_TITLE)

# تحضير المسارات
os.makedirs(cfg.DATA_DIR, exist_ok=True)

# مكوّنات أساسية
retriever = Retriever()
summarizer = Summarizer()
generator = AnswerSynthesizer()
intent_model = IntentModel()
sentiment = SentimentAnalyzer()
memory = ConversationMemory()
ingestor = Ingestor()
auto_trainer = AutoTrainer(intent_model, memory)

# Startup: قاعدة البيانات + تنزيل موارد لازمة إن لم توجد
@app.on_event("startup")
def _startup():
    try:
        init_db()
    except Exception as e:
        print("DB init error:", e)

# ======= نماذج الطلبات =======
class ChatRequest(BaseModel):
    user_id: str = "default"
    message: str
    top_k: int = 5
    use_web: bool = True
    use_wiki: bool = True
    summarize: bool = True
    save: bool = True

# ======= واجهات =======
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html>
    <head><meta charset="utf-8"><title>{APP_TITLE}</title></head>
    <body style="font-family:Arial;direction:rtl;text-align:center;padding:40px">
      <h1>🧠 {APP_TITLE}</h1>
      <p>بدون مفاتيح — بحث/تلخيص/تحليل/توليد/ذاكرة/نية/مشاعر — يدعم Render Starter</p>
      <p><a href="/docs" style="padding:10px 20px;background:#0b7;color:#fff;border-radius:6px;text-decoration:none">واجهة التوثيق</a></p>
    </body>
    </html>
    """

@app.get("/ping")
def ping():
    return {"ok": True, "engine": APP_TITLE}

@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    added = []
    for f in files:
        path = ingestor.save_and_convert(f)
        added.append(path)
    retriever.rebuild_index()
    return {"ok": True, "added": added}

@app.get("/search")
def search(q: str, top_k: int = 5):
    hits = retriever.search(q, top_k=top_k)
    return {"ok": True, "results": [{"path": h["path"], "score": h["score"]} for h in hits]}

@app.post("/chat")
def chat(req: ChatRequest):
    text = (req.message or "").strip()
    if not text:
        return JSONResponse({"ok": False, "error": "لا توجد رسالة"}, status_code=400)

    # 1) نية + مشاعر
    intent = intent_model.predict(text)
    senti = sentiment.analyze(text)  # {"label": .., "score": ..}

    # 2) استرجاع محلي
    hits = retriever.search(text, top_k=req.top_k)
    local_context = "\n\n".join(h["text"] for h in hits) if hits else ""

    # 3) مصادر خارجية (اختياري)
    snippets = []
    if req.use_web:
        web_results = web_search(text, max_results=5)
        for r in web_results:
            snip = (r.get("body") or r.get("snippet") or "")[:280]
            url = (r.get("href") or r.get("url") or "")[:200]
            if snip:
                snippets.append(f"- {snip} … [{url}]")
    wiki = wiki_summary_ar(text) if req.use_wiki else ""

    # 4) تلخيص
    context_for_answer = local_context
    if req.summarize and local_context:
        context_for_answer = summarizer.combine_and_summarize([h["text"] for h in hits])

    # 5) توليد مبسّط
    answer = generator.answer(
        query=text,
        context=context_for_answer,
        intent=intent,
        sentiment=senti.get("label", "neutral"),
        web_snippets=snippets,
        wiki=wiki
    )

    # 6) ذاكرة + تدريب تلقائي
    if req.save:
        memory.add(req.user_id, text, answer, intent, senti.get("label", "neutral"))
    auto_trainer.maybe_learn(text, intent)

    return JSONResponse({
        "ok": True,
        "intent": intent,
        "sentiment": senti,
        "answer": answer,
        "sources": [{"path": h["path"], "score": h["score"]} for h in hits]
    })

# تدريب يدوي
class TrainExample(BaseModel):
    text: str
    intent: str

@app.post("/train/manual")
def train_manual(examples: List[TrainExample]):
    intent_model.add_examples([(e.text, e.intent) for e in examples])
    intent_model.train()
    return {"ok": True, "classes": intent_model.classes()}

@app.post("/train/auto")
def train_auto():
    n = auto_trainer.learn_from_memory()
    return {"ok": True, "added_examples": n}
