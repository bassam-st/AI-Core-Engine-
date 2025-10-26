import os, re
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from engine.config import cfg

import requests

try:
    from PyPDF2 import PdfReader
    HAS_PDF = True
except Exception:
    HAS_PDF = False

os.makedirs(cfg.CORPUS_DIR, exist_ok=True)

def _clean_text(s: str) -> str:
    s = re.sub(r'\s+', ' ', s or '')
    return s.strip()

def _safe_name_from_url(url: str, default: str = "doc") -> str:
    p = urlparse(url)
    base = (p.netloc + p.path).replace("/", "_").replace("\\", "_")
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base) or default
    return base[:200]

class Ingestor:
    def save_and_convert(self, upfile) -> str:
        name = upfile.filename
        raw = upfile.file.read()
        dest = Path(cfg.CORPUS_DIR) / name
        with open(dest, "wb") as f:
            f.write(raw)
        return self._bytes_to_textfile(dest, raw)

    def ingest_from_url(self, url: str) -> str:
        url = url.strip()
        if not url.startswith("http"):
            raise ValueError("رابط غير صحيح")
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        content = r.content
        ctype = r.headers.get("content-type", "").lower()

        # اسم ملف آمن
        base = _safe_name_from_url(url)
        dest = Path(cfg.CORPUS_DIR) / base

        # PDF
        if ("pdf" in ctype or url.lower().endswith(".pdf")) and HAS_PDF:
            dest = dest.with_suffix(".pdf")
            with open(dest, "wb") as f:
                f.write(content)
            return self._bytes_to_textfile(dest, content)

        # HTML
        if "html" in ctype or url.lower().endswith((".htm", ".html")):
            dest = dest.with_suffix(".html")
            with open(dest, "wb") as f:
                f.write(content)
            soup = BeautifulSoup(content, "html.parser")
            text = _clean_text(soup.get_text(" "))
            txt = dest.with_suffix(".txt")
            with open(txt, "w", encoding="utf-8") as f:
                f.write(text)
            return str(txt)

        # نص عادي أو أي شيء آخر
        dest = dest.with_suffix(".txt")
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            text = ""
        with open(dest, "w", encoding="utf-8") as f:
            f.write(_clean_text(text))
        return str(dest)

    def _bytes_to_textfile(self, original_path: Path, raw_bytes: bytes) -> str:
        ext = original_path.suffix.lower()
        if ext in [".txt", ".md"]:
            text = raw_bytes.decode("utf-8", errors="ignore")
        elif ext in [".html", ".htm"]:
            soup = BeautifulSoup(raw_bytes, "html.parser")
            text = soup.get_text(" ")
        elif ext == ".pdf" and HAS_PDF:
            try:
                reader = PdfReader(original_path)
                text = " ".join((p.extract_text() or "") for p in reader.pages)
            except Exception:
                text = ""
        else:
            text = raw_bytes.decode("utf-8", errors="ignore")

        text_path = original_path.with_suffix(".txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(_clean_text(text))
        return str(text_path)
