import os
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
from .config import cfg

class IntentModel:
    def __init__(self):
        self.model = None
        self.vec = None
        self.labels = []

    def load_or_init(self):
        if os.path.exists(cfg.INTENT_PATH):
            self.vec, self.model, self.labels = joblib.load(cfg.INTENT_PATH)
        else:
            # نموذج بسيط افتراضي
            self.add_examples([
                ("السلام عليكم", "greeting"),
                ("اريد تلخيص هذا", "summarize"),
                ("ابحث في الانترنت", "web_search"),
                ("حلل لي هذا النص", "analyze"),
                ("انشئ لي كود", "code"),
            ])
            self.train()

    def add_examples(self, pairs: List[Tuple[str,str]]):
        if not hasattr(self, "_data"):
            self._data = []
        self._data.extend(pairs)

    def train(self):
        texts = [t for t,_ in self._data]
        ys = [y for _,y in self._data]
        self.labels = sorted(list(set(ys)))
        self.vec = TfidfVectorizer(max_features=20000, ngram_range=(1,2))
        X = self.vec.fit_transform(texts)
        self.model = LogisticRegression(max_iter=200).fit(X, ys)
        joblib.dump((self.vec, self.model, self.labels), cfg.INTENT_PATH)

    def predict(self, text: str) -> str:
        if not self.model:
            self.load_or_init()
        X = self.vec.transform([text])
        return self.model.predict(X)[0]

    def classes(self) -> List[str]:
        return self.labels or []
