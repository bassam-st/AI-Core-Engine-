from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
import os
from pathlib import Path

from engine.retriever import Retriever
from engine.generator import AnswerSynthesizer

APP_DIR = Path(__file__).parent.resolve()
DATA_DIR = APP_DIR / "data"
CORPUS_DIR = DATA_DIR / "corpus"
UPLOADS_DIR = DATA_DIR / "uploads"
OWNER_PIN = os.environ.get("OWNER_PIN", "bassam1234")

CORPUS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI Core Engine - Bassam Edition")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

retriever = Retriever(index_dir=str(DATA_DIR / "index"), corpus_dir=str(CORPUS_DIR))
synth = AnswerSynthesizer()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask(payload: Dict[str, Any]):
    q = (payload or {}).get("q") or ""
    if not q.strip():
        raise HTTPException(status_code=400, detail="السؤال فارغ")
    if not retriever.is_ready():
        retriever.build()
    hits = retriever.search(q, k=5)
    answer, used = synth.compose_answer(q, hits)
    meta = {"intent": "qa_local" if hits else "web_search", "sentiment": "neutral", "sources": [h["path"] for h in used]}
    return {"answer": answer, "meta": meta}

@app.post("/api/ingest/upload")
async def ingest_upload(file: UploadFile = File(...), owner_pin: Optional[str] = Header(default=None, alias="X-Owner-Pin")):
    if not OWNER_PIN or owner_pin != OWNER_PIN:
        raise HTTPException(status_code=401, detail="غير مصرّح: المالك فقط")
    out_path = CORPUS_DIR / file.filename
    with open(out_path, "wb") as f:
        f.write(await file.read())
    try:
        retriever.build()
    except Exception:
        pass
    return {"ok": True, "saved": str(out_path)}
