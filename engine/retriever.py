import os, glob, math, joblib
from typing import List, Dict
from engine.config import cfg
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

os.makedirs(cfg.INDEX_DIR, exist_ok=True)

class Retriever:
    def __init__(self):
        self.paths: List[str] = []
        self.docs: List[str] = []
        self.bm25 = None
        self.vectorizer = None
        self.X = None
        self._load_or_build()

    def _scan(self):
        self.paths, self.docs = [], []
        for fp in glob.glob(os.path.join(cfg.CORPUS_DIR, "*.txt")):
            self.paths.append(fp)
            with open(fp, "r", encoding="utf-8") as f:
                self.docs.append(f.read())

    def _save(self):
        joblib.dump(self.paths, os.path.join(cfg.INDEX_DIR, "paths.pkl"))
        joblib.dump(self.docs,  os.path.join(cfg.INDEX_DIR, "docs.pkl"))
        joblib.dump(self.bm25,  os.path.join(cfg.INDEX_DIR, "bm25.pkl"))
        if cfg.USE_TFIDF and self.vectorizer is not None:
            joblib.dump(self.vectorizer, os.path.join(cfg.INDEX_DIR, "tfidf_vec.pkl"))
            joblib.dump(self.X,         os.path.join(cfg.INDEX_DIR, "tfidf_X.pkl"))

    def _load(self) -> bool:
        try:
            self.paths = joblib.load(os.path.join(cfg.INDEX_DIR, "paths.pkl"))
            self.docs  = joblib.load(os.path.join(cfg.INDEX_DIR, "docs.pkl"))
            self.bm25  = joblib.load(os.path.join(cfg.INDEX_DIR, "bm25.pkl"))
            if cfg.USE_TFIDF:
                self.vectorizer = joblib.load(os.path.join(cfg.INDEX_DIR, "tfidf_vec.pkl"))
                self.X         = joblib.load(os.path.join(cfg.INDEX_DIR, "tfidf_X.pkl"))
            return True
        except Exception:
            return False

    def _load_or_build(self):
        if not self._load():
            self.rebuild_index()

    def rebuild_index(self):
        self._scan()
        # BM25
        tokenized = [d.split() for d in self.docs] if self.docs else [[]]
        self.bm25 = BM25Okapi(tokenized) if self.docs else BM25Okapi([[]])
        # TF-IDF اختياري
        if cfg.USE_TFIDF:
            self.vectorizer = TfidfVectorizer(max_features=50000, ngram_range=(1,2))
            self.X = self.vectorizer.fit_transform(self.docs or [""])
        self._save()

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self.docs:
            return []
        # BM25
        bm_scores = self.bm25.get_scores(query.split())
        bm_rank = sorted(enumerate(bm_scores), key=lambda x: x[1], reverse=True)[:top_k*2]
        # TF-IDF (اندماج بسيط)
        tf_scores = []
        if cfg.USE_TFIDF and self.vectorizer is not None:
            qv = self.vectorizer.transform([query])
            sims = cosine_similarity(qv, self.X)[0]
            tf_scores = list(enumerate(sims))
        # دمج
        scores = {}
        for i, s in bm_rank:
            scores[i] = scores.get(i, 0) + (0.6 * s)
        for i, s in tf_scores:
            if i in scores:
                scores[i] += 0.4 * s
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        results = []
        for i, s in ranked:
            txt = self.docs[i][:3000]
            results.append({"path": self.paths[i], "score": float(s), "text": txt})
        return results
