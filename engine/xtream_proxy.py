# engine/xtream_proxy.py
from __future__ import annotations
import os
from urllib.parse import urljoin
import httpx

# ===== إعدادات Xtream من البيئة (.env أو Render) =====
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER = os.getenv("XTREAM_USER", "")
XTREAM_PASS = os.getenv("XTREAM_PASS", "")

def _assert_cfg() -> None:
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise RuntimeError("XTREAM_BASE/USER/PASS غير مضبوطة في البيئة")

def _api(action: str | None = None, **params) -> dict | list:
    """استدعاء player_api.php مع الأكشن المطلوب وإرجاع JSON."""
    _assert_cfg()
    base = f"{XTREAM_BASE}/player_api.php?username={XTREAM_USER}&password={XTREAM_PASS}"
    if action:
        base += f"&action={action}"
    if params:
        extra = "&" + "&".join(f"{k}={v}" for k, v in params.items())
        base += extra
    r = httpx.get(base, timeout=20)
    r.raise_for_status()
    return r.json()

# ===== معلومات الحساب/السيرفر =====
def get_info() -> dict:
    """يعيد user_info و server_info للتحقق من الاتصال وعدد الاتصالات…"""
    return _api()

# ===== القنوات الحية =====
def get_channels() -> list[dict]:
    """
    يعيد قائمة القنوات الحية بصيغة Xtream القياسية.
    كل عنصر يحتوي على: name, stream_id, category_id, stream_type, stream_icon …
    """
    data = _api("get_live_streams")
    # API يعيد قائمة مباشرة
    if isinstance(data, list):
        return data
    # بعض البانلات تعيدها داخل مفاتيح أخرى
    for k in ("live", "available_channels", "channels"):
        if k in data and isinstance(data[k], list):
            return data[k]
    return []

def get_categories() -> list[dict]:
    """تصنيفات القنوات (اختياري للفلترة في الواجهة)."""
    try:
        data = _api("get_live_categories")
        return data if isinstance(data, list) else []
    except Exception:
        return []

# ===== بناء روابط التشغيل =====
def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    """
    http(s)://host:port/live/<user>/<pass>/<stream_id>.<ext>
    مثال: m3u8 أو ts
    """
    _assert_cfg()
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))

# ===== بحث ذكي بالقنوات (بالفرق/الدوري) =====
def find_stream_id_by_teams(home: str, away: str, league: str = "") -> str | None:
    """
    يحاول مطابقة أسماء (home/away/league) مع أسماء القنوات ويعيد stream_id عند نجاح المطابقة.
    """
    try:
        words = [w.strip().lower() for w in (home, away, league) if w and len(w.strip()) > 1]
        chans = get_channels()
        for ch in chans:
            name = str(ch.get("name", "")).lower()
            if any(w in name for w in words):
                return str(ch.get("stream_id"))
    except Exception as e:
        print("find_stream_id_by_teams error:", e)
    return None

# ===== بحث نصّي بسيط =====
def search_channels(query: str = "", category_id: str | None = None) -> list[dict]:
    """بحث نصي داخل القنوات مع فلترة اختيارية بالتصنيف."""
    q = (query or "").strip().lower()
    chans = get_channels()
    if category_id:
        chans = [c for c in chans if str(c.get("category_id")) == str(category_id)]
    if not q:
        return chans
    return [c for c in chans if q in str(c.get("name", "")).lower()]
