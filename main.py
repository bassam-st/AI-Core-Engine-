
# -*- coding: utf-8 -*-
from __future__ import annotations
import os, base64
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

app = FastAPI(title="النواة الذكية الاحترافية – Bassam")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from engine.xtream_proxy import router as xtream_router
app.include_router(xtream_router)

CONV_MEMORY: List[dict] = []

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_HOME

@app.get("/ui/xtream", response_class=HTMLResponse)
def ui_xtream():
    return HTML_XTREAM

@app.get("/ping")
def ping():
    return {"ok": True, "app": "Bassam AI Core Engine", "xtream": True}

@app.post("/ask")
async def ask(body: dict):
    question = (body.get("question") or "").strip()
    language = body.get("language") or "ar"
    system_hint = body.get("system_hint") or "أجب باحتراف وبوضوح وبالعربية الفصحى المبسطة."

    context = "\\n".join([f"User: {m['user']}\\nAssistant: {m['assistant']}" for m in CONV_MEMORY[-8:]])
    parts = [
        system_hint,
        "السياق السابق (اختصره ثم اجب بدقة):",
        context,
        "",
        "سؤال المستخدم:",
        question,
        "",
        "متطلبات الإجابة:",
        "- إن كانت تحتاج خطوات، اعرضها مرقمة.",
        "- اختصر ولا تخلّ بالدقة.",
        "- أخرج أمثلة عملية عندما يكون ذلك مفيدًا.",
        f"- أعد الجواب بالعربية ({language})."
    ]
    prompt = "\n".join(parts)

    if not OPENAI_API_KEY:
        return JSONResponse({"ok": False, "error": "Missing OPENAI_API_KEY"}, status_code=400)

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        answer = data["choices"][0]["message"]["content"]

    CONV_MEMORY.append({"user": question, "assistant": answer})
    return {"ok": True, "answer": answer}

@app.post("/learn/text")
async def learn_text(text: str = Form(...), note: Optional[str] = Form(None)):
    snippet = text[:2000]
    CONV_MEMORY.append({"user": f"[تعلم/معلومة]: {note or ''}", "assistant": f"(حُفظت المعلومة): {snippet}"})
    return {"ok": True, "saved_chars": len(snippet)}

@app.post("/learn/file")
async def learn_file(file: UploadFile = File(...)):
    content = await file.read()
    try:
        text = content.decode("utf-8", errors="ignore")
    except:
        text = base64.b64encode(content).decode("utf-8")
        text = f"[B64:{file.filename}] {text[:2000]}"
    snippet = text[:3000]
    CONV_MEMORY.append({"user": f"[ملف مُتعلم: {file.filename}]", "assistant": f"(حُفظ مقتطف): {snippet}"})
    return {"ok": True, "filename": file.filename, "saved_chars": len(snippet)}

@app.get("/memory")
def memory():
    return JSONResponse({"count": len(CONV_MEMORY), "last": CONV_MEMORY[-3:]})

@app.post("/memory/clear")
def memory_clear():
    CONV_MEMORY.clear()
    return {"ok": True, "message": "تم مسح الذاكرة المؤقتة."}

HTML_HOME = """
<html><head><meta charset='utf-8'><meta name="viewport" content="width=device-width,initial-scale=1">
<title>النواة الذكية – Bassam</title></head>
<body style='font-family:Arial;direction:rtl;text-align:center;margin-top:40px;background:#0f172a;color:#e2e8f0'>
  <h2>🧠 النواة الذكية الاحترافية</h2>
  <p>مرحبًا بك في نواة بسّام — اختر ما تريد:</p>
  <p>
    <a href='/ui/xtream' style='color:#93c5fd;text-decoration:none;font-size:18px'>📺 شاشة Xtream</a> |
    <a href='/docs' style='color:#93c5fd;text-decoration:none;font-size:18px'>🧩 Swagger API</a>
  </p>
</body></html>
"""

HTML_XTREAM = r"""<!doctype html><html lang="ar" dir="rtl"><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>قنوات Xtream – Bassam AI</title>
<style>
 body{font-family:system-ui,Segoe UI,Roboto,Arial;background:#0f172a;color:#e2e8f0;margin:0}
 header{padding:12px 16px;background:#0b1220;border-bottom:1px solid #1f2937}
 main{display:grid;grid-template-columns:320px 1fr;gap:12px;padding:12px}
 @media(max-width:900px){main{display:block}}
 .card{background:#0b1220;border:1px solid #1f2937;border-radius:12px;padding:12px}
 input,button,select{border:1px solid #334155;border-radius:10px;background:#0f172a;color:#e2e8f0;padding:10px}
 .chip{border:1px solid #334155;background:#0f172a;border-radius:999px;padding:7px 10px;margin:4px;display:inline-block;cursor:pointer}
 .chip.active{background:#1d4ed8;border-color:#1d4ed8}
 .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
 video{width:100%;max-height:60vh;background:#000;border-radius:10px;border:1px solid #1f2937}
 .item{display:flex;gap:10px;align-items:center;justify-content:space-between;border:1px solid #1f2937;background:#0b1220;border-radius:10px;padding:10px;margin:6px 0}
 .muted{opacity:.75}
</style></head>
<body>
<header><b>🎯 Xtream</b> <span class="muted">— أدخل بياناتك مرة واحدة</span></header>
<main>
<section class="card">
<h3>الإعدادات</h3>
<div class="row" style="margin-top:8px"><input id="host" placeholder="host:port (مثال mhiptv.info:2095)" style="flex:1"></div>
<div class="row"><input id="user" placeholder="u"><input id="pass" placeholder="p" type="password"><button id="save">حفظ/تحديث</button></div>
<p class="muted" id="status">جاهز</p>
<h3>التصنيفات</h3><div id="cats"></div>
</section>
<section class="card">
<div class="row" style="justify-content:space-between"><h3>المشغل</h3><div class="muted" id="now"></div></div>
<video id="player" controls playsinline></video>
<div class="row" style="margin-top:10px"><input id="q" placeholder="ابحث باسم القناة…" style="flex:1"><select id="sort"><option value="name">الاسم</option><option value="id">المعرّف</option></select></div>
<div id="streams"></div>
</section>
</main>
<script>
const $=id=>document.getElementById(id);
const state={host:localStorage.getItem('xt_host')||'',u:localStorage.getItem('xt_u')||'',p:localStorage.getItem('xt_p')||'',cat:null,all:[]};
$("host").value=state.host;$("user").value=state.u;$("pass").value=state.p;
$("save").onclick=()=>{state.host=$("host").value.trim();state.u=$("user").value.trim();state.p=$("pass").value.trim();localStorage.setItem("xt_host",state.host);localStorage.setItem("xt_u",state.u);localStorage.setItem("xt_p",state.p);loadCats();};
$("q").oninput=render;$("sort").onchange=render;
function setStatus(s){$("status").textContent=s;}
function badge(txt){const s=document.createElement('span');s.className='chip';s.textContent=txt;return s;}
async function loadCats(){if(!(state.host&&state.u&&state.p)){setStatus("أدخل الإعدادات ثم حفظ");$("cats").innerHTML="";$("streams").innerHTML="";return;}setStatus("جلب التصنيفات…");const u=new URLSearchParams({host:state.host,u:state.u,p:state.p});const r=await fetch(`/api/xtream/categories?${u.toString()}`);if(!r.ok){setStatus("تعذّر جلب التصنيفات");return;}const cats=await r.json();$("cats").innerHTML="";cats.forEach(c=>{const b=badge(c.category_name||("#"+c.category_id));b.onclick=()=>selectCat(c.category_id,b);$("cats").appendChild(b);});setStatus("اختر تصنيفًا");}
async function selectCat(catId,btn){[...document.querySelectorAll(".chip")].forEach(e=>e.classList.remove("active"));btn.classList.add("active");state.cat=catId;$("streams").innerHTML="…";const u=new URLSearchParams({host:state.host,u:state.u,p:state.p,category_id:String(catId)});const r=await fetch(`/api/xtream/streams?${u.toString()}`);if(!r.ok){$("streams").innerHTML="فشل تحميل القنوات";return;}state.all=await r.json();render();}
function render(){const q=$("q").value.trim().toLowerCase();const s=$("sort").value;let L=Array.isArray(state.all)?state.all.slice():[];if(q)L=L.filter(x=>(x.name||"").toLowerCase().includes(q));L.sort((a,b)=>s==="id"?(+a.stream_id||0)-(+b.stream_id||0):(a.name||"").localeCompare(b.name||""));$("streams").innerHTML="";L.forEach(x=>{const d=document.createElement("div");d.className="item";const name=document.createElement("div");name.textContent=x.name||("ID "+x.stream_id);name.style.flex="1";const id=document.createElement("small");id.className="muted";id.textContent="#"+x.stream_id;const btn=document.createElement("button");btn.textContent="تشغيل ▶";btn.onclick=()=>play(x.stream_id);d.appendChild(name);d.appendChild(id);d.appendChild(btn);$("streams").appendChild(d);});}
function canHLS(){const v=document.createElement('video');return v.canPlayType('application/vnd.apple.mpegURL')||v.canPlayType('application/x-mpegURL');}
async function play(id){$("now").textContent="تشغيل: #"+id;const m3u8=`/api/xtream/stream/${id}.m3u8?host=${encodeURIComponent(state.host)}&u=${encodeURIComponent(state.u)}&p=${encodeURIComponent(state.p)}`;const ts=`/api/xtream/stream/${id}.ts?host=${encodeURIComponent(state.host)}&u=${encodeURIComponent(state.u)}&p=${encodeURIComponent(state.p)}`;const video=$("player");if(canHLS()){video.src=m3u8;video.play().catch(()=>{});}else{if(!window.Hls){await new Promise((ok,er)=>{const s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/hls.js@latest';s.onload=ok;s.onerror=er;document.head.appendChild(s);});}if(window.Hls&&window.Hls.isSupported()){const hls=new Hls();hls.loadSource(m3u8);hls.attachMedia(video);hls.on(Hls.Events.MANIFEST_PARSED,()=>video.play().catch(()=>{}));}else{video.src=ts;video.play().catch(()=>{});}}}
loadCats();
</script></body></html>
