from __future__ import annotations
from typing import List, Dict
from duckduckgo_search import DDGS
import requests, json, os
from bs4 import BeautifulSoup
from core.memory import add_fact, get_recent_conversations

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
    if not url: return ""
    try:
        html = requests.get(url, headers=UA, timeout=12).text
        soup = BeautifulSoup(html, "lxml")
        for s in soup(["script", "style", "noscript"]): s.extract()
        text = " ".join(soup.get_text(" ").split())
        return text[:max_chars]
    except Exception: return ""

def _summarize_lines(blobs: List[str], max_lines: int = 4) -> List[str]:
    sents = []
    for t in blobs:
        for sent in t.split("."):
            sent = sent.strip()
            if 30 < len(sent) < 220: sents.append(sent)
    sents = sorted(sents, key=len, reverse=True)
    out, seen = [], set()
    for s in sents:
        key = s[:40]
        if key not in seen:
            seen.add(key); out.append(s)
        if len(out) >= max_lines: break
    return out

def _generate_topics_from_memory() -> List[str]:
    try:
        conversations = get_recent_conversations(limit=10)
        topics = []
        for conv in conversations:
            user_msg = conv.get("user", "").lower()
            if any(w in user_msg for w in ["كود", "برمجة", "بايثون"]):
                topics.extend(["برمجة بايثون", "تطوير الويب", "قواعد البيانات"])
            if any(w in user_msg for w in ["صحة", "طبي", "علاج"]):
                topics.extend(["نصائح صحية", "الطب الوقائي", "التغذية"])
            if any(w in user_msg for w in ["تقنية", "ذكاء", "آلة"]):
                topics.extend(["الذكاء الاصطناعي", "تعلم الآلة", "التقنيات الحديثة"])
        return list(set(topics))[:5]
    except: return []

def run_once(topics: List[str] | None = None) -> int:
    if topics is None:
        topics = _generate_topics_from_memory() or [
            "مبادئ المحاسبة للتجار", "تعريف الذكاء الاصطناعي وفروعه",
            "نصائح صحية مبسطة", "أخبار تقنية اليوم باختصار",
        ]

    store = _load_knowledge()
    known_set = set((item.get("text") or "").strip() for item in store if item.get("text"))

    added = 0
    for t in topics:
        results = _ddg_search(t, max_results=5)
        blobs = []
        for r in results[:3]:
            txt = _fetch_clean_text(r.get("url", ""))
            if txt: blobs.append(txt)
        lines = _summarize_lines(blobs, max_lines=4)
        for ln in lines:
            ln = ln.strip()
            if len(ln) > 40 and ln not in known_set:
                store.append({"text": ln, "source": "autolearn", "topic": t})
                known_set.add(ln)
                add_fact(ln, source="autolearn")  # إضافة للذاكرة أيضاً
                added += 1

    if added: _save_knowledge(store)
    return added

def learn_from_conversations() -> int:
    learned_count = 0
    try:
        conversations = get_recent_conversations(limit=20)
        for conv in conversations:
            bot_msg = conv.get("bot", "")
            if len(bot_msg) > 50 and "لم أجد" not in bot_msg:
                add_fact(bot_msg, source="conversation_learning")
                learned_count += 1
    except Exception as e:
        print(f"خطأ في التعلم من المحادثات: {e}")
    return learned_count

def continuous_learning_pipeline() -> Dict:
    web_learned = run_once()
    conv_learned = learn_from_conversations()
    from core.memory import manage_memory_size
    manage_memory_size()
    
    return {
        "web_learned": web_learned,
        "conversation_learned": conv_learned,
        "total_learned": web_learned + conv_learned
    }
