# main.py — نواة بحث/تلخيص/ذاكرة + تعلّم ذاتي ويدوي (بدون مفاتيح)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from core.brain import chat_answer
from core.memory import init_db, add_fact, search_memory
from core.learn_loop import run_once as autolearn_run_once

app = FastAPI(title="Al Core Engine — Free Brain")

# Static & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class ChatIn(BaseModel):
    message: str

class LearnIn(BaseModel):
    text: str
    source: str | None = None

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
def api_chat(inp: ChatIn):
    reply, sources = chat_answer(inp.message)
    return {"ok": True, "reply": reply, "sources": sources}

@app.post("/api/learn")
def api_learn(body: LearnIn):
    add_fact(body.text.strip(), body.source or "manual")
    return {"ok": True}

@app.get("/api/memory/search")
def api_memory(q: str):
    hits = search_memory(q, limit=5)
    return {"ok": True, "hits": hits}

@app.post("/api/autolearn/run")
def api_autolearn():
    added = autolearn_run_once()
    return {"ok": True, "added": added}

@app.get("/health")
def health():
    return {"ok": True}
