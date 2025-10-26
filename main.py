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

# Startup: قاعدة البيانات
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

class UrlIngestRequest(BaseModel):
    url: str

class TrainExample(BaseModel):
    text: str
    intent: str

# ======= واجهات =======
@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <html>
    <head><meta charset="utf-8"><title>{APP_TITLE}</title></head>
    <body style="font-family:Arial;direction:rtl;text-align:center;padding:40px">
      <h1>🧠 {APP_TITLE}</h1>
      <p>بدون مفاتيح — بحث/تلخيص/تحليل/توليد/ذاكرة/نية/مشاعر — يدعم Render Starter</p>
      <p style="margin-top:24px">
        <a href="/ui" style="padding:10px 20px;background:#0b7;color:#fff;border-radius:8px;text-decoration:none;margin:6px;display:inline-block">واجهة الجوال</a>
        <a href="/docs" style="padding:10px 20px;background:#555;color:#fff;border-radius:8px;text-decoration:none;margin:6px;display:inline-block">التوثيق (Swagger)</a>
      </p>
    </body>
    </html>
    """

@app.get("/ui", response_class=HTMLResponse)
def ui():
    # صفحة HTML خفيفة للجوال تستدعي /chat و /ingest/url
    return """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>واجهة النواة الذكية</title>
<style>
  body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial; background:#f7f7f9; margin:0; padding:16px;}
  .card{background:#fff; border-radius:14px; padding:16px; box-shadow:0 6px 20px rgba(0,0,0,.06); margin-bottom:16px;}
  .title{font-size:20px; margin:0 0 10px}
  input[type="text"], textarea{width:100%; padding:12px; border:1px solid #ddd; border-radius:10px; font-size:16px; box-sizing:border-box;}
  button{padding:12px 16px; border:0; border-radius:10px; background:#0b7; color:#fff; font-size:16px}
  .secondary{background:#555}
  .muted{color:#777; font-size:13px}
  pre{white-space:pre-wrap; word-wrap:break-word;}
  .row{display:flex; gap:8px; align-items:center}
  .row > *{flex:1}
  .badge{background:#0b7;color:#fff;border-radius:10px;padding:2px 8px;font-size:12px}
</style>
</head>
<body>
  <div class="card">
    <h2 class="title">محادثة سريعة</h2>
    <div class="row">
      <input id="msg" type="text" placeholder="اكتب سؤالك هنا..."/>
      <button onclick="send()">إرسال</button>
    </div>
    <p class="muted">سيتم استخدام البحث والويكي والذاكرة داخليًا.</p>
    <div id="out" class="card" style="display:none"></div>
  </div>

  <div class="card">
    <h2 class="title">إضافة مستند بالرابط <span class="badge">/ingest/url</span></h2>
    <div class="row">
      <input id="u" type="text" placeholder="https://example.com/file.pdf أو صفحة ويب"/>
      <button class="secondary" onclick="ingestUrl()">إضافة</button>
    </div>
    <p id="u-status" class="muted"></p>
  </div>

<script>
async function send(){
  const m = document.getElementById('msg').value.trim();
  if(!m){ alert('اكتب رسالة'); return; }
  const out = document.getElementById('out');
  out.style.display='block';
  out.innerHTML = '<b>جارٍ التحليل...</b>';
  try{
    const res = await fetch('/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ user_id: 'bassam', message: m, use_web: true, use_wiki: true, summarize: true })
    });
    const data = await res.json();
    if(!data.ok){ out.innerHTML = 'خطأ: ' + (data.error || ''); return; }
    let src = '';
    if(data.sources && data.sources.length){
      src += '<hr/><b>المصادر المحلية:</b><ul>';
      for(const s of data.sources){ src += `<li>${s.path} (score=${(s.score||0).toFixed(3)})</li>`; }
      src += '</ul>';
    }
    out.innerHTML = `<pre>${data.answer || ''}</pre>` + src;
  }catch(e){
    out.innerHTML = 'خطأ في الاتصال';
  }
}
async function ingestUrl(){
  const u = document.getElementById('u').value.trim();
  const p = document.getElementById('u-status');
  if(!u){ alert('أدخل رابطًا'); return; }
  p.textContent = 'جارٍ جلب وتعلّم الرابط...';
  try{
    const res = await fetch('/ingest/url', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ url: u })
    });
    const data = await res.json();
    if(!data.ok){ p.textContent = 'فشل: ' + (data.error||''); return; }
    p.textContent = 'تمت الإضافة: ' + data.added;
  }catch(e){
    p.textContent = 'تعذر الاتصال بالسيرفر';
  }
}
</script>
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
        for r in web_results or []:
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

@app.post("/train/manual")
def train_manual(examples: List[TrainExample]):
    intent_model.add_examples([(e.text, e.intent) for e in examples])
    intent_model.train()
    return {"ok": True, "classes": intent_model.classes()}

@app.post("/train/auto")
def train_auto():
    n = auto_trainer.learn_from_memory()
    return {"ok": True, "added_examples": n}
