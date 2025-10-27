# engine/web_search.py
import os
import requests
from typing import List, Dict

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GOOGLE_CSE_ID  = os.getenv("GOOGLE_CSE_ID", "").strip()

class WebSearchError(Exception):
    pass

def google_cse_search(query: str, num: int = 5) -> List[Dict]:
    """
    يبحث عبر Google Programmable Search Engine ويعيد قائمة نتائج:
    [{ 'title': str, 'link': str, 'snippet': str }]
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        raise WebSearchError("Google API key or CSE ID missing. Set GOOGLE_API_KEY and GOOGLE_CSE_ID.")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": max(1, min(num, 10)),  # حد جوجل 10
        "safe": "off",
        "hl": "ar",  # نتائج عربية قدر الإمكان
    }
    r = requests.get(url, params=params, timeout=20)
    if r.status_code != 200:
        raise WebSearchError(f"Google CSE HTTP {r.status_code}: {r.text[:300]}")

    data = r.json()
    items = data.get("items", []) or []
    results = []
    for it in items:
        results.append({
            "title": it.get("title", ""),
            "link": it.get("link", ""),
            "snippet": it.get("snippet", "") or it.get("htmlSnippet", ""),
        })
    return results
