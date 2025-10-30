# engine/ingest.py
import os
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any
import mimetypes

# مجلد تخزين البيانات
DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTS = {".txt", ".md", ".pdf", ".json", ".csv"}

def _read_file_content(path: Path) -> str:
    """قراءة محتوى الملف النصي أو PDF أو JSON أو CSV."""
    ext = path.suffix.lower()
    try:
        if ext in (".txt", ".md"):
            return path.read_text(encoding="utf-8", errors="ignore")
        elif ext == ".json":
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif ext == ".csv":
            return path.read_text(encoding="utf-8", errors="ignore")
        elif ext == ".pdf":
            # قراءة نصوص PDF إن وُجدت مكتبة PyPDF2
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(str(path))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                return f"[PDF File: {path.name}] (لم يتمكن من قراءة النصوص)"
        else:
            return f"[Unsupported file type: {path.suffix}]"
    except Exception as e:
        return f"[Error reading file {path.name}: {e}]"


def ingest_file(upload_path: str) -> Dict[str, Any]:
    """
    معالجة ملف واحد وإضافته إلى مجلد البيانات الداخلية للنواة.
    """
    p = Path(upload_path)
    if not p.exists():
        return {"ok": False, "error": f"الملف غير موجود: {p}"}

    dest = UPLOADS_DIR / p.name
    shutil.copy(p, dest)

    content = _read_file_content(dest)
    record = {
        "filename": dest.name,
        "size_kb": round(dest.stat().st_size / 1024, 2),
        "ext": dest.suffix,
        "content_preview": content[:500],
    }

    index_path = UPLOADS_DIR / "index.json"
    all_files = []
    if index_path.exists():
        try:
            all_files = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            all_files = []

    all_files.append(record)
    index_path.write_text(json.dumps(all_files, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"ok": True, "added": record}


def ingest_folder(folder_path: str) -> Dict[str, Any]:
    """
    إضافة كل الملفات النصية داخل مجلد دفعة واحدة.
    """
    folder = Path(folder_path)
    if not folder.exists():
        return {"ok": False, "error": f"المجلد غير موجود: {folder}"}

    added = []
    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTS:
            result = ingest_file(str(file))
            if result.get("ok"):
                added.append(result["added"])

    return {"ok": True, "count": len(added), "files": added}


def list_ingested_files() -> List[Dict[str, Any]]:
    """عرض جميع الملفات المضافة للنواة."""
    index_path = UPLOADS_DIR / "index.json"
    if not index_path.exists():
        return []
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        return []


if __name__ == "__main__":
    print(json.dumps(list_ingested_files(), ensure_ascii=False, indent=2))
