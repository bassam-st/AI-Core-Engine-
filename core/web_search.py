# core/web_search.py — DuckDuckGo + HTML to Text
from __future__ import annotations
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}

def web_search(query: str, max_results: int = 6):
    with DDGS() as ddg:
        results = ddg.text(query, max_results=max_results, region="xa-ar")
    clean = []
    for r in results or []:
        url = r.get("href") or r.get("url")
        title = r.get("title") or (url or "")
        snippet = r.get("body") or r.get("snippet") or ""
        if url:
            clean.append({"title": title, "url": url, "snippet": snippet})
    return clean

def fetch_text(url: str, max_chars: int = 4000) -> str:
    if not url: return ""
    try:
        html = requests.get(url, headers=UA, timeout=12).text
        soup = BeautifulSoup(html, "lxml")
        for s in soup(["script", "style", "noscript"]): s.extract()
        text = " ".join(soup.get_text(" ").split())
        return text[:max_chars]
    except Exception:
        return ""
