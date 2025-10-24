# core/brain.py — دماغ مبسط: ذاكرة + بحث ويب + تلخيص جُمَل
from __future__ import annotations
from typing import List, Tuple
from core.memory import search_memory, add_fact, save_conv
from core.web_search import web_search, fetch_text

OPENERS = [
    "أكيد!",
    "تمام،",
    "خلّيني أختصر لك:",
    "باختصار:",
]

def _pick_opener(i: int = 0) -> str:
    return OPENERS[i % len(OPENERS)]

def _summarize_snippets(snippets: List[str], max_lines: int = 6) -> List[str]:
    sents: List[str] = []
    for t in snippets:
        for p in t.split("."):
            p = p.strip()
            if 20 < len(p) < 240:
                sents.append(p)
    sents = sorted(sents, key=len, reverse=True)
    seen, out = set(), []
    for s in sents:
        k = s[:40]
        if k not in seen:
            seen.add(k)
            out.append(s)
        if len(out) >= max_lines:
            break
    return out

def _format_sources(sources: List[dict]) -> List[dict]:
    return [{"title": s.get("title",""), "url": s.get("url","")} for s in sources]

def chat_answer(q: str) -> Tuple[str, List[dict]]:
    q = (q or "").strip()
    # 1) ذاكرة
    mem_hits = search_memory(q, limit=5)
    mem_texts = [h["text"] for h in mem_hits]
    # 2) قرار استخدام الويب
    need_web = len(mem_hits) == 0 or (mem_hits and mem_hits[0]["score"] < 1.5)
    web_results = web_search(q, max_results=6) if need_web else []
    # 3) جلب نصوص من أفضل الروابط
    page_texts: List[str] = []
    for r in web_results[:3]:
        u = r.get("url")
        if not u:
            continue
        txt = fetch_text(u)
        if txt:
            page_texts.append(txt)
    # 4) تلخيص وتركيب جواب
    summary_lines = _summarize_snippets(mem_texts + page_texts, max_lines=6)
    if not summary_lines and not mem_texts and not page_texts:
        reply = "لم أجد معلومات كافية الآن. جرّب إعادة الصياغة أو أضف معلومة يدويًا عبر /api/learn."
        save_conv(q, reply);  return reply, []
    opener = _pick_opener(len(mem_texts) + len(page_texts))
    body = ("\n- " + "\n- ".join(summary_lines)) if summary_lines else ""
    reply = f"{opener} {body.strip()}".strip()
    # 5) تخزين بعض الجُمل كحقائق
    for line in summary_lines[:3]:
        if len(line) > 40:
            add_fact(line, source="autolearn")
    save_conv(q, reply)
    return reply, _format_sources(web_results[:5])
