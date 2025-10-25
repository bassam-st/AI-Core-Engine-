# core/crawler.py — جلب صفحة + زحف بسيط داخل نفس النطاق
from __future__ import annotations
import re, urllib.parse, requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124 Safari/537.36"}

def fetch_url(url: str, timeout: int = 12) -> tuple[str, list[str]]:
    """يرجع (نص_مُنظّف, روابط_مطلقة) لصفحة واحدة."""
    try:
        r = requests.get(url, headers=UA, timeout=timeout)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "lxml")
        for s in soup(["script","style","noscript"]): s.extract()
        text = " ".join(soup.get_text(" ").split())
        links: list[str] = []
        for a in soup.find_all("a", href=True):
            abs_url = urllib.parse.urljoin(url, a["href"])
            if abs_url.startswith("http"):
                links.append(abs_url)
        return text, links
    except Exception:
        return "", []

def crawl_site(seed_url: str, max_pages: int = 5) -> list[dict]:
    """يزحف داخل نفس النطاق بشكل محدود ويجمع نصوصًا وروابط."""
    seen, queue = set(), [seed_url]
    out: list[dict] = []
    try:
        base = urllib.parse.urlparse(seed_url).netloc
    except Exception:
        base = ""
    while queue and len(out) < max_pages:
        u = queue.pop(0)
        if u in seen: 
            continue
        seen.add(u)
        txt, links = fetch_url(u)
        if txt:
            out.append({"url": u, "text": txt})
        # روابط داخل نفس النطاق فقط
        for v in links:
            try:
                if urllib.parse.urlparse(v).netloc == base and v not in seen and len(queue) < max_pages*3:
                    queue.append(v)
            except Exception:
                continue
    return out
