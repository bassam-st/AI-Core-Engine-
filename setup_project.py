import os

# إنشاء المجلدات الأساسية الخاصة بالبيانات
for p in ["data/corpus", "data/index", "data/exports"]:
    os.makedirs(p, exist_ok=True)

# إنشاء ملفات مبدئية حتى لا تظهر أخطاء
for f, txt in [
    ("data/memory.db", "# init\n"),
    ("data/intent.joblib", "# will be created after first training\n"),
]:
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as h:
            h.write(txt)

print("✅ تم تجهيز مجلد data بنجاح.")
