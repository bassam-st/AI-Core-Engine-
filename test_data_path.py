import os
from engine.config import DATA_DIR

print("📁 مسار مجلد البيانات:", DATA_DIR)
print("📂 المجلد موجود:", os.path.exists(DATA_DIR))
print("📂 المجلد corpus:", os.path.exists(os.path.join(DATA_DIR, "corpus")))
print("📂 المجلد index:", os.path.exists(os.path.join(DATA_DIR, "index")))
print("📂 المجلد exports:", os.path.exists(os.path.join(DATA_DIR, "exports")))
