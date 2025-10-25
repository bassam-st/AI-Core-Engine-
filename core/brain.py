from __future__ import annotations
from typing import List, Tuple
from core.memory import search_memory, add_fact, save_conv
from core.web_search import web_search, fetch_text, wiki_summary_ar
from core.code_team import build_project
from core.coder import generate_code

OPENERS = ["أكيد!", "تمام،", "خلّيني أختصر لك:", "باختصار:"]
SMALL_TALK = {
    "كيف حالك": "أنا بخير ولله الحمد 🙌 جاهز أساعدك في أي شيء.",
    "من انت": "أنا نواة بسّام الذكية — أبحث وألخّص وأتعلّم من كلامك.",
    "السلام عليكم": "وعليكم السلام ورحمة الله، حيّاك الله 🌟",
}

def _normalize_ar(s: str) -> str:
    return (s or "").replace("أ","ا").replace("إ","ا").replace("آ","ا").replace("ة","ه").lower()

def _small_talk_reply(q: str) -> str | None:
    nq = _normalize_ar(q)
    for k, v in SMALL_TALK.items():
        if _normalize_ar(k) in nq: return v
    return None

def _escape_html(s: str) -> str:
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def _is_code_intent(q: str) -> bool:
    nq = _normalize_ar(q)
    code_words = ["كود","اكواد","برمجه","برمج","شفره","دالة","function"]
    tech_words = ["javascript","python","html","css","sql","java","react","vue","go","rust","dart","c++","c#","php","kotlin","swift"]
    return any(w in nq for w in code_words + tech_words)

def _is_project_intent(q: str) -> bool:
    nq = _normalize_ar(q)
    project_words = ["مشروع","موقع","تطبيق","api","خادم","سيرفر","landing","صفحه","صفحة","نظام"]
    return any(w in nq for w in project_words)

def _should_learn(text: str) -> bool:
    if len(text) < 30: return False
    if any(word in text for word in ["خطأ", "error", "لا أعرف", "لم أجد"]): return False
    return True

def _summarize_snippets(snippets: List[str], max_lines: int = 6) -> List[str]:
    sents: List[str] = []
    for t in snippets or []:
        for p in (t or "").split("."):
            p = p.strip()
            if 20 < len(p) < 240: sents.append(p)
    sents = sorted(sents, key=len, reverse=True)
    out, seen = [], set()
    for s in sents:
        k = s[:40]
        if k in seen: continue
        seen.add(k); out.append(s)
        if len(out) >= max_lines: break
    return out

def _format_sources(sources: List[dict] | None) -> List[dict]:
    return [{"title": s.get("title",""), "url": s.get("url","")} for s in (sources or [])]

def chat_answer(q: str) -> Tuple[str, List[dict]]:
    q = (q or "").strip()
    if not q: return "اذكر سؤالك من فضلك.", []

    # 0) حوار ودّي
    st = _small_talk_reply(q)
    if st: save_conv(q, st); return st, []

    # 0.5) نية مشروع/كود — قبل أي بحث
    if _is_project_intent(q):
        try:
            proj = build_project(q)
            if proj.get("ok"):
                files = proj.get("files", {})
                names = list(files.keys())
                show = ""
                if names:
                    first = names[0]
                    show = f"<pre><code>{_escape_html(files[first])}</code></pre>"
                reply = "🧩 تم إنشاء مشروع أوّلي.\n" \
                        f"- الملفات: {', '.join(names) or 'لا يوجد'}\n" \
                        f"- ملاحظات: {len(proj.get('issues', []))}\n" \
                        f"- نصيحة: {proj.get('tips','')}\n\n" + show
                save_conv(q, reply)
                for n in names[:3]:
                    add_fact(f"ملف مشروع: {n} ({len(files[n])} chars).", source="code-team")
                return reply, []
        except Exception as e:
            print(f"خطأ في بناء المشروع: {e}")

    if _is_code_intent(q):
        try:
            result = generate_code(q)
            code, lang, title = result["code"], result["lang"], result["title"]
            reply = f"🔧 {title}\n\n<pre><code>{_escape_html(code)}</code></pre>"
            if _should_learn(code):
                add_fact(f"مثال كود {lang}: {title}.", source="codegen")
                add_fact(f"مقتطف {lang}: {code.strip()[:800]}", source="codegen")
            save_conv(q, reply)
            return reply, []
        except Exception as e:
            print(f"خطأ في توليد الكود: {e}")

    # 1) ذاكرة محسنة
    mem_hits = search_memory(q, limit=8)
    mem_texts = [h["text"] for h in mem_hits]

    # 2) بحث ويب
    need_web = not mem_hits or (mem_hits and mem_hits[0]["score"] < 1.5)
    try: web_results = web_search(q, max_results=6) if need_web else []
    except Exception as e: 
        print(f"خطأ في البحث: {e}")
        web_results = []
    
    page_texts: List[str] = []
    for r in web_results[:3]:
        u = r.get("url"); 
        if not u: continue
        txt = fetch_text(u)
        if txt: page_texts.append(txt)
    if need_web and not page_texts:
        wk = wiki_summary_ar(q)
        if wk: page_texts.append(wk)

    # 3) إجابة مختصرة
    summary = _summarize_snippets(mem_texts + page_texts, max_lines=6)
    if not summary:
        msg = "لم أجد معلومات كافية الآن. جرّب إعادة الصياغة أو اطلب مني مشروع/كود."
        save_conv(q, msg); return msg, _format_sources(web_results[:5])

    opener = OPENERS[(len(mem_texts)+len(page_texts)) % len(OPENERS)]
    reply = f"{opener}\n- " + "\n- ".join(summary)
    
    # تعلم تلقائي من الردود الجيدة
    for line in summary[:3]:
        if _should_learn(line): 
            add_fact(line, source="autolearn")
    
    save_conv(q, reply)
    return reply, _format_sources(web_results[:5])

def trigger_learning():
    from core.learn_loop import continuous_learning_pipeline
    result = continuous_learning_pipeline()
    return f"🤖 تعلمت {result['total_learned']} معلومة جديدة!"
