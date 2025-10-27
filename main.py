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
from engine.web_search import google_cse_search

APP_TITLE = "النواة الذكية الاحترافية - Bassam"
app = FastAPI(title=APP_TITLE)

os.makedirs(cfg.DATA_DIR, exist_ok=True)

retriever = Retriever()
summarizer = Summarizer()
generator = AnswerSynthesizer()
intent_model = IntentModel()
sentiment = SentimentAnalyzer()
memory = ConversationMemory()
ingestor = Ingestor()
auto_trainer = AutoTrainer(intent_model, memory)
scaffolder = Scaffolder()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")

@app.on_event("startup")
def _startup():
    try:
        init_db()
    except Exception as e:
        print("DB init error:", e)


# ---------- نماذج ----------
class ChatRequest(BaseModel):
    user_id: str = "default"
    message: str
    top_k: int = 5
    use_web: bool = True
    use_wiki: bool = True
    summarize: bool = True
    save: bool = True
    style: str | None = None


class SmartAnswerRequest(BaseModel):
    query: str
    style: str | None = None
    use_wiki: bool = True
    top_k: int = 5
    summarize: bool = True


# ---------- صفحات HTML ----------
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><head><meta charset='utf-8'><title>{APP_TITLE}</title></head>
    <body style='font-family:Arial;direction:rtl;text-align:center;padding:40px'>
      <h1>🧠 {APP_TITLE}</h1>
      <p>بحث ذكي، تلخيص، تحليل، تعلم ذاتي، فهم نية ومشاعر.</p>
      <a href='/ui' style='padding:10px 20px;background:#0b7;color:#fff;border-radius:8px;text-decoration:none;'>واجهة النواة</a>
      <a href='/smart-google' style='padding:10px 20px;background:#6a5acd;color:#fff;border-radius:8px;text-decoration:none;margin:8px;'>بحث ذكي عبر Google API</a>
    </body></html>
    """


@app.get("/smart-google", response_class=HTMLResponse)
def smart_google_ui():
    html_path = os.path.join("templates", "smart_google.html")
    with open(html_path, encoding="utf-8") as f:
        return HTMLResponse(f.read())


# ---------- API ----------
@app.post("/api/smart_answer")
def api_smart_answer(req: SmartAnswerRequest):
    text = (req.query or "").strip()
    if not text:
        return JSONResponse({"ok": False, "error": "الاستعلام فارغ"}, status_code=400)
    if req.style:
        generator.set_style(req.style)

    intent = intent_model.predict(text)
    senti = sentiment.analyze(text)
    hits = retriever.search(text, top_k=req.top_k)
    local_context = "\n\n".join(h["text"] for h in hits) if hits else ""

    # --- بحث عبر Google API أو بديله ---
    snippets, google_hits, web_used = [], [], "none"
    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        try:
            google_hits = google_cse_search(text, num=5)
            web_used = "google"
            for r in google_hits:
                snip = (r.get("snippet") or "")[:280]
                url = r.get("link") or ""
                snippets.append(f"- {snip} … [{url}]")
        except Exception as e:
            print("Google Search Error:", e)
    else:
        try:
            ddg_hits = web_search(text, max_results=5)
            web_used = "ddg"
            for r in ddg_hits:
                snip = (r.get("snippet") or r.get("body") or "")[:200]
                url = (r.get("url") or r.get("href") or "")
                snippets.append(f"- {snip} … [{url}]")
        except Exception as e:
            print("DDG Search Error:", e)

    wiki = wiki_summary_ar(text) if req.use_wiki else ""
    context_for_answer = summarizer.combine_and_summarize([h["text"] for h in hits]) if req.summarize else local_context

    answer = generator.answer(
        query=text,
        context=context_for_answer,
        intent=intent,
        sentiment=senti.get("label", "neutral"),
        web_snippets=snippets,
        wiki=wiki
    )

    return JSONResponse({
        "ok": True,
        "intent": intent,
        "sentiment": senti,
        "engine": web_used,
        "answer": answer,
        "results": google_hits,
        "sources": [{"path": h["path"], "score": h["score"]} for h in hits]
    })
