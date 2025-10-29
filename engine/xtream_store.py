# engine/xtream_store.py
from __future__ import annotations
import os, json
from pathlib import Path
from cryptography.fernet import Fernet
from engine.config import cfg

# ضع هذا المفتاح في متغيرات بيئة Render باسم XTREAM_SECRET
SECRET = os.getenv("XTREAM_SECRET")
if not SECRET:
    raise RuntimeError("XTREAM_SECRET env missing. Generate one and set it in Render.")

fernet = Fernet(SECRET.encode())
STORE = Path(cfg.DATA_DIR) / "xtream.enc"

def save_xtream(server: str, username: str, password: str) -> None:
    payload = json.dumps({
        "server": server.strip().rstrip("/"),
        "username": username.strip(),
        "password": password.strip()
    }, ensure_ascii=False).encode()
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_bytes(fernet.encrypt(payload))

def load_xtream() -> dict | None:
    if not STORE.exists():
        return None
    try:
        data = fernet.decrypt(STORE.read_bytes())
        return json.loads(data.decode())
    except Exception:
        return None
