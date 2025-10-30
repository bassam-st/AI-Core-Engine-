# engine/sports.py
import datetime as dt
import httpx
from bs4 import BeautifulSoup

# ⬇️ ربط مع البروكسي الخاص باكستريم (أضفناه سابقًا)
# - build_live_url(stream_id) يولّد رابط m3u8 آمن عبر خادمك
# - find_stream_id_by_teams(home, away, league) يحاول يطابق المباراة بقناة اكستريم
try:
    from engine.xtream_proxy import build_live_url, find_stream_id_by_teams  # اختياري: إذا الملف موجود
except Exception:
    # احتياطي: لو ما أضفت xtream_proxy بعد، نخلي هذه الدوال لا تعمل لكن لا نكسر الصفحة
    def build_live_url(_sid: str) -> str | None:  # type: ignore
        return None
    def find_stream_id_by_teams(_h: str, _a: str, _l: str = "") -> str | None:  # type: ignore
        return None

# -------- أدوات مساعدة --------
def _today_iso():
    return dt.date.today().isoformat()

def _is_live_text(txt: str) -> bool:
    t = (txt or "").strip().lower()
    return any(k in t for k in ["live", "مباشر", "حي", "قيد", "الآن"])

def _norm(s: str) -> str:
    return (s or "").strip()

# -------- مصادر: FilGoal --------
def _scrape_filgoal():
    url = "https://www.filgoal.com/matches"
    r = httpx.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for card in soup.select(".match-card, .c-matches__item"):
        def _txt(sel):
            el = card.select_one(sel)
            return el.get_text(strip=True) if el else ""
        home = _norm(_txt(".teamA, .c-team__name"))
        away = _norm(_txt(".teamB, .c-team__name--away"))
        time = _norm(_txt(".matchDate, time"))
        league = _norm(_txt(".tournament, .c-competition"))
        if home and away:
            out.append({
                "id": f"fg-{home}-{away}-{time}",
                "home": home, "away": away,
                "time": time, "league": league,
                "isLive": _is_live_text(time),
                "source": {"name": "FilGoal", "url": url},
                "streamUrl": None,
            })
    return out

# -------- مصادر: YallaKora --------
def _scrape_yallakora():
    url = "https://www.yallakora.com/match-center"
    r = httpx.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for card in soup.select(".matchCard, .matchCardLi"):
        def _txt(sel):
            el = card.select_one(sel)
            return el.get_text(strip=True) if el else ""
        home = _norm(_txt(".teamA, .teamA .team"))
        away = _norm(_txt(".teamB, .teamB .team"))
        time = _norm(_txt(".time, time"))
        league = _norm(_txt(".tournament"))
        if home and away:
            out.append({
                "id": f"yl-{home}-{away}-{time}",
                "home": home, "away": away,
                "time": time, "league": league,
                "isLive": _is_live_text(time),
                "source": {"name": "YallaKora", "url": url},
                "streamUrl": None,
            })
    return out

# -------- مصادر: Kooora --------
def _scrape_kooora():
    url = "https://www.kooora.com/?region=-1&day=today"
    r = httpx.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for row in soup.select("table tr"):
        tds = row.select("td")
        if len(tds) >= 5:
            lg = _norm(tds[0].get_text(strip=True))
            home = _norm(tds[1].get_text(strip=True))
            time = _norm(tds[2].get_text(strip=True))
            away = _norm(tds[3].get_text(strip=True))
            if home and away:
                out.append({
                    "id": f"kr-{home}-{away}-{time}",
                    "home": home, "away": away,
                    "time": time, "league": lg,
                    "isLive": _is_live_text(time),
                    "source": {"name": "Kooora", "url": url},
                    "streamUrl": None,
                })
    return out

# -------- تجميع + ربط اكستريم --------
async def get_today_fixtures(league_filter: str | None = None):
    # 1) نجمع من 3 مواقع
    results = []
    for fn in (_scrape_filgoal, _scrape_yallakora, _scrape_kooora):
        try:
            results.extend(fn())
        except Exception:
            # نتجاهل أي فشل مصدر واحد عشان الصفحة تظل شغالة
            pass

    # 2) إزالة التكرار
    seen = set()
    dedup = []
    for m in results:
        key = (m["home"].lower(), m["away"].lower(), m["time"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(m)

    # 3) فلترة الدوري (اختياري)
    if league_filter:
        lf = league_filter.strip().lower()
        dedup = [m for m in dedup if lf in (m.get("league") or "").lower()]

    # 4) محاولة إيجاد قناة اكستريم لكل مباراة وإرفاق رابط m3u8 (إن توفر)
    for m in dedup:
        try:
            # يحاول يطابق اسم المباراة مع قناة في اشتراكك
            stream_id = find_stream_id_by_teams(m["home"], m["away"], m.get("league", ""))
            if stream_id:
                # يولّد رابط آمن عبر خادمك (سيُشغَّل داخل مشغّل الويب في /ui/sports_player)
                url = build_live_url(stream_id)
                if url:
                    m["streamId"] = stream_id
                    m["streamUrl"] = url
        except Exception:
            # إن فشل الربط لأي سبب، نترك streamUrl=None بدون كسر الواجهة
            m["streamUrl"] = m.get("streamUrl") or None

    return {
        "date": _today_iso(),
        "count": len(dedup),
        "matches": dedup,
        "sources": [
            {"name": "Kooora", "url": "https://www.kooora.com"},
            {"name": "YallaKora", "url": "https://www.yallakora.com"},
            {"name": "FilGoal", "url": "https://www.filgoal.com"},
        ],
    }
