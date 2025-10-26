from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests, re

def web_search(query: str, max_results: int = 5):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        # توحيد الحقول
        norm = []
        for r in results:
            norm.append({
                "title": r.get("title"),
                "href": r.get("href") or r.get("url"),
                "body": r.get("body") or r.get("snippet")
            })
        return norm
    except Exception:
        return []

def wiki_summary_ar(query: str) -> str:
    # تبسيط: نبحث عن صفحة ويكيبيديا العربية ونقص نصها الأولي
    try:
        q = f"site:ar.wikipedia.org {query}"
        rs = web_search(q, max_results=1)
        if not rs:
            return ""
        url = rs[0].get("href")
        if not url:
            return ""
        html = requests.get(url, timeout=6).text
        soup = BeautifulSoup(html, "html.parser")
        p = soup.select_one("p")
        text = re.sub(r"\[\d+\]", "", (p.get_text(" ") if p else "")).strip()
        return text
    except Exception:
        return ""
