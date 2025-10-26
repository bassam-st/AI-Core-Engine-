import os, re
from pathlib import Path
from bs4 import BeautifulSoup
from engine.config import cfg

try:
    from PyPDF2 import PdfReader
    HAS_PDF = True
except Exception:
    HAS_PDF = False

os.makedirs(cfg.CORPUS_DIR, exist_ok=True)

def _clean_text(s: str) -> str:
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

class Ingestor:
    def save_and_convert(self, upfile) -> str:
        name = upfile.filename
        raw = upfile.file.read()
        dest = Path(cfg.CORPUS_DIR) / name
        with open(dest, "wb") as f:
            f.write(raw)

        ext = dest.suffix.lower()
        if ext in [".txt", ".md"]:
            text = raw.decode("utf-8", errors="ignore")
        elif ext in [".html", ".htm"]:
            soup = BeautifulSoup(raw, "html.parser")
            text = soup.get_text(" ")
        elif ext == ".pdf" and HAS_PDF:
            reader = PdfReader(dest)
            text = " ".join((p.extract_text() or "") for p in reader.pages)
        else:
            text = raw.decode("utf-8", errors="ignore")

        text_path = dest.with_suffix(".txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(_clean_text(text))
        return str(text_path)
