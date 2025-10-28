# engine/web_agent.py
from __future__ import annotations
import re, html, time
from typing import List, Dict, Tuple, Optional
import requests
from bs4 import BeautifulSoup

try:
    from duckduckgo_search import DDGS
except Exception:
    DDGS = None  # اختياري

from .web import google_cse_search  # يستخدم مفاتيح GOOGLE_... إن وُجدت

USER_AGENT = "BassamWebAgent/1.0 (+https://render.com)"
HEADERS = {"User-Agent": USER_AGENT, "Accept-Language": "ar,en;q=0.8"}

_URL = re.compile(r"https?://[^\s\]]+")

def _clean_text(t: str) -> str:
    t = html.unescape(t or "")
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _fetch_text(url: str, timeout: int = 15) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code != 200 or "text/html" not in r.headers.get("content-type",""):
            return ""
        soup = BeautifulSoup(r.text, "html.parser")
        # إزالة سكربت/ستايل
        for tag in soup(["script", "style", "noscript"]): tag.decompose()
        txt = soup.get_text(" ")
        return _clean_text(txt)[:8000]  # حد أمان
    except Exception:
        return ""

def _ddg_search(query: str, max_results: int = 5) -> List[Dict]:
    if DDGS is None:
        return []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        out = []
        for r in results:
            out.append({
                "title": r.get("title",""),
                "link": r.get("href") or r.get("link") or "",
                "snippet": r.get("body") or r.get("snippet") or ""
            })
        return out
    except Exception:
        return []

def wiki_summary_ar(query: str) -> str:
    try:
        endpoint = "https://ar.wikipedia.org/api/rest_v1/page/summary/"
        r = requests.get(endpoint + requests.utils.quote(query), headers=HEADERS, timeout=12)
        if r.status_code == 200:
            js = r.json(); return js.get("extract","") or ""
        return ""
    except Exception:
        return ""

def gather_web(query: str, num: int = 5, fetch_pages: bool = True) -> Tuple[List[str], List[Dict], str, str]:
    """
    يُرجع:
    - web_snippets: قائمة سطور "- نص … [url]" لاستخدامها مع المولّد المحلي
    - sources: قائمة مصادر {title, link}
    - wiki: خلاصة ويكي بالعربية (إن وجدت)
    - engine_used: "google" | "ddg" | "none"
    """
    results: List[Dict] = []
    engine_used = "none"

    # 1) جرّب Google CSE إن المفاتيح مضبوطة
    try:
        results = google_cse_search(query, num=num)
        if results:
            engine_used = "google"
    except Exception:
        results = []

    # 2) وإلا جرّب DuckDuckGo
    if not results:
        ddg = _ddg_search(query, max_results=num)
        if ddg:
            engine_used = "ddg"
            results = ddg

    # 3) هيّئ السنيبّتات + (اختياري) جلب محتوى الصفحات وزيادة الانطباع
    snippets: List[str] = []
    sources: List[Dict] = []
    for it in results[:num]:
        title = _clean_text(it.get("title",""))
        link  = it.get("link") or it.get("href") or ""
        sn    = _clean_text(it.get("snippet",""))
        if not link: 
            continue
        # إن أردنا تعميق السنيبّت
        if fetch_pages and len(sn) < 160:
            body = _fetch_text(link)
            if body:
                # خذ أول فقرة مفيدة
                para = body[:400]
                if len(para) > 60:
                    sn = para
        if sn:
            snippets.append(f"- {title}: {sn} … [{link}]")
            sources.append({"title": title, "link": link})

    # 4) ويكي عربي
    wiki = wiki_summary_ar(query)

    return snippets, sources, wiki, engine_used
