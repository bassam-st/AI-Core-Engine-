# core/memory.py — ذاكرة محلية مع فهرسة BM25
from __future__ import annotations
import os, sqlite3, time
from typing import List, Dict
from rank_bm25 import BM25Okapi

DB_PATH = os.environ.get("BASSAM_DB", "bassam.db")

_AR_STOP = set("""
و في على من مع عن الى إلى أو أم ثم بل قد لقد كان كانت كانوا كن كنت كنتن يكون تكون تكونون تكونن هذا هذه ذلك تلك هناك هنا حيث كذلك كما كيف لماذا لما إن أن إنما أنما ألا إلا ما لا لم لن هل جدا جداً فقط أيضا أيضًا أي أيًّا أيها التي الذي الذين اللذان اللتان اللواتي اللائي أولئك هؤلاء حين عندما بينما أثناء بسبب لدى ضمن دون غير بين قبل بعد منذ حتى خلال فوق تحت أمام وراء لذلك لهذا لذا لأن كي لكي إذ إذا إلا إنّ أنّ ألا
""".split())

_memory_cache: List[Dict] = []
_bm25 = None

def _connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = _connect(); cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS facts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            source TEXT,
            added_at INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conv(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_msg TEXT, bot_msg TEXT, ts INTEGER
        )
    """)
    con.commit(); con.close()
    _rebuild_index()

def _normalize(s: str) -> str:
    s = (s or "").strip()
    repl = {"أ":"ا","إ":"ا","آ":"ا","ة":"ه","ى":"ي"}
    for k,v in repl.items():
        s = s.replace(k,v)
    return " ".join(w for w in s.split() if w not in _AR_STOP)

def _rebuild_index():
    global _memory_cache, _bm25
    con = _connect(); cur = con.cursor()
    cur.execute("SELECT id, text, COALESCE(source,'') FROM facts ORDER BY id DESC")
    rows = cur.fetchall(); con.close()
    _memory_cache = [{"id": r[0], "text": r[1], "source": r[2]} for r in rows]
    if _memory_cache:
        corpus = [_normalize(x["text"]) for x in _memory_cache]
        _bm25 = BM25Okapi([c.split() for c in corpus])
    else:
        _bm25 = None

def add_fact(text: str, source: str | None = None):
    if not text: return
    con = _connect(); cur = con.cursor()
    cur.execute("INSERT INTO facts(text, source, added_at) VALUES(?,?,?)",
                (text, source, int(time.time())))
    con.commit(); con.close()
    _rebuild_index()

def save_conv(user_msg: str, bot_msg: str):
    con = _connect(); cur = con.cursor()
    cur.execute("INSERT INTO conv(user_msg, bot_msg, ts) VALUES(?,?,?)",
                (user_msg, bot_msg, int(time.time())))
    con.commit(); con.close()

def search_memory(q: str, limit: int = 5) -> List[Dict]:
    if not _bm25 or not _memory_cache:
        return []
    norm_q = _normalize(q)
    if not norm_q:
        return []
    scores = _bm25.get_scores(norm_q.split())
    ranked = sorted(zip(_memory_cache, scores), key=lambda t: t[1], reverse=True)
    out = []
    for item, sc in ranked[:limit]:
        out.append({"id": item["id"], "text": item["text"], "source": item["source"], "score": float(sc)})
    return out
