from __future__ import annotations
import os, glob, re
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from pypdf import PdfReader
from docx import Document
from bs4 import BeautifulSoup

from .config import cfg

def _read_txt(p): 
    with open(p, "r", encoding="utf-8", errors="ignore") as f: 
        return f.read()

def _read_pdf(p):
    try:
        reader = PdfReader(p); return "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception: 
        return ""

def _read_docx(p):
    try:
        doc = Document(p); return "\n".join([p.text for p in doc.paragraphs])
    except Exception: 
        return ""

def _read_html(p):
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            return soup.get_text(" ")
    except Exception:
        return ""

def read_any(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".txt", ".md"]: return _read_txt(path)
    if ext in [".pdf"]: return _read_pdf(path)
    if ext in [".docx"]: return _read_docx(path)
    if ext in [".html", ".htm"]: return _read_html(path)
    return ""

class Retriever:
    def __init__(self):
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self.paths: List[str] = []

    def corpus_files(self) -> List[str]:
        exts = ["*.txt","*.md","*.pdf","*.docx","*.html","*.htm"]
        files = []
        for e in exts:
            files += glob.glob(os.path.join(cfg.CORPUS_DIR, e))
        return sorted(set(files))

    def rebuild_index(self):
        self.paths = self.corpus_files()
        texts = [read_any(p) for p in self.paths]
        self.vectorizer = TfidfVectorizer(max_features=40000, ngram_range=(1,2))
        if texts:
            self.matrix = self.vectorizer.fit_transform(texts)
            joblib.dump((self.vectorizer, self.matrix, self.paths), os.path.join(cfg.INDEX_DIR, "tfidf.joblib"))
        else:
            self.matrix = None

    def _load_if_exists(self):
        f = os.path.join(cfg.INDEX_DIR, "tfidf.joblib")
        if self.vectorizer is None and os.path.exists(f):
            self.vectorizer, self.matrix, self.paths = joblib.load(f)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        self._load_if_exists()
        if not self.vectorizer or self.matrix is None or not self.paths:
            return []
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix)[0]
        idx = sims.argsort()[::-1][:top_k]
        results = []
        for i in idx:
            text = read_any(self.paths[i])
            results.append({"path": os.path.basename(self.paths[i]), "text": text[:3000], "score": float(sims[i])})
        return results
