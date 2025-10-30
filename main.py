# main.py — النسخة الكاملة المحدثة AI-Core-Engine + Xtream
from __future__ import annotations
import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# === استيرادات النواة الأساسية ===
from engine.config import cfg
from engine.retriever import Retriever
from engine.summarizer import Summarizer
from engine.generator import AnswerSynthesizer
from engine.intent import IntentModel
from engine.sentiment import SentimentAnalyzer
from engine.memory import ConversationMemory, init_db
from engine.ingest import Ingestor
from engine.trainer import AutoTrainer
from engine.web import web_search, wiki_summary_ar, google_cse_search
from engine.coder import Scaffolder
from engine.web_agent import gather_web
from engine.sports import get_today_fixtures

# === استيراد Xtream Proxy Router ===
from engine.xtream_proxy import router as xtream_router

APP_TITLE = "🧠 النواة الذكية الاحترافية – Bassam"
app = FastAPI(title=APP_TITLE)

# --- تضمين راوتر Xtream ---
app.include_router(xtream_router)

# --- إعداد المجلدات ---
os.makedirs(cfg.DATA_DIR, exist_ok=True)
EXPORT_DIR = Path(cfg.DATA_DIR) / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/exports", StaticFiles(directory=str(EXPORT_DIR)), name="exports")

# --- مكونات النواة ---
retriever = Retriever()
summarizer = Summarizer()
generator = AnswerSynthesizer()
intent_model = IntentModel()
sentiment = SentimentAnalyzer()
memory = ConversationMemory()
ingestor = Ingestor()
auto_trainer = AutoTrainer(intent_model, memory)
scaffolder = Scaffolder()

@app.on_event("startup")
def _startup():
    init_db()
    try:
        retriever.rebuild_index()
        intent_model.load_or_init()
    except Exception as e:
        print("Startup issue:", e)

# === تهيئة القوالب ===
templates = Jinja2Templates(directory="templates")

# === النماذج ===
class ChatRequest(BaseModel):
    user_id: str = "default"
    message: str
    top_k: int = 5
    use_web: bool = True
    use_wiki: bool = True
    summarize: bool = True
    save: bool = True
    style: Optional[str] = None

class UrlIngestRequest(BaseModel):
    url: str

class TrainExample(BaseModel):
    text: str
    intent: str

class ScaffoldRequest(BaseModel):
    kind: str
    name: str

class LiveAskRequest(BaseModel):
    message: str
    top_n: int = 5
    include_steps: bool = True
    style: Optional[str] = None

# === الصفحة الرئيسية ===
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><head><meta charset='utf-8'><title>{APP_TITLE}</title></head>
    <body style='font-family:Arial;text-align:center;direction:rtl;margin-top:40px'>
      <h2>{APP_TITLE}</h2>
      <p>بحث ذكي، توليد، تلخيص، تدريب ذاتي، ومشاهدة مباريات مباشرة.</p>
      <p>
        <a href='/ui'>واجهة النواة</a> |
        <a href='/live-ui'>🔍 البحث الذكي المباشر</a> |
        <a href='/ui/sports'>🏟️ مباريات اليوم</a> |
        <a href='/ui/xtream'>🎬 قنوات Xtream</a> |
        <a href='/docs'>Swagger</a>
      </p>
    </body></html>
    """

# === البحث الذكي المباشر ===
@app.post("/ask-live")
def ask_live(req: LiveAskRequest):
    q = (req.message or "").strip()
    if not q:
        return JSONResponse({"ok": False, "error": "الرسالة فارغة."}, status_code=400)
    if req.style:
        generator.set_style(req.style)
    intent = intent_model.predict(q)
    senti = sentiment.analyze(q)
    try:
        web_snippets, sources, wiki, engine_used = gather_web(q, num=req.top_n, fetch_pages=True)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    answer = generator.answer(
        query=q,
        context="",
        intent=intent,
        sentiment=senti.get("label", "neutral"),
        web_snippets=web_snippets,
        wiki=wiki,
    )
    return JSONResponse({
        "ok": True,
        "engine": engine_used,
        "style": req.style or generator.style,
        "answer": answer,
        "sources": sources
    })

# === صفحات وعروض قسم المباريات ===
@app.get("/api/sports/today")
async def api_sports_today(league: str | None = Query(default=None)):
    return await get_today_fixtures(league_filter=league)

@app.get("/ui/sports")
async def ui_sports(request: Request, league: str | None = None):
    return templates.TemplateResponse(
        "sports_today.html",
        {"request": request, "league": league or ""}
    )

@app.get("/ui/sports_player")
async def ui_sports_player(request: Request, url: str | None = None):
    return templates.TemplateResponse(
        "sports_player.html",
        {"request": request, "url": url or ""}
    )

# === واجهة قنوات Xtream ===
@app.get("/ui/xtream", response_class=HTMLResponse)
def ui_xtream():
    return """
<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>قنوات Xtream</title>
<style>
 body{font-family:system-ui,Segoe UI,Roboto,Arial;background:#0f172a;color:#e2e8f0;margin:0;padding:16px}
 .wrap{max-width:860px;margin:auto}
 .row{border:1px solid #223;border-radius:14px;padding:12px;margin:10px 0;background:#0b1220}
 .ctrl{display:flex;gap:8px;align-items:center;margin:10px 0}
 input,button,select{font-family:inherit}
 .btn{padding:10px 12px;border:0;border-radius:10px;background:#10b981;color:#041016;font-weight:700;cursor:pointer}
 .badge{display:inline-block;padding:4px 8px;border-radius:9999px;background:#1f2937}
</style></head>
<body><div class="wrap">
  <h2>🎬 قنوات Xtream</h2>
  <div class="ctrl">
    <input id="q" placeholder="إبحث عن قناة (مثال: beIN, SSC, MBC)" style="flex:1;padding:10px;border-radius:10px;border:1px solid #223;background:#0b1220;color:#e2e8f0">
    <button class="btn" onclick="load()">تحديث</button>
  </div>
  <div id="list"></div>
</div>
<script>
async function load(){
  const q=document.getElementById('q').value||"";
  const r=await fetch('/api/xtream/channels'+(q?`?q=${encodeURIComponent(q)}`:''));
  const data=await r.json();
  const list=document.getElementById('list'); list.innerHTML='';
  if(!data.items || !data.items.length){ list.innerHTML='<div class="row">لا توجد نتائج.</div>'; return; }
  for(const ch of data.items){
    const div=document.createElement('div'); div.className='row';
    div.innerHTML = `
      <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap">
        <div>
          <div style="font-weight:700">${ch.name}</div>
          <div class="badge">ID: ${ch.stream_id}</div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
          <a class="btn" href="/ui/sports_player?url=${encodeURIComponent(ch.m3u8)}">تشغيل</a>
          <a class="badge" target="_blank" href="${ch.m3u8}">m3u8</a>
        </div>
      </div>`;
    list.appendChild(div);
  }
}
load();
</script>
</body></html>
"""

# === فحص الصحة ===
@app.get("/ping")
def ping():
    return {"ok": True, "engine": APP_TITLE}
