import os, json, joblib
from typing import List, Tuple
from engine.config import cfg
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

os.makedirs(cfg.INTENT_DIR, exist_ok=True)

DEFAULT_CLASSES = [
    "بحث","تلخيص","تحليل","توليد_نص","سؤال_معرفي","أمر_تنفيذي","تحويل_ملف","مساعدة_تقنية"
]

class IntentModel:
    def __init__(self):
        self.v_path = os.path.join(cfg.INTENT_DIR, "vec.pkl")
        self.m_path = os.path.join(cfg.INTENT_DIR, "clf.pkl")
        self.d_path = os.path.join(cfg.INTENT_DIR, "data.jsonl")
        self.vectorizer = None
        self.clf = None
        self._load_or_init()

    def _bootstrap(self):
        X = [
            "ابحث لي عن", "دور على", "اعطني مصادر",            # بحث
            "لخص", "اعمل ملخص", "خلاصة",                       # تلخيص
            "حلل", "قيم", "قارن",                              # تحليل
            "اكتب لي", "انشئ نص", "صياغة",                      # توليد
            "ما هو", "من هو", "كم",                            # سؤال معرفي
            "نفّذ", "شغل", "ابدأ",                             # أمر تنفيذي
            "حوّل لبي دي اف", "استخرج صفحة", "قسّم ملف",        # تحويل ملف
            "لا يعمل التطبيق", "مشكلة في ريندر", "اعدادات",     # مساعدة تقنية
        ]
        y = [
            "بحث","بحث","بحث",
            "تلخيص","تلخيص","تلخيص",
            "تحليل","تحليل","تحليل",
            "توليد_نص","توليد_نص","توليد_نص",
            "سؤال_معرفي","سؤال_معرفي","سؤال_معرفي",
            "أمر_تنفيذي","أمر_تنفيذي","أمر_تنفيذي",
            "تحويل_ملف","تحويل_ملف","تحويل_ملف",
            "مساعدة_تقنية","مساعدة_تقنية","مساعدة_تقنية",
        ]
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=40000)
        Xv = self.vectorizer.fit_transform(X)
        self.clf = LogisticRegression(max_iter=400).fit(Xv, y)

    def _load_or_init(self):
        if os.path.exists(self.v_path) and os.path.exists(self.m_path):
            self.vectorizer = joblib.load(self.v_path)
            self.clf = joblib.load(self.m_path)
        else:
            self._bootstrap()
            joblib.dump(self.vectorizer, self.v_path)
            joblib.dump(self.clf, self.m_path)

    def predict(self, text: str) -> str:
        Xv = self.vectorizer.transform([text])
        return self.clf.predict(Xv)[0]

    def add_examples(self, pairs: List[Tuple[str, str]]):
        with open(self.d_path, "a", encoding="utf-8") as f:
            for t, lab in pairs:
                f.write(json.dumps({"text": t, "label": lab}, ensure_ascii=False) + "\n")

    def train(self):
        texts, labels = [], []
        if os.path.exists(self.d_path):
            with open(self.d_path, "r", encoding="utf-8") as f:
                for line in f:
                    obj = json.loads(line)
                    texts.append(obj["text"])
                    labels.append(obj["label"])
        if not texts:
            return
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=50000)
        Xv = self.vectorizer.fit_transform(texts)
        self.clf = LogisticRegression(max_iter=600).fit(Xv, labels)
        joblib.dump(self.vectorizer, self.v_path)
        joblib.dump(self.clf, self.m_path)

    def classes(self):
        return list(set(DEFAULT_CLASSES))
