# main.py — النسخة النهائية AI-Core-Engine-Live
from __future__ import annotations
import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# === استيرادات النواة ===
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
from engine.web_agent import gather_web  # عامل الويب الجديد

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
scaffolder = Scaffolder()

@app.on_event("startup")
def _startup():
    init_db()
    try:
        retriever.rebuild_index()
        intent_model.load_or_init()
    except Exception as e:
        print("Startup issue:", e)

# === نماذج البيانات ===
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

# === صفحات أساسية ===
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><head><meta charset='utf-8'><title>{APP_TITLE}</title></head>
    <body style='font-family:Arial;text-align:center;direction:rtl;margin-top:40px'>
      <h2>🧠 {APP_TITLE}</h2>
      <p>بحث ذكي، توليد، تلخيص، تدريب ذاتي، وواجهة مباشرة للبحث في الإنترنت.</p>
      <p>
        <a href='/ui'>واجهة النواة</a> |
        <a href='/live-ui'>البحث الذكي المباشر</a> |
        <a href='/docs'>Swagger</a>
      </p>
    </body></html>
    """

# === واجهة البحث الذكي المباشر ===
@app.get("/live-ui", response_class=HTMLResponse)
def live_ui():
    return """
<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>بحث ذكي مباشر</title>
<style>
  :root{--bg:#0f1222;--card:#161a2d;--text:#eef0ff;--muted:#93a0c9;--accent:#10b981}
  body{font-family:system-ui,Segoe UI,Roboto,Arial;background:var(--bg);color:var(--text);margin:0;padding:16px}
  .wrap{max-width:860px;margin:0 auto}
  .card{background:var(--card);border-radius:14px;padding:14px;box-shadow:0 6px 20px rgba(0,0,0,.20);margin-bottom:14px}
  textarea,select{width:100%;padding:12px;border:1px solid #2a3052;background:#0e1120;color:var(--text);border-radius:10px;font-size:16px}
  button{padding:12px;border:0;border-radius:10px;background:var(--accent);color:#041016;font-weight:700;font-size:16px}
  pre{white-space:pre-wrap}
  .muted{color:var(--muted);font-size:13px}
</style></head>
<body><div class="wrap">
<div class="card">
<h2>🔎 بحث ذكي مباشر</h2>
<textarea id="q" rows="3" placeholder="اكتب سؤالك هنا..."></textarea>
<div style="margin-top:8px;display:flex;gap:8px">
<select id="style">
<option value="">أسلوب افتراضي</option>
<option value="friendly">ودود</option>
<option value="formal">رسمي</option>
<option value="brief">مختصر</option>
</select>
<button onclick="go()">بحث مباشر</button>
</div>
<p class="muted">يتم جلب النتائج من جوجل/دك-دك-جو وويكيبيديا العربية.</p>
</div>
<div id="out" class="card" style="display:none"></div>
</div>
<script>
async function go(){
  const out=document.getElementById('out'); out.style.display='block'; out.innerHTML='<b>جارٍ الجمع من المصادر...</b>';
  const q=document.getElementById('q').value.trim();
  const style=document.getElementById('style').value||null;
  if(!q){ out.innerHTML='اكتب سؤالاً أولاً.'; return; }
  try{
    const r=await fetch('/ask-live',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:q, style})});
    const data=await r.json();
    if(!data.ok){ out.innerHTML='فشل: '+(data.error||''); return; }
    let src=''; if(data.sources?.length){
      src='<hr/><b>المصادر:</b><ul>'+data.sources.map(s=>`<li><a href="${s.link}" target="_blank">${s.title||s.link}</a></li>`).join('')+'</ul>';
    }
    out.innerHTML=`<div class="muted">المحرّك: <b>${data.engine||'none'}</b> — الأسلوب: ${data.style}</div><pre>${data.answer}</pre>`+src;
  }catch{ out.innerHTML='تعذّر الاتصال.'; }
}
</script></body></html>
"""

# === البحث الذكي المباشر (API) ===
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

# === فحص الصحة ===
@app.get("/ping")
def ping():
    return {"ok": True, "engine": APP_TITLE}
