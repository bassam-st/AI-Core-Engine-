# engine/iptv.py
from __future__ import annotations
import httpx, re

# تخزين بسيط في الذاكرة (يمكنك لاحقًا حفظه في ملف/DB)
CHANNELS: list[dict] = []

def parse_m3u(text: str) -> list[dict]:
    # صيغة مبسطة: يبحث عن #EXTINF:-1 tvg-name,Channel Name ثم السطر التالي URL
    lines = text.splitlines()
    out = []
    name = group = ""
    for i,l in enumerate(lines):
        if l.startswith("#EXTINF:"):
            # استخراج الاسم والمجموعة إن وُجدت
            m_name = re.search(r',\s*(.+)$', l)
            m_group = re.search(r'group-title="([^"]+)"', l)
            name  = (m_name.group(1).strip() if m_name else "").strip()
            group = (m_group.group(1).strip() if m_group else "").strip()
            # السطر التالي غالبًا هو الرابط
            if i+1 < len(lines):
                url = lines[i+1].strip()
                if url.startswith("http"):
                    out.append({"name": name, "group": group, "url": url})
    return out

async def load_m3u_from_url(url: str) -> int:
    global CHANNELS
    r = httpx.get(url, timeout=30)
    r.raise_for_status()
    CHANNELS = parse_m3u(r.text)
    return len(CHANNELS)

def find_channel_like(*keywords: str) -> dict | None:
    """يحاول إيجاد قناة بحسب كلمات مفتاحية (غير حسّاسة لحالة الأحرف)."""
    keys = [k.lower() for k in keywords if k]
    for ch in CHANNELS:
        n = (ch["name"] or "").lower()
        if all(k in n for k in keys):
            return ch
    return None
