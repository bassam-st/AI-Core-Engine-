# core/web_search.py — DuckDuckGo + HTML→نص مع تحمّل Ratelimit
from __future__ import annotations
from duckduckgo_search import DDGS
import requests, time, random
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}

def web_search(query: str, max_results: int = 6, retries: int = 2):
    """بحث آمن: عند الحظر يرجّع قائمة فاضية بدل رفع استثناء."""
    for attempt in range(retries + 1):
        try:
            region = random.choice(["xa-ar","sa-ar","us-en"])
            with DDGS() as ddg:
                results = ddg.text(query, max_results=max_results, region=region)
            clean = []
            for r in results or []:
                url = r.get("href") or r.get("url")
                if not url: 
                    continue
                title = r.get("title") or url
                snippet = r.get("body") or r.get("snippet") or ""
                clean.append({"title": title, "url": url, "snippet": snippet})
            return clean
        except Exception:
            # مهلة بسيطة ثم إعادة المحاولة
            if attempt < retries:
                time.sleep(1.2 + attempt*0.8)
                continue
            return []  # فشل نهائي: نرجّع فاضي بدون استثناء

def fetch_text(url: str, max_chars: int = 4000) -> str:
    if not url: 
        return ""
    try:
        html = requests.get(url, headers=UA, timeout=12).text
        soup = BeautifulSoup(html, "lxml")
        for s in soup(["script","style","noscript"]):
            s.extract()
        text = " ".join(soup.get_text(" ").split())
        return text[:max_chars]
    except Exception:
        return ""
