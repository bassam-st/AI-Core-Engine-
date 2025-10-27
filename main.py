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
from engine.web import web_search, wiki_summary_ar, google_cse_search
from engine.coder import Scaffolder

APP_TITLE = "النواة الذكية الاحترافية - Bassam"
app = FastAPI(title=APP_TITLE)

# تهيئة مجلد البيانات
os.makedirs(cfg.DATA_DIR, exist_ok=True)

# مكونات النواة
retriever = Retriever()
summarizer = Summarizer()
generator = AnswerSynthesizer()
intent_model = IntentModel()
sentiment = SentimentAnalyzer()
memory = ConversationMemory()
ingestor = Ingestor()
auto_trainer = AutoTrainer(intent_model, memory)
scaffolder = Scaffolder()

# نفضّل جوجل إن كانت المفاتيح متوفرة
PREFER_GOOGLE = os.environ.get("USE_GOOGLE_CSE", "1").strip().lower() in ("1", "true", "yes")

@app.on_event("startup")
def _startup():
    try:
        init_db()
        retriever.rebuild_index()
        intent_model.load_or_init()
    except Exception as e:
        print("Startup error:", e)

# ---------- نماذج ----------
class ChatRequest(BaseModel):
    user_id: str = "default"
    message: str
    top_k: int = 5
    use_web: bool = True
    use_wiki: bool = True
    summarize: bool = True
    save: bool = True
    style: str | None = None  # friendly | formal | brief

class UrlIngestRequest(BaseModel):
    url: str

class TrainExample(BaseModel):
    text: str
    intent: str

class StyleRequest(BaseModel):
    mode: str

class ScaffoldRequest(BaseModel):
    kind: str   # fastapi | html
    name: str

# ---------- صفحات ----------
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html><head><meta charset="utf-8"><title>{APP_TITLE}</title>
    <style>body{{font-family:Arial;direction:rtl;text-align:center;margin-top:40px}}</style></head>
    <body>
      <h2>🧠 {APP_TITLE}</h2>
      <p>بحث ذكي، تلخيص، تحليل نية/مشاعر، توليد، ذاكرة وتعلم ذاتي.</p>
      <p>
        <a href="/ui" style="background:#0b7;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;">واجهة النواة</a>
        &nbsp;
        <a href="/docs" style="background:#555;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;">Swagger</a>
        &nbsp;
        <a href="/google-ui" style="background:#6a5acd;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;">Google API بحث ذكي عبر</a>
      </p>
    </body></html>
    """

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>واجهة النواة الذكية</title>
<style>
  :root{--bg:#0f1222;--card:#161a2d;--text:#eef0ff;--muted:#93a0c9;--accent:#10b981;--btn:#7c3aed}
  body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;background:var(--bg);color:var(--text);margin:0;padding:14px}
  .wrap{max-width:980px;margin:0 auto}
  .card{background:var(--card);border-radius:14px;padding:14px;box-shadow:0 6px 20px rgba(0,0,0,.20);margin-bottom:14px}
  .title{font-size:22px;margin:0 0 10px}
  textarea,input,select{width:100%;padding:12px;border:1px solid #2a3052;background:#0e1120;color:var(--text);border-radius:10px;font-size:16px}
  button{padding:12px;border:0;border-radius:10px;background:var(--accent);color:#041016;font-weight:700;font-size:16px}
  .secondary{background:#424a77;color:#fff}
  .row{display:flex;gap:8px;align-items:center}
  .row>*{flex:1}
  .pill{display:inline-block;padding:4px 10px;border-radius:999px;background:#232a4d;color:#cbd2ff;font-size:12px}
  pre{white-space:pre-wrap}
  .muted{color:var(--muted);font-size:13px}
</style></head>
<body><div class="wrap">

<div class="card">
  <h2 class="title">محادثة سريعة</h2>
  <div class="row">
    <textarea id="msg" rows="3" placeholder="اكتب سؤالك هنا..."></textarea>
    <div style="display:flex;flex-direction:column;gap:8px;width:140px">
      <button onclick="send()">إرسال</button>
      <button class="secondary" onclick="copyAns()">نسخ الإجابة</button>
    </div>
  </div>
  <div class="row" style="margin-top:8px">
    <select id="style">
      <option value="friendly">أسلوب: ودود</option>
      <option value="formal">أسلوب: رسمي</option>
      <option value="brief">أسلوب: مختصر</option>
    </select>
    <label class="pill"><input id="use_web" type="checkbox" checked> استخدام الويب</label>
    <label class="pill"><input id="use_wiki" type="checkbox" checked> ويكي</label>
    <label class="pill"><input id="summarize" type="checkbox" checked> تلخيص</label>
  </div>
  <p class="muted">سيتم الدمج بين المصادر المحلية ونتائج الويب/ويكي.</p>
  <div id="out" class="card" style="display:none"></div>
</div>

<div class="card">
  <h2 class="title">رفع ملفات</h2>
  <div class="row">
    <input id="files" type="file" multiple/>
    <button class="secondary" onclick="uploadFiles()">رفع</button>
  </div>
  <p id="f-status" class="muted"></p>
</div>

<div class="card">
  <h2 class="title">إضافة رابط</h2>
  <div class="row">
    <input id="u" type="text" placeholder="https://example.com/file.pdf أو صفحة ويب"/>
    <button class="secondary" onclick="ingestUrl()">إضافة</button>
  </div>
  <p id="u-status" class="muted"></p>
</div>

<p style="text-align:right"><a class="pill" href="/google-ui">فتح Google UI</a></p>
</div>

<script>
function copyAns(){
  const el = document.querySelector('#out pre');
  if(!el){ alert('لا توجد إجابة بعد'); return; }
  navigator.clipboard.writeText(el.innerText).then(()=>alert('تم النسخ ✅'));
}
async function send(){
  const m = document.getElementById('msg').value.trim();
  if(!m){ alert('اكتب رسالة'); return; }
  const out = document.getElementById('out');
  const style = document.getElementById('style').value;
  const use_web = document.getElementById('use_web').checked;
  const use_wiki = document.getElementById('use_wiki').checked;
  const summarize = document.getElementById('summarize').checked;
  out.style.display='block'; out.innerHTML='<b>جارٍ التحليل...</b>';
  try{
    const res = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},
      body: JSON.stringify({user_id:'bassam',message:m,use_web,use_wiki,summarize,style})});
    const data = await res.json();
    if(!data.ok){ out.innerHTML='خطأ: '+(data.error||''); return; }
    let meta = `<div class="muted">النية: ${data.intent} — المشاعر: ${data.sentiment?.label||data.sentiment} — ويب: <b>${data.web_engine||'none'}</b> — أسلوب: ${data.style}</div>`;
    let src = '';
    if(data.sources?.length){
      src += '<hr/><b>مصادر محلية:</b><ul>';
      for(const s of data.sources){ src += `<li>${s.path} (score=${(s.score||0).toFixed(3)})</li>`; }
      src += '</ul>';
    }
    out.innerHTML = meta + `<pre>${data.answer||''}</pre>` + src;
  }catch(e){ out.innerHTML='خطأ اتصال'; }
}
async function uploadFiles(){
  const inp=document.getElementById('files'); const p=document.getElementById('f-status');
  if(!inp.files.length){ alert('اختر ملفات'); return; }
  p.textContent='جارٍ الرفع...';
  try{
    const fd=new FormData(); for(const f of inp.files){ fd.append('files',f); }
    const res=await fetch('/ingest',{method:'POST',body:fd}); const data=await res.json();
    p.textContent=data.ok?('تم: '+(data.added||[]).join(', ')):('فشل: '+(data.error||'')); 
  }catch{ p.textContent='تعذر الاتصال'; }
}
async function ingestUrl(){
  const u=document.getElementById('u').value.trim(); const p=document.getElementById('u-status');
  if(!u){ alert('أدخل رابط'); return; }
  p.textContent='جارٍ الجلب والتعلّم...';
  try{
    const res=await fetch('/ingest/url',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:u})});
    const data=await res.json(); p.textContent=data.ok?('تمت الإضافة: '+data.added):('فشل: '+(data.error||'')); 
  }catch{ p.textContent='تعذر الاتصال'; }
}
</script>
</body></html>
    """

@app.get("/google-ui", response_class=HTMLResponse)
def google_ui(q: str = ""):
    cx = os.environ.get("GOOGLE_CSE_ID", "").strip()
    if not cx:
        return HTMLResponse("<p style='font-family:Arial'>يجب ضبط GOOGLE_CSE_ID في Environment.</p>", status_code=500)
    return f"""
<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>نتائج جوجل (مضمنة)</title>
<style>body{{font-family:Arial;margin:0;padding:10px;background:#0f1222;color:#fff}}
.wrap{{max-width:900px;margin:0 auto}} a{{color:#9be}} .box{{background:#161a2d;border-radius:12px;padding:12px}}</style>
<script async src="https://cse.google.com/cse.js?cx={cx}"></script>
</head><body>
<div class="wrap">
  <h2>نتائج البحث (Google)</h2>
  <div class="gcse-searchbox-only" data-autoSearchOnLoad="{'true' if q else 'false'}" data-query="{q}"></div>
  <div class="box" style="margin-top:10px"><div class="gcse-searchresults-only"></div></div>
  <p><a href="/ui">⬅ العودة</a></p>
</div></body></html>"""

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

@app.get("/search")
def search(q: str, top_k: int = 5):
    hits = retriever.search(q, top_k=top_k)
    return {"ok": True, "results": [{"path": h["path"], "score": h["score"]} for h in hits]}

@app.get("/web/google")
def web_google(q: str, num: int = 5):
    data = google_cse_search(q, num=num)
    return {"ok": True, "results": data, "used_google": bool(data)}

@app.post("/settings/style")
def set_style(req: StyleRequest):
    generator.set_style(req.mode)
    return {"ok": True, "style": req.mode}

@app.post("/chat")
def chat(req: ChatRequest):
    text = (req.message or "").strip()
    if not text:
        return JSONResponse({"ok": False, "error": "لا توجد رسالة"}, status_code=400)
    if req.style:
        generator.set_style(req.style)

    intent = intent_model.predict(text)
    senti = sentiment.analyze(text)

    hits = retriever.search(text, top_k=req.top_k)
    local_context = "\n\n".join(h["text"] for h in hits) if hits else ""

    snippets = []
    web_used = "none"
    if req.use_web:
        google_hits = google_cse_search(text, num=5) if PREFER_GOOGLE else []
        if google_hits:
            web_used = "google"
            for r in google_hits:
                sn = (r.get("body") or "")[:280]
                url = (r.get("href") or "")[:200]
                if sn:
                    snippets.append(f"- {sn} … [{url}]")
        else:
            ddg_hits = web_search(text, max_results=5)
            if ddg_hits:
                web_used = "ddg"
            for r in ddg_hits or []:
                sn = (r.get("body") or r.get("snippet") or "")[:280]
                url = (r.get("href") or r.get("url") or "")[:200]
                if sn:
                    snippets.append(f"- {sn} … [{url}]")

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
        "style": req.style or generator.style,
        "answer": answer,
        "sources": [{"path": h["path"], "score": h["score"]} for h in hits]
    })

@app.post("/train/manual")
def train_manual(examples: List[TrainExample]):
    intent_model.add_examples([(e.text, e.intent) for e in examples])
    intent_model.train()
    return {"ok": True, "classes": intent_model.classes()}

@app.post("/train/auto")
def train_auto():
    n = auto_trainer.learn_from_memory()
    return {"ok": True, "added_examples": n}

@app.post("/code/scaffold")
def code_scaffold(req: ScaffoldRequest):
    try:
        path = scaffolder.scaffold(req.kind, req.name)
        return {"ok": True, "zip_path": path}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)
