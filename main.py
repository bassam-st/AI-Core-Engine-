# main.py — AI-Core-Engine-Live (Xtream Ready)
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# === النواة (ابقِها كما لديك إن كانت موجودة) ===
from engine.config import cfg
from engine.retriever import Retriever
from engine.summarizer import Summarizer
from engine.generator import AnswerSynthesizer
from engine.intent import IntentModel
from engine.sentiment import SentimentAnalyzer
from engine.memory import ConversationMemory, init_db
from engine.ingest import Ingestor
from engine.trainer import AutoTrainer

# إن كان عندك وظائف رياضية/ويب احتفظ بها، وإلا تجاهل
try:
    from engine.web_agent import gather_web
except Exception:
    def gather_web(*args, **kwargs):
        return [], [], {}, "none"

try:
    from engine.sports import get_today_fixtures
except Exception:
    async def get_today_fixtures(league_filter: str | None = None):
        return {"ok": True, "fixtures": []}

# === Xtream Router ===
from engine.xtream_proxy import router as xtream_router

APP_TITLE = "النواة الذكية الاحترافية – Bassam"
app = FastAPI(title=APP_TITLE)

# --- مجلدات ---
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

@app.on_event("startup")
def _startup():
    init_db()
    try:
        retriever.rebuild_index()
        intent_model.load_or_init()
    except Exception as e:
        print("Startup issue:", e)

# === قوالب (لو لديك مجلد templates؛ وإلا ليست مطلوبة لهذه الواجهة) ===
templates = Jinja2Templates(directory="templates")

# === صفحات أساسية ===
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><head><meta charset='utf-8'><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{APP_TITLE}</title></head>
    <body style='font-family:Arial;text-align:center;direction:rtl;margin-top:40px'>
      <h2>🧠 {APP_TITLE}</h2>
      <p>بحث ذكي، توليد، تلخيص، تدريب ذاتي، ومشاهدة مباريات وقنوات Xtream.</p>
      <p>
        <a href='/ui/xtream'>📺 قنوات Xtream</a> |
        <a href='/ui/sports'>🏟️ مباريات اليوم</a> |
        <a href='/docs'>Swagger</a>
      </p>
    </body></html>
    """

# === واجهة قنوات Xtream ===
@app.get("/ui/xtream", response_class=HTMLResponse)
def ui_xtream():
    return """
<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>قنوات Xtream</title>
<style>
 body{font-family:system-ui,Segoe UI,Roboto,Arial;background:#0f172a;color:#e2e8f0;margin:0;padding:16px}
 .wrap{max-width:880px;margin:auto}
 .row{border:1px solid #223; border-radius:14px; padding:12px; margin:10px 0; background:#0b1220}
 input,button{font-family:inherit}
 .ctrl{display:flex;gap:8px;align-items:center;margin-bottom:12px}
 .btn{padding:10px 14px;border:0;border-radius:10px;background:#10b981;color:#041016;font-weight:700}
 .badge{display:inline-block;padding:4px 8px;border-radius:9999px;background:#1f2937;color:#e2e8f0;margin:2px}
 video{width:100%;max-height:60vh;background:#000;border-radius:12px}
</style></head>
<body><div class="wrap">
  <h2>📺 قنوات Xtream</h2>
  <div class="ctrl">
    <input id="q" placeholder="ابحث عن قناة (مثال: SSC, beIN, MBC)" style="flex:1;padding:10px;border-radius:10px;border:1px solid #223;background:#0b1220;color:#e2e8f0"/>
    <button class="btn" onclick="load()">تحديث</button>
  </div>
  <div id="count"></div>
  <div id="list"></div>
  <hr/>
  <div id="player" style="display:none">
    <h3 id="now"></h3>
    <video id="v" controls playsinline></video>
  </div>
</div>
<script>
let all=[];
async function load(){
  const r=await fetch('/api/xtream/channels');
  const data=await r.json();
  all=data.channels||[];
  render();
}
function render(){
  const q=(document.getElementById('q').value||'').trim().toLowerCase();
  let items = q ? all.filter(c => (c.name||'').toLowerCase().includes(q)) : all;
  document.getElementById('count').innerHTML='القنوات: '+items.length;
  const box=document.getElementById('list'); box.innerHTML='';
  if(!items.length){ box.innerHTML='<div class="row">لا توجد نتائج.</div>'; return; }
  for(const c of items.slice(0,300)){
    const d=document.createElement('div'); d.className='row';
    d.innerHTML = `
      <div><b>${c.name||''}</b> <span class="badge">${c.category||''}</span></div>
      <div style="margin-top:6px;display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn" onclick="play(${c.stream_id})">تشغيل</button>
      </div>
    `;
    box.appendChild(d);
  }
}
async function play(id){
  // استخدم بروكسي m3u8 لتجاوز Mixed Content
  const url = '/api/xtream/stream/'+id+'.m3u8';
  document.getElementById('player').style.display='block';
  document.getElementById('now').innerText='تشغيل: '+id;
  const v=document.getElementById('v'); v.src=url; v.play().catch(()=>{});
}
load();
</script>
</body></html>
"""

# === مباريات اليوم (اختياري) ===
@app.get("/api/sports/today")
async def api_sports_today(league: str | None = Query(default=None)):
    return await get_today_fixtures(league_filter=league)

@app.get("/ui/sports")
def ui_sports_page() -> HTMLResponse:
    return HTMLResponse("""
<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>مباريات اليوم</title>
<style>body{background:#0f172a;color:#e2e8f0;font-family:system-ui,Segoe UI,Arial;padding:16px}</style>
</head><body>
<h2>🏟️ مباريات اليوم</h2>
<p>هذه صفحة مبسطة. إن أردت نسختك القديمة أخبرني أرسلك القالب كامل.</p>
</body></html>
    """)

# === صحّة ===
@app.get("/ping")
def ping():
    return {"ok": True, "engine": APP_TITLE}

# === ربط راوتر Xtream ===
app.include_router(xtream_router)
