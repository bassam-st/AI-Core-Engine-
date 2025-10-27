import os
from dataclasses import dataclass

@dataclass
class Config:
    ROOT: str = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    CORPUS_DIR: str = os.path.join(DATA_DIR, "corpus")
    DB_PATH: str = os.path.join(DATA_DIR, "memory.db")
    INDEX_DIR: str = os.path.join(DATA_DIR, "index")
    INTENT_PATH: str = os.path.join(DATA_DIR, "intent.joblib")

    GOOGLE_CSE_ID: str = os.environ.get("GOOGLE_CSE_ID", "")
    GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")

cfg = Config()

# تأكد من المجلدات
os.makedirs(cfg.DATA_DIR, exist_ok=True)
os.makedirs(cfg.CORPUS_DIR, exist_ok=True)
os.makedirs(cfg.INDEX_DIR, exist_ok=True)
