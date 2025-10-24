# core/learn_loop.py — حلقة التعلّم الذاتي المجانية (بدون مفاتيح)
from __future__ import annotations
from typing import List, Dict
from duckduckgo_search import DDGS
import requests, json, os
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}

# مسار ملف المعرفة الطويلة الأمد (موجود مجلد knowledge عندك)
KNOW_PATH = os.path.join("knowledge", "elite_knowledge.json")

def _load_knowledge() -> List[Dict]:
    os.makedirs(os.path.dirname(KNOW_PATH), exist_ok=True)
    if not os.path.isfile(KNOW_PATH):
        with open(KNOW_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    try:
        with open(KNOW_PATH, "r", encoding="utf-8") as f:
            return json.load(f) or []
    except Exception:
        return []

def _save_knowledge(items: List[Dict]) -> None:
    with open(KNOW_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def _ddg_search(q: str, max_results: int = 6) -> List[Dict]:
    with DDGS() as ddg:
        res = ddg.text(q, max_results=max_results, region="xa-ar")
        out = []
        for r in res or []:
            out.append({
                "title": r.get("title") or "",
                "url": r.get("href") or r.get("url") or "",
                "snippet": r.get("body") or r.get("snippet") or ""
            })
        return out

def _fetch_clean_text(url: str, max_chars: int = 4000) -> str:
    if not url:
        return ""
    try:
        html = requests.get(url, headers=UA, timeout=12).text
        soup = BeautifulSoup(html, "lxml")
        for s in soup(["script", "style", "noscript"]):
            s.extract()
        text = " ".join(soup.get_text(" ").split())
        return text[:max_chars]
    except Exception:
        return ""

def _summarize_lines(blobs: List[str], max_lines: int = 4) -> List[str]:
    # ملخّص بسيط: اختيار جمل معلوماتية متوسطة الطول بدون أي نموذج مدفوع
    sents = []
    for t in blobs:
        for sent in t.split("."):
            sent = sent.strip()
            if 30 < len(sent) < 220:
                sents.append(sent)
    sents = sorted(sents, key=len, reverse=True)
    out, seen = [], set()
    for s in sents:
        key = s[:40]
        if key not in seen:
            seen.add(key)
            out.append(s)
        if len(out) >= max_lines:
            break
    return out

def run_once(topics: List[str] | None = None) -> int:
    """
    يشغَّل مرة واحدة: يبحث في الويب، يستخرج جُمل معرفة، ويضيفها لملف knowledge/elite_knowledge.json
    يرجّع عدد الجمل الجديدة المضافة.
    """
    if topics is None:
        topics = [
            "مبادئ المحاسبة للتجار",
            "تعريف الذكاء الاصطناعي وفروعه",
            "نصائح صحية مبسطة",
            "أخبار تقنية اليوم باختصار",
        ]

    store = _load_knowledge()
    known_set = set((item.get("text") or "").strip() for item in store if item.get("text"))

    added = 0
    for t in topics:
        results = _ddg_search(t, max_results=5)
        blobs = []
        for r in results[:3]:
            txt = _fetch_clean_text(r.get("url", ""))
            if txt:
                blobs.append(txt)
        lines = _summarize_lines(blobs, max_lines=4)
        for ln in lines:
            ln = ln.strip()
            if len(ln) > 40 and ln not in known_set:
                store.append({"text": ln, "source": "autolearn", "topic": t})
                known_set.add(ln)
                added += 1

    if added:
        _save_knowledge(store)
    return added
