import sqlite3, os, time
from .config import cfg

def init_db():
    os.makedirs(cfg.DATA_DIR, exist_ok=True)
    con = sqlite3.connect(cfg.DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memory(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT, msg TEXT, answer TEXT, intent TEXT, sentiment TEXT, ts REAL
    )""")
    con.commit(); con.close()

class ConversationMemory:
    def add(self, user_id: str, msg: str, answer: str, intent: str, sentiment: str):
        con = sqlite3.connect(cfg.DB_PATH)
        con.execute("INSERT INTO memory(user_id,msg,answer,intent,sentiment,ts) VALUES(?,?,?,?,?,?)",
                    (user_id, msg, answer, intent, sentiment, time.time()))
        con.commit(); con.close()

    def all(self, limit: int = 200):
        con = sqlite3.connect(cfg.DB_PATH)
        cur = con.execute("SELECT user_id,msg,answer,intent,sentiment,ts FROM memory ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall(); con.close()
        return rows
