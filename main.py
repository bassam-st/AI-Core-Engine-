# main.py — AI-Core-Engine-Live + Sports + Xtream (قنوات + تشغيل)
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

# === استيرادات النواة الأصلية (لا تغييرات) ===
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

# === مفاتيح البيئة ===
SECRET_KEY    = os.getenv("SECRET_KEY", "")
XTREAM_SECRET = os.getenv("XTREAM_SECRET", SECRET_KEY)  # احتياط
XTREAM_BASE   = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER   = os.getenv("XTREAM_USER", "")
XTREAM_PASS   = os.getenv("XTREAM_PASS", "")

APP_TITLE = "النواة الذكية الاحترافية – Bassam"
app = FastAPI(title=APP_TITLE)

# --- مجلدات ثابتة ---
os.makedirs(cfg.DATA_DIR, exist_ok=True)
EXPORT_DIR = Path(cfg.DATA_DIR) / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/exports", StaticFiles(directory=str(EXPORT_DIR)), name="exports")

# --- مكونات النواة (كما هي) ---
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

templates = Jinja2Templates(directory="templates")

# =========================
# واجهات أساسية (كما هي)
# =========================
class LiveAskRequest(BaseModel):
    message: str
    top_n: int = 5
    include_steps: bool = True
    style: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><head><meta charset='utf-8'><title>{APP_TITLE}</title></head>
    <body style='font-family:Arial;text-align:center;direction:rtl;margin-top:40px'>
      <h2>🧠 {APP_TITLE}</h2>
      <p>بحث ذكي، توليد، تلخيص، تدريب ذاتي، ومشاهدة مباريات مباشرة.</p>
      <p>
        <a href='/ui'>واجهة النواة</a> |
        <a href='/live-ui'>البحث الذكي المباشر</a> |
        <a href='/ui/sports'>🏟️ مباريات اليوم</a> |
        <a href='/xtream-ui'>🎥 قنوات Xtream</a> |
        <a href='/docs'>Swagger</a>
      </p>
    </body></html>
    """

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
  pre{white-space:pre-wrap}.muted{color:var(--muted);font-size:13px}
</style></head>
<body><div class="wrap">
<div class="card">
<h2>🔎 بحث ذكي مباشر</h2>
<textarea id="q" rows="3" placeholder="اكتب سؤالك هنا..."></textarea>
<div style="margin-top:8px;display:flex;gap:8px">
<select id="style"><option value="">أسلوب افتراضي</option>
<option value="friendly">ودود</option><option value="formal">رسمي</option><option value="brief">مختصر</option></select>
<button onclick="go()">بحث مباشر</button></div>
<p class="muted">يتم جلب النتائج من جوجل/دك-دك-جو وويكيبيديا العربية.</p>
</div><div id="out" class="card" style="display:none"></div></div>
<script>
async function go(){
  const out=document.getElementById('out'); out.style.display='block'; out.innerHTML='<b>جارٍ الجمع من المصادر...</b>';
  const q=document.getElementById('q').value.trim(); const style=document.getElementById('style').value||null;
  if(!q){ out.innerHTML='اكتب سؤالاً أولاً.'; return; }
  try{
    const r=await fetch('/ask-live',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:q, style})});
    const data=await r.json();
    if(!data.ok){ out.innerHTML='فشل: '+(data.error||''); return; }
    let src=''; if(data.sources?.length){ src='<hr/><b>المصادر:</b><ul>'+data.sources.map(s=>`<li><a href="${s.link}" target="_blank">${s.title||s.link}</a></li>`).join('')+'</ul>'; }
    out.innerHTML=`<div class="muted">المحرّك: <b>${data.engine||'none'}</b></div><pre>${data.answer}</pre>`+src;
  }catch{ out.innerHTML='تعذّر الاتصال.'; }
}
</script></body></html>
"""

@app.post("/ask-live")
def ask_live(req: LiveAskRequest):
    q = (req.message or "").strip()
    if not q:
        return JSONResponse({"ok": False, "error": "الرسالة فارغة."}, status_code=400)
    try:
        web_snippets, sources, wiki, engine_used = gather_web(q, num=req.top_n, fetch_pages=True)
        answer = generator.answer(query=q, context="", web_snippets=web_snippets, wiki=wiki)
        return JSONResponse({"ok": True, "engine": engine_used, "style": req.style or "", "answer": answer, "sources": sources})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# =========================
# قسم المباريات (كما كان)
# =========================
@app.get("/api/sports/today")
async def api_sports_today(league: str | None = Query(default=None)):
    return await get_today_fixtures(league_filter=league)

@app.get("/ui/sports")
async def ui_sports(request: Request, league: str | None = None):
    return templates.TemplateResponse("sports_today.html", {"request": request, "league": league or ""})

@app.get("/ui/sports_player")
async def ui_sports_player(request: Request, url: str | None = None):
    return templates.TemplateResponse("sports_player.html", {"request": request, "url": url or ""})

# =========================
# Xtream IPTV  (قنوات + تشغيل)
# =========================
def _xtream_ready() -> bool:
    return bool(XTREAM_BASE and XTREAM_USER and XTREAM_PASS)

def _xtream_api(action: str, params: dict | None = None) -> dict | list:
    """
    استدعاء API القياسي لـ Xtream: player_api.php
    أمثلة actions:
      - 'get_live_streams'
      - 'get_live_categories'
      - 'get_vod_streams', ...
    """
    if not _xtream_ready():
        raise RuntimeError("XTREAM_BASE/USER/PASS غير مضبوطة.")
    url = f"{XTREAM_BASE}/player_api.php"
    q = {"username": XTREAM_USER, "password": XTREAM_PASS}
    if action:
        q["action"] = action
    if params:
        q.update(params)
    r = requests.get(url, params=q, timeout=15)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        # بعض السيرفرات ترجع نصاً — نعيده كما هو للفحص
        return {"raw": r.text}

@app.get("/xtream-ui", response_class=HTMLResponse)
def xtream_ui():
    """واجهة بسيطة بالقائمة والبحث، تعتمد على /api/xtream/..."""
    if not _xtream_ready():
        return HTMLResponse("""
        <html dir='rtl'><head><meta charset='utf-8'><title>Xtream</title></head>
        <body style='font-family:Arial;background:#0f1222;color:#fff;text-align:center'>
          <h2>⚠️ لم يتم ضبط بيانات Xtream</h2>
          <p>أضف XTREAM_BASE, XTREAM_USER, XTREAM_PASS في Render أو .env</p>
        </body></html>""", status_code=500)

    return HTMLResponse("""
<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>🎥 قنوات Xtream</title>
<style>
  body{background:#0f1222;color:#eef0ff;font-family:system-ui,Segoe UI,Arial;margin:0}
  .wrap{max-width:920px;margin:16px auto;padding:0 12px}
  .bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
  input,select{padding:10px;border-radius:10px;border:1px solid #2a3052;background:#0e1120;color:#eef0ff}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;margin-top:12px}
  .card{background:#161a2d;border-radius:12px;padding:10px}
  .title{font-weight:700;margin:0 0 4px}
  .muted{color:#93a0c9;font-size:12px}
  .btn{display:inline-block;padding:8px 10px;border-radius:8px;background:#10b981;color:#041016;text-decoration:none;font-weight:700}
</style></head>
<body><div class="wrap">
  <h2>🎥 قنوات Xtream</h2>
  <div class="bar">
    <input id="q" placeholder="ابحث عن قناة (مثال: beIN, SSC, MBC)"/>
    <select id="cat"><option value="">كل التصنيفات</option></select>
    <button class="btn" onclick="load()">تحديث</button>
  </div>
  <div id="out" class="grid"></div>
</div>
<script>
async function loadCats(){
  const r=await fetch('/api/xtream/categories'); const cats=await r.json();
  const sel=document.getElementById('cat'); sel.innerHTML='<option value=\"\">كل التصنيفات</option>';
  cats.forEach(c=>{ const o=document.createElement('option'); o.value=c.category_id; o.textContent=c.category_name; sel.appendChild(o); });
}
async function load(){
  const q=document.getElementById('q').value.trim(); const cat=document.getElementById('cat').value;
  const url=new URL('/api/xtream/channels', location.origin);
  if(q) url.searchParams.set('q', q);
  if(cat) url.searchParams.set('cat_id', cat);
  const r=await fetch(url); const data=await r.json();
  const out=document.getElementById('out'); out.innerHTML='';
  if(!Array.isArray(data) || !data.length){ out.innerHTML='<div class="card">لا توجد نتائج.</div>'; return; }
  data.forEach(ch=>{
    const div=document.createElement('div'); div.className='card';
    const name=ch.name || ('ID '+ch.stream_id);
    div.innerHTML = `
      <div class="title">${name}</div>
      <div class="muted">ID: ${ch.stream_id} • ${ch.category_name||''}</div>
      <a class="btn" href="/xtream/play/${ch.stream_id}?ext=m3u8" target="_blank">تشغيل ▶️</a>
    `;
    out.appendChild(div);
  });
}
loadCats(); load();
</script></body></html>
""")

@app.get("/api/xtream/categories")
def xtream_categories():
    """قائمة التصنيفات"""
    try:
        data = _xtream_api("get_live_categories")
        # بعض السيرفرات تُرجع dict بداخلها قائمة
        if isinstance(data, dict) and "categories" in data:
            data = data["categories"]
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/xtream/channels")
def xtream_channels(q: str | None = None, cat_id: str | None = None, limit: int = 200):
    """
    جلب قنوات Live. يدعم:
      - q: فلترة نصية على الاسم
      - cat_id: فلترة على تصنيف معيّن
    """
    try:
        items = _xtream_api("get_live_streams")
        if isinstance(items, dict) and "streams" in items:
            items = items["streams"]

        # تنظيف وتوسيع بعض الحقول الشائعة
        for it in items:
            it["name"] = it.get("name") or it.get("stream_display_name") or f"ID {it.get('stream_id')}"
            # بعض APIs ترجع category_id فقط — نتركها فارغة إن لم تتوفر
            it["category_name"] = it.get("category_name", "")

        # فلترة
        if q:
            qlow = q.lower()
            items = [x for x in items if qlow in (x["name"] or "").lower()]
        if cat_id:
            items = [x for x in items if str(x.get("category_id", "")) == str(cat_id)]

        # حد أعلى للنتائج
        items = items[:max(10, min(limit, 1000))]
        return JSONResponse(items)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/xtream/play/{stream_id}")
def xtream_play(stream_id: str, ext: str = "m3u8"):
    """
    تحويل (Redirect) إلى رابط البث المباشر للقناة.
    لاحقًا يمكنك تمرير user-agent أو header عبر مشغّل داخلي (ExoPlayer في أندرويد).
    """
    if not _xtream_ready():
        return JSONResponse({"ok": False, "error": "Xtream غير مُعد."}, status_code=500)

    # بعض السيرفرات تعمل .ts فقط، وبعضها .m3u8
    ext = "m3u8" if ext.lower() not in ("ts", "m3u8") else ext.lower()
    live_url = f"{XTREAM_BASE}/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return RedirectResponse(url=live_url, status_code=302)

# =========================
# صحة
# =========================
@app.get("/ping")
def ping():
    return {"ok": True, "engine": APP_TITLE}
