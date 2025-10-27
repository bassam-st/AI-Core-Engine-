from __future__ import annotations
from fastapi import FastAPI, UploadFile, File
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
from engine.coder import Scaffolder
from engine.web import web_search, wiki_summary_ar
from engine.web_search import google_cse_search  # ← أضفنا هذا

APP_TITLE = "النواة الذكية الاحترافية - Bassam"
app = FastAPI(title=APP_TITLE)

# تهيئة المسارات
os.makedirs(cfg.DATA_DIR, exist_ok=True)

# تحميل المكونات
retriever = Retriever()
summarizer = Summarizer()
generator = AnswerSynthesizer()
intent_model = IntentModel()
sentiment = SentimentAnalyzer()
memory = ConversationMemory()
ingestor = Ingestor()
auto_trainer = AutoTrainer(intent_model, memory)
scaffolder = Scaffolder()

# تفضيل جوجل إذا المفاتيح متوفرة
PREFER_GOOGLE = os.getenv("USE_GOOGLE_CSE", "1").lower() in ("1", "true", "yes")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")

@app.on_event("startup")
def _startup():
    try:
        init_db()
    except Exception as e:
        print("DB init error:", e)

# ---------- نماذج الطلبات ----------
class ChatRequest(BaseModel):
    user_id: str = "default"
    message: str
    top_k: int = 5
    use_web: bool = True
    use_wiki: bool = True
    summarize: bool = True
    save: bool = True
    style: str | None = None

class UrlIngestRequest(BaseModel):
    url: str

class TrainExample(BaseModel):
    text: str
    intent: str

class StyleRequest(BaseModel):
    mode: str

class ScaffoldRequest(BaseModel):
    kind: str
    name: str

# ---------- صفحات HTML ----------
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html>
    <head><meta charset='utf-8'><title>{APP_TITLE}</title></head>
    <body style='font-family:Arial;direction:rtl;text-align:center;padding:40px'>
      <h1>🧠 {APP_TITLE}</h1>
      <p>نظام ذكي للبحث، التحليل، التلخيص، التعلم، وفهم النية والمشاعر.</p>
      <a href='/ui' style='background:#0b7;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;'>واجهة الجوال</a>
      <a href='/google-ui' style='background:#6a5acd;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;margin:8px;'>بحث جوجل المدمج</a>
    </body>
    </html>
    """

@app.get("/google-ui", response_class=HTMLResponse)
def google_ui(q: str = ""):
    if not GOOGLE_CSE_ID:
        return HTMLResponse("<p>يجب ضبط GOOGLE_CSE_ID في Environment.</p>", status_code=500)
    return f"""
    <!doctype html><html lang="ar" dir="rtl"><head>
    <meta charset="utf-8"/><title>بحث جوجل المدمج</title>
    <script async src="https://cse.google.com/cse.js?cx={GOOGLE_CSE_ID}"></script>
    </head><body style="font-family:Arial;background:#0f1222;color:#fff">
    <h2>نتائج بحث جوجل</h2><div class="gcse-search"></div>
    </body></html>
    """

# ---------- API ----------
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

@app.post("/ingest/url")
def ingest_url(req: UrlIngestRequest):
    try:
        path = ingestor.ingest_from_url(req.url)
        retriever.rebuild_index()
        return {"ok": True, "added": path}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)

@app.post("/chat")
def chat(req: ChatRequest):
    text = (req.message or "").strip()
    if not text:
        return JSONResponse({"ok": False, "error": "الرسالة فارغة"}, status_code=400)
    if req.style:
        generator.set_style(req.style)

    intent = intent_model.predict(text)
    senti = sentiment.analyze(text)
    hits = retriever.search(text, top_k=req.top_k)
    local_context = "\n\n".join(h["text"] for h in hits) if hits else ""

    snippets = []
    web_used = "none"
    if req.use_web:
        google_hits = []
        if GOOGLE_API_KEY and GOOGLE_CSE_ID and PREFER_GOOGLE:
            try:
                google_hits = google_cse_search(text, num=5)
                web_used = "google"
            except Exception as e:
                print("Google search failed:", e)

        if not google_hits:
            try:
                ddg_hits = web_search(text, max_results=5)
                if ddg_hits:
                    web_used = "ddg"
                    for r in ddg_hits:
                        snip = (r.get("snippet") or "")[:200]
                        url = (r.get("url") or "")
                        if snip:
                            snippets.append(f"- {snip} … [{url}]")
            except Exception as e:
                print("DDG search failed:", e)

        for r in google_hits:
            snip = (r.get("snippet") or "")[:200]
            url = (r.get("link") or "")
            snippets.append(f"- {snip} … [{url}]")

    wiki = wiki_summary_ar(text) if req.use_wiki else ""
    context_for_answer = local_context
    if req.summarize and local_context:
        context_for_answer = summarizer.combine_and_summarize([h["text"] for h in hits])

    answer = generator.answer(
        query=text,
        context=context_for_answer,
        intent=intent,
        sentiment=senti.get("label", "neutral"),
        web_snippets=snippets,
        wiki=wiki
    )

    if req.save:
        memory.add(req.user_id, text, answer, intent, senti.get("label", "neutral"))
    auto_trainer.maybe_learn(text, intent)

    return JSONResponse({
        "ok": True,
        "intent": intent,
        "sentiment": senti,
        "web_engine": web_used,
        "answer": answer,
        "sources": [{"path": h["path"], "score": h["score"]} for h in hits]
    })
