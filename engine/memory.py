import os, json, time, sqlite3
from typing import List, Tuple
from engine.config import cfg

os.makedirs(cfg.MEM_DIR, exist_ok=True)

def _conn():
    return sqlite3.connect(cfg.DB_PATH)

def init_db():
    con = _conn()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS conversation(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts INTEGER, user_id TEXT, message TEXT, answer TEXT, intent TEXT, sentiment TEXT
    )""")
    con.commit()
    con.close()

class ConversationMemory:
    def add(self, user_id: str, message: str, answer: str, intent: str, sentiment: str):
        con = _conn()
        cur = con.cursor()
        cur.execute("INSERT INTO conversation(ts,user_id,message,answer,intent,sentiment) VALUES(?,?,?,?,?,?)",
                    (int(time.time()), user_id, message, answer, intent, sentiment))
        con.commit()
        con.close()

    def get_context(self, user_id: str, limit: int = 5) -> str:
        con = _conn()
        cur = con.cursor()
        cur.execute("SELECT message, answer FROM conversation WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))
        rows = cur.fetchall()
        con.close()
        parts = []
        for m, a in rows:
            parts.append(f"س: {m}\nج: {a[:300]}")
        return "\n\n".join(reversed(parts))
