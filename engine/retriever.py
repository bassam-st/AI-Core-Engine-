import os
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

ALLOWED_EXT = {".txt", ".md"}

def _read_text(path: Path) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        try:
            with open(path, "r", encoding="cp1256", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

class Retriever:
    def __init__(self, index_dir: str, corpus_dir: str):
        self.index_dir = Path(index_dir)
        self.corpus_dir = Path(corpus_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_dir / "tfidf.joblib"
        self.vectorizer = None
        self.matrix = None
        self.paths: List[Path] = []

    def is_ready(self) -> bool:
        return self.index_file.exists()

    def build(self):
        docs, self.paths = [], []
        for p in self.corpus_dir.rglob("*"):
            if p.suffix.lower() in ALLOWED_EXT:
                txt = _read_text(p).strip()
                if txt:
                    docs.append(txt)
                    self.paths.append(p)
        if not docs:
            self.vectorizer = TfidfVectorizer()
            self.matrix = self.vectorizer.fit_transform([""])
            joblib.dump((self.vectorizer, self.matrix, self.paths), self.index_file)
            return
        self.vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1,2), min_df=1, max_df=0.9)
        self.matrix = self.vectorizer.fit_transform(docs)
        joblib.dump((self.vectorizer, self.matrix, self.paths), self.index_file)

    def _ensure_loaded(self):
        if self.vectorizer is None or self.matrix is None:
            if self.index_file.exists():
                self.vectorizer, self.matrix, self.paths = joblib.load(self.index_file)
            else:
                self.build()

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        if not self.matrix or not self.vectorizer: return []
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix).ravel()
        idxs = sims.argsort()[::-1][:k]
        results = []
        for i in idxs:
            path = str(self.paths[i])
            score = float(sims[i])
            snippet = _read_text(Path(path))[:400]
            results.append({"path": path, "score": score, "snippet": snippet})
        return results
