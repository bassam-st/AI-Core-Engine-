# engine/sports.py
import datetime as dt
import httpx
from bs4 import BeautifulSoup

# محاولة ربط المباراة بالقناة (اختياري)
try:
    from engine.xtream_proxy import build_live_url
    _HAS_XTREAM = True
except Exception:
    _HAS_XTREAM = False
    build_live_url = None  # type: ignore

def _today_iso():
    return dt.date.today().isoformat()

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
        home = _txt(".teamA, .c-team__name")
        away = _txt(".teamB, .c-team__name--away")
        time = _txt(".matchDate, time")
        league = _txt(".tournament, .c-competition")
        if home and away:
            out.append({
                "id": f"fg-{home}-{away}-{time}",
                "home": home, "away": away,
                "time": time, "league": league,
                "source": {"name": "FilGoal", "url": url},
                "streamUrl": None,
            })
    return out

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
        home = _txt(".teamA, .teamA .team")
        away = _txt(".teamB, .teamB .team")
        time = _txt(".time, time")
        league = _txt(".tournament")
        if home and away:
            out.append({
                "id": f"yl-{home}-{away}-{time}",
                "home": home, "away": away,
                "time": time, "league": league,
                "source": {"name": "YallaKora", "url": url},
                "streamUrl": None,
            })
    return out

def _scrape_kooora():
    url = "https://www.kooora.com/?region=-1&day=today"
    r = httpx.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for row in soup.select("table tr"):
        tds = row.select("td")
        if len(tds) >= 5:
            lg = tds[0].get_text(strip=True)
            home = tds[1].get_text(strip=True)
            time = tds[2].get_text(strip=True)
            away = tds[3].get_text(strip=True)
            if home and away:
                out.append({
                    "id": f"kr-{home}-{away}-{time}",
                    "home": home, "away": away,
                    "time": time, "league": lg,
                    "source": {"name": "Kooora", "url": url},
                    "streamUrl": None,
                })
    return out

async def get_today_fixtures(league_filter: str | None = None):
    results = []
    for fn in (_scrape_filgoal, _scrape_yallakora, _scrape_kooora):
        try:
            results.extend(fn())
        except Exception:
            pass

    # إزالة التكرار
    seen = set()
    dedup = []
    for m in results:
        key = (m["home"].lower(), m["away"].lower(), m["time"])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(m)

    if league_filter:
        lf = league_filter.strip().lower()
        dedup = [m for m in dedup if lf in (m["league"] or "").lower()]

    # محاولة ربط بث افتراضي (مثال: beIN 1/2… لو Xtream متوفر)
    if _HAS_XTREAM and build_live_url:
        # قنوات رياضية شائعة — تُعدّل حسب اشتراكك
        guess_ids = {
            "bein": ["22","4905","4906","4907","4908","4909","4910","2391","19"],
            "ssc":  ["60000","60001","60002","60003","60004","60005","60006"],
        }
        for m in dedup:
            # اختصار: إن كان الدوري عربي نحاول beIN أولاً
            target = "bein" if "دوري" in (m["league"] or "") or "كأس" in (m["league"] or "") else "bein"
            ids = guess_ids.get(target, [])
            if ids:
                m["streamUrl"] = build_live_url(ids[0])

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
