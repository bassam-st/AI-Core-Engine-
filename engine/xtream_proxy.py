import os
from urllib.parse import urljoin

XT_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XT_USER = os.getenv("XTREAM_USER", "")
XT_PASS = os.getenv("XTREAM_PASS", "")

def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    """
    صيغة Xtream المعتادة:
    http://host:port/live/<user>/<pass>/<stream_id>.m3u8
    """
    if not (XT_BASE and XT_USER and XT_PASS):
        raise RuntimeError("تأكد من تعيين XTREAM_BASE و XTREAM_USER و XTREAM_PASS في Render أو .env")
    path = f"/live/{XT_USER}/{XT_PASS}/{stream_id}.{ext}"
    # urljoin لسلامة الـ slashes
    return urljoin(XT_BASE + "/", path.lstrip("/"))
