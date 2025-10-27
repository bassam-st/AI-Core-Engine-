import os, uuid, requests
from bs4 import BeautifulSoup
from fastapi import UploadFile
from .config import cfg
from .retriever import read_any

class Ingestor:
    def save_and_convert(self, f: UploadFile) -> str:
        ext = os.path.splitext(f.filename or "")[1].lower() or ".txt"
        fname = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(cfg.CORPUS_DIR, fname)
        with open(path, "wb") as out:
            out.write(f.file.read())
        # مجرد حفظ؛ القراءة تتم في retriever
        return path

    def ingest_from_url(self, url: str) -> str:
        r = requests.get(url, timeout=20)
        ct = (r.headers.get("content-type") or "").lower()
        if "text/html" in ct:
            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(" ")
            fname = f"{uuid.uuid4().hex}.txt"
            path = os.path.join(cfg.CORPUS_DIR, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return path
        else:
            # نزّل كما هو (PDF أو غيره)
            ext = ".bin"
            if "pdf" in ct: ext = ".pdf"
            fname = f"{uuid.uuid4().hex}{ext}"
            path = os.path.join(cfg.CORPUS_DIR, fname)
            with open(path, "wb") as f:
                f.write(r.content)
            return path
