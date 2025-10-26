import os
import glob
import joblib
from typing import List, Dict

from engine.config import cfg
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# تأكد من وجود مسار الفهارس
os.makedirs(cfg.INDEX_DIR, exist_ok=True)


class Retriever:
    """
    مسترجِع محلي يجمع بين BM25 و TF-IDF
    مع معالجة حالة عدم وجود مستندات لتفادي أخطاء القسمة على صفر.
    """

    def __init__(self):
        self.paths: List[str] = []
        self.docs: List[str] = []
        self.bm25: BM25Okapi | None = None
        self.vectorizer: TfidfVectorizer | None = None
        self.X = None
        self._load_or_build()

    # --------- بناء/حفظ/تحميل ---------
    def _scan(self):
        self.paths, self.docs = [], []
        for fp in glob.glob(os.path.join(cfg.CORPUS_DIR, "*.txt")):
            self.paths.append(fp)
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    self.docs.append(f.read())
            except Exception:
                self.docs.append("")

    def _save(self):
        joblib.dump(self.paths, os.path.join(cfg.INDEX_DIR, "paths.pkl"))
        joblib.dump(self.docs, os.path.join(cfg.INDEX_DIR, "docs.pkl"))
        joblib.dump(self.bm25, os.path.join(cfg.INDEX_DIR, "bm25.pkl"))
        if cfg.USE_TFIDF and self.vectorizer is not None and self.X is not None:
            joblib.dump(self.vectorizer, os.path.join(cfg.INDEX_DIR, "tfidf_vec.pkl"))
            joblib.dump(self.X, os.path.join(cfg.INDEX_DIR, "tfidf_X.pkl"))

    def _load(self) -> bool:
        try:
            self.paths = joblib.load(os.path.join(cfg.INDEX_DIR, "paths.pkl"))
            self.docs = joblib.load(os.path.join(cfg.INDEX_DIR, "docs.pkl"))
            self.bm25 = joblib.load(os.path.join(cfg.INDEX_DIR, "bm25.pkl"))
            if cfg.USE_TFIDF:
                self.vectorizer = joblib.load(os.path.join(cfg.INDEX_DIR, "tfidf_vec.pkl"))
                self.X = joblib.load(os.path.join(cfg.INDEX_DIR, "tfidf_X.pkl"))
            return True
        except Exception:
            return False

    def _load_or_build(self):
        if not self._load():
            self.rebuild_index()

    # --------- إعادة بناء الفهرس ---------
    def rebuild_index(self):
        """
        يعيد بناء فهارس BM25 و TF-IDF مع حماية من حالة عدم وجود مستندات.
        """
        self._scan()

        # حماية: إذا لا يوجد أي مستندات، نضع عنصرًا افتراضيًا لتجنّب ZeroDivisionError
        if not self.docs:
            self.docs = [""]
            self.paths = ["(no_docs_placeholder)"]

        # BM25
        tokenized = [d.split() for d in self.docs]
        try:
            self.bm25 = BM25Okapi(tokenized)
        except ZeroDivisionError:
            # لو حدثت قسمة على صفر رغم الحماية، نستخدم توكن وهمي
            self.bm25 = BM25Okapi([["placeholder"]])

        # TF-IDF (اختياري)
        if cfg.USE_TFIDF:
            try:
                self.vectorizer = TfidfVectorizer(max_features=50000, ngram_range=(1, 2))
                self.X = self.vectorizer.fit_transform(self.docs)
            except Exception as e:
                # لا نوقف النظام بسبب فشل بناء TF-IDF
                print("TF-IDF build warning:", e)
                self.vectorizer, self.X = None, None

        self._save()

    # --------- البحث ---------
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        يبحث باستخدام مزيج من BM25 و TF-IDF (إن وُجد)،
        ويُعيد أفضل النتائج مع نص مقتطع (حتى 3000 حرف).
        """
        if not self.docs or not self.bm25:
            return []

        # إذا كانت مجموعة المستندات عبارة عن العنصر الوهمي فقط، لا ترجع نتائج حقيقية
        only_placeholder = len(self.docs) == 1 and self.paths and self.paths[0] == "(no_docs_placeholder)"
        if only_placeholder:
            return []

        # BM25 scores
        try:
            bm_scores = self.bm25.get_scores(query.split())
        except Exception:
            bm_scores = [0.0] * len(self.docs)

        # أفضل مضاعف من top_k من BM25 (لأجل الدمج لاحقاً)
        bm_rank = sorted(enumerate(bm_scores), key=lambda x: x[1], reverse=True)[: max(top_k * 2, 1)]

        # TF-IDF cosine (إن وُجدت)
        tf_scores = []
        if cfg.USE_TFIDF and self.vectorizer is not None and self.X is not None:
            try:
                qv = self.vectorizer.transform([query])
                sims = cosine_similarity(qv, self.X)[0]
                tf_scores = list(enumerate(sims))
            except Exception:
                tf_scores = []

        # دمج خطي بسيط (BM25 أثقل وزنًا)
        scores = {}
        for i, s in bm_rank:
            scores[i] = scores.get(i, 0.0) + (0.6 * float(s))
        for i, s in tf_scores:
            if i in scores:
                scores[i] += 0.4 * float(s)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[: max(top_k, 1)]

        results = []
        for i, s in ranked:
            # حماية القراءة
            try:
                txt = self.docs[i][:3000]
            except Exception:
                txt = ""
            results.append({"path": self.paths[i], "score": float(s), "text": txt})

        return results
