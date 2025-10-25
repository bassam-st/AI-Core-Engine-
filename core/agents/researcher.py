# core/agents/researcher.py — باحث: بحث DuckDuckGo + قراءة روابط
from __future__ import annotations
from typing import Dict, List
from core.web_search import web_search, fetch_text
from core.crawler import crawl_site

def research(goal: str, extra_urls: list[str] | None = None, k: int = 5) -> dict:
    notes: List[str] = []
    sources: List[Dict] = []

    # نتائج بحث عامة
    results = web_search(goal, max_results=k) or []
    for r in results:
        url = r.get("url")
        txt = fetch_text(url) if url else ""
        if txt:
            notes.append(txt[:2000])
            sources.append({"title": r.get("title",""), "url": url})

    # قراءة الروابط المعطاة + زحف خفيف
    for u in (extra_urls or []):
        for item in crawl_site(u, max_pages=3):
            notes.append(item["text"][:2000])
            sources.append({"title": u, "url": item["url"]})

    # موجز بسيط
    brief = []
    for t in notes:
        for s in t.split("."):
            s = s.strip()
            if 25 < len(s) < 200:
                brief.append(s)
        if len(brief) > 24:
            break
    brief = brief[:24]

    return {"notes": notes, "brief": brief, "sources": sources[:12]}
