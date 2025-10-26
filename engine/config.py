import os

class cfg:
    ROOT = os.path.dirname(os.path.dirname(__file__))
    # على Render نستخدم المسار الثابت من env، محليًا نستخدم data/
    DATA_DIR = os.environ.get("ENGINE_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
    CORPUS_DIR = os.path.join(DATA_DIR, "corpus")
    INDEX_DIR  = os.path.join(DATA_DIR, "index")
    INTENT_DIR = os.path.join(DATA_DIR, "intents")
    MEM_DIR    = os.path.join(DATA_DIR, "memory")

    DB_PATH    = os.environ.get("ENGINE_DB", os.path.join(DATA_DIR, "engine.db"))

    # مفاتيح التفعيل الداخلية
    USE_TFIDF = True     # بجانب BM25
    SUM_SENTENCES = 8    # عدد جمل التلخيص
