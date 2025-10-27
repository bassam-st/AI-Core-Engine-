import os
import requests
from typing import List, Dict

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "").strip()

class WebSearchError(Exception):
    pass

def google_cse_search(query: str, num: int = 5) -> List[Dict]:
    """البحث عبر Google Custom Search API"""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        raise WebSearchError("مفاتيح GOOGLE_API_KEY أو GOOGLE_CSE_ID غير مضبوطة.")

    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": max(1, min(num, 10)),
        "safe": "off",
        "hl": "ar"
    }

    resp = requests.get(endpoint, params=params, timeout=20)
    if resp.status_code != 200:
        raise WebSearchError(f"خطأ في الاتصال بـ Google ({resp.status_code})")

    data = resp.json()
    items = data.get("items", []) or []
    results = []
    for item in items:
        results.append({
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", "")
        })
    return results
