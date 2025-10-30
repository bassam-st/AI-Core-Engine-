# engine/xtream_proxy.py
import os
import re
from urllib.parse import urljoin
import httpx

# إعدادات Xtream من البيئة (.env أو Render)
XTREAM_BASE = os.getenv("XTREAM_BASE", "").rstrip("/")
XTREAM_USER = os.getenv("XTREAM_USER", "")
XTREAM_PASS = os.getenv("XTREAM_PASS", "")

# ⚙️ إنشاء رابط البث المباشر (m3u8)
def build_live_url(stream_id: int | str, ext: str = "m3u8") -> str:
    """
    يبني رابط بث مباشر بصيغة:
    http://host:port/live/user/pass/stream_id.m3u8
    """
    if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
        raise RuntimeError("⚠️ لم يتم ضبط متغيرات XTREAM_BASE / USER / PASS")
    path = f"/live/{XTREAM_USER}/{XTREAM_PASS}/{stream_id}.{ext}"
    return urljoin(XTREAM_BASE + "/", path.lstrip("/"))


# 🧠 دالة ذكية للبحث عن stream_id للقناة المطابقة لاسم المباراة
def find_stream_id_by_teams(home: str, away: str, league: str = "") -> str | None:
    """
    يحاول مطابقة أسماء الفرق أو الدوري مع القنوات داخل اشتراك Xtream.
    يعيد stream_id عند العثور على قناة مناسبة.
    """
    try:
        if not (XTREAM_BASE and XTREAM_USER and XTREAM_PASS):
            return None

        api_url = f"{XTREAM_BASE}/player_api.php?username={XTREAM_USER}&password={XTREAM_PASS}"
        r = httpx.get(api_url, timeout=10)
        r.raise_for_status()
        data = r.json()

        channels = []
        if "available_channels" in data:
            channels = data["available_channels"]
        elif "live" in data:
            for cat in data["live"].values():
                channels.extend(cat)

        # قائمة كلمات مفتاحية لتطابق الأسماء (تحويل للأحرف الصغيرة للمقارنة)
        q_words = [home.lower(), away.lower(), league.lower()]
        q_words = [w for w in q_words if w and len(w) > 2]

        # البحث عن قناة تحتوي أي كلمة مطابقة
        for ch in channels:
            name = str(ch.get("name", "")).lower()
            for w in q_words:
                if w in name:
                    return str(ch.get("stream_id"))

    except Exception as e:
        print("find_stream_id_by_teams error:", e)

    return None
