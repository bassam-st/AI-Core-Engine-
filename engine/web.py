from __future__ import annotations
import os, requests
from typing import List, Dict
from duckduckgo_search import DDGS

from .config import cfg

def google_cse_search(query: str, num: int = 5) -> List[Dict]:
    cx = cfg.GOOGLE_CSE_ID.strip()
    key = cfg.GOOGLE_API_KEY.strip()
    if not cx or not key:
        return []
    url = "https://www.googleapis.com/customsearch/v1"
    try:
        r = requests.get(url, params={"key": key, "cx": cx, "q": query, "num": num}, timeout=20)
        r.raise_for_status()
        items = r.json().get("items", []) or []
        out = []
        for it in items:
            out.append({
                "title": it.get("title"),
                "href": it.get("link"),
                "body": it.get("snippet"),
            })
        return out
    except Exception:
        return []

def web_search(query: str, max_results: int = 5) -> List[Dict]:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        out = []
        for r in results:
            out.append({"title": r.get("title"), "href": r.get("href"), "snippet": r.get("body")})
        return out
    except Exception:
        return []

def wiki_summary_ar(query: str) -> str:
    try:
        r = requests.get("https://ar.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(query), timeout=15)
        if r.status_code == 200:
            js = r.json()
            return js.get("extract", "") or ""
        return ""
    except Exception:
        return ""
