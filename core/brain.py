# core/brain.py — دماغ نواة بسّام الذكية (بحث + ويكي + كود + تعلم من الكود)
from __future__ import annotations
from typing import List, Tuple
from core.memory import search_memory, add_fact, save_conv
from core.web_search import web_search, fetch_text, wiki_summary_ar

OPENERS = ["أكيد!", "تمام،", "خلّيني أختصر لك:", "باختصار:"]

SMALL_TALK = {
    "كيف حالك": "أنا بخير ولله الحمد 🙌 جاهز أساعدك في أي شيء.",
    "من انت": "أنا نواة بسّام الذكية — أبحث وألخّص وأتعلّم من كلامك.",
    "وش اخبارك": "كل شيء تمام! قل لي ماذا تريد أن أعمل الآن؟",
    "السلام عليكم": "وعليكم السلام ورحمة الله، حيّاك الله 🌟",
}

def _pick_opener(i: int = 0) -> str:
    return OPENERS[i % len(OPENERS)]

def _summarize_snippets(snippets: List[str], max_lines: int = 6) -> List[str]:
    sents: List[str] = []
    for t in snippets:
        if not t:
            continue
        for p in t.split("."):
            p = p.strip()
            if 20 < len(p) < 240:
                sents.append(p)
    sents = sorted(sents, key=len, reverse=True)
    seen, out = set(), []
    for s in sents:
        k = s[:40]
        if k not in seen:
            seen.add(k); out.append(s)
        if len(out) >= max_lines:
            break
    return out

def _format_sources(sources: List[dict] | None) -> List[dict]:
    safe = sources or []
    return [{"title": s.get("title",""), "url": s.get("url","")} for s in safe]

def _normalize_ar(s: str) -> str:
    return (s or "").replace("أ","ا").replace("إ","ا").replace("آ","ا").replace("ة","ه").lower()

def _small_talk_reply(q: str) -> str | None:
    nq = _normalize_ar(q)
    for k, v in SMALL_TALK.items():
        if _normalize_ar(k) in nq:
            return v
    return None

def _escape_html(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def _is_code_intent(q: str) -> bool:
    nq = _normalize_ar(q)
    # كلمات متنوّعة للطلب: انشئ/انشا/سوي/اكتب/اعطني/ولد ... + كود/اكواد/برمجه/شفره
    triggers_any = any(w in nq for w in ["انشئ","انشا","سوي","اكتب","اعطني","ولد","انشاء"])
    code_words   = any(w in nq for w in ["كود","اكواد","برمجه","برمج","شفره","javascript","python","html","css","sql","جافا"])
    return ("كود" in nq) or (triggers_any and code_words)

def chat_answer(q: str) -> Tuple[str, List[dict]]:
    q = (q or "").strip()
    if not q:
        return "اذكر سؤالك من فضلك.", []

    # 0) ردود ودّية
    st = _small_talk_reply(q)
    if st:
        save_conv(q, st)
        return st, []

    # 0.5) ⚡ توليد الكود مباشرةً إن كانت النية برمجية (قبل أي بحث/تلخيص)
    if _is_code_intent(q):
        from core.coder import generate_code
        result = generate_code(q)            # {title, lang, code}
        code = result["code"]; lang = result["lang"]; title = result["title"]
        code_html = _escape_html(code)
        reply = f"🔧 {title}\n\n<pre><code>{code_html}</code></pre>"
        # نتعلّم من الكود
        add_fact(f"مثال كود ({lang}) بعنوان: {title}.", source="codegen")
        add_fact(f"مقتطف {lang}: {code.strip()[:1200]}", source="codegen")
        save_conv(q, reply)
        return reply, []

    # 1) ذاكرة
    mem_hits = search_memory(q, limit=5)
    mem_texts = [h["text"] for h in mem_hits]

    # 2) بحث ويب
    need_web = len(mem_hits) == 0 or (mem_hits and mem_hits[0]["score"] < 1.5)
    try:
        web_results = web_search(q, max_results=6) if need_web else []
    except Exception:
        web_results = []

    # 3) جلب نصوص من الروابط + ملخص ويكي
    page_texts: List[str] = []
    for r in web_results[:3]:
        u = r.get("url")
        if not u: 
            continue
        txt = fetch_text(u)
        if txt:
            page_texts.append(txt)

    if need_web and not page_texts:
        wk = wiki_summary_ar(q)
        if wk:
            page_texts.append(wk)

    # 4) تلخيص وتركيب جواب
    summary_lines = _summarize_snippets(mem_texts + page_texts, max_lines=6)
    if not summary_lines:
        reply = "لم أجد معلومات كافية الآن. جرّب إعادة الصياغة أو علّمني معلومة بقولك: «أضف هذه المعلومة: ...»."
        save_conv(q, reply)
        return reply, _format_sources(web_results[:5])

    opener = _pick_opener(len(mem_texts) + len(page_texts))
    body = ("\n- " + "\n- ".join(summary_lines)) if summary_lines else ""
    reply = f"{opener} {body.strip()}".strip()

    # 5) تعلّم تلقائي من الملخص
    for line in summary_lines[:3]:
        if len(line) > 40:
            add_fact(line, source="autolearn")

    save_conv(q, reply)
    return reply, _format_sources(web_results[:5])
