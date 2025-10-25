from __future__ import annotations
import os, sqlite3, time, re
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
            added_at INTEGER,
            quality_score REAL DEFAULT 1.0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conv(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_msg TEXT, bot_msg TEXT, ts INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories(
            fact_id INTEGER,
            category TEXT,
            FOREIGN KEY(fact_id) REFERENCES facts(id)
        )
    """)
    con.commit(); con.close()
    _rebuild_index()

def _enhanced_normalize(s: str) -> str:
    s = (s or "").strip().lower()
    repl = {"أ":"ا", "إ":"ا", "آ":"ا", "ة":"ه", "ى":"ي", "ـ":""}
    for k, v in repl.items():
        s = s.replace(k, v)
    s = re.sub(r'[^\w\s]', ' ', s)
    words = [w for w in s.split() if w not in _AR_STOP and len(w) > 1]
    return " ".join(words)

def _rebuild_index():
    global _memory_cache, _bm25
    con = _connect(); cur = con.cursor()
    cur.execute("SELECT id, text, COALESCE(source,'') FROM facts ORDER BY id DESC")
    rows = cur.fetchall(); con.close()
    _memory_cache = [{"id": r[0], "text": r[1], "source": r[2]} for r in rows]
    if _memory_cache:
        corpus = [_enhanced_normalize(x["text"]) for x in _memory_cache]
        _bm25 = BM25Okapi([c.split() for c in corpus])
    else:
        _bm25 = None

def add_fact(text: str, source: str | None = None):
    if not text: return
    quality = _calculate_fact_quality(text)
    con = _connect(); cur = con.cursor()
    cur.execute("INSERT INTO facts(text, source, added_at, quality_score) VALUES(?,?,?,?)",
                (text, source, int(time.time()), quality))
    con.commit(); con.close()
    _rebuild_index()

def _calculate_fact_quality(text: str) -> float:
    if len(text) < 30: return 0.1
    if any(word in text for word in ["إعلان", "اشتراك", "تسجيل", "انقر هنا"]): return 0.1
    
    score = 0.0
    if "." in text: score += 0.3
    if any(char.isdigit() for char in text): score += 0.2
    if len(text.split()) > 8: score += 0.3
    if len(text) > 100: score += 0.2
    
    return min(score, 1.0)

def save_conv(user_msg: str, bot_msg: str):
    con = _connect(); cur = con.cursor()
    cur.execute("INSERT INTO conv(user_msg, bot_msg, ts) VALUES(?,?,?)",
                (user_msg, bot_msg, int(time.time())))
    con.commit(); con.close()

def search_memory(q: str, limit: int = 5) -> List[Dict]:
    if not _bm25 or not _memory_cache:
        return []
    norm_q = _enhanced_normalize(q)
    if not norm_q:
        return []
    scores = _bm25.get_scores(norm_q.split())
    ranked = sorted(zip(_memory_cache, scores), key=lambda t: t[1], reverse=True)
    out = []
    for item, sc in ranked[:limit*2]:  # جلب المزيد للتصفية
        if sc > 0.1:  # تصفية النتائج الضعيفة
            out.append({"id": item["id"], "text": item["text"], "source": item["source"], "score": float(sc)})
    return out[:limit]

def manage_memory_size(max_facts: int = 10000):
    con = _connect(); cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM facts")
    count = cur.fetchone()[0]
    
    if count > max_facts:
        cur.execute("""
            DELETE FROM facts 
            WHERE id IN (
                SELECT id FROM facts 
                ORDER BY added_at ASC 
                LIMIT ?
            )
        """, (count - max_facts,))
        con.commit()
        _rebuild_index()
    con.close()

def get_recent_conversations(limit: int = 10):
    con = _connect(); cur = con.cursor()
    cur.execute("SELECT user_msg, bot_msg FROM conv ORDER BY id DESC LIMIT ?", (limit,))
    results = cur.fetchall()
    con.close()
    return [{"user": r[0], "bot": r[1]} for r in results]
