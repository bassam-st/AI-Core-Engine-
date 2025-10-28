# engine/generator.py
from __future__ import annotations
from typing import List, Optional, Tuple
import re
from urllib.parse import urlparse

# نعتمد على scikit-learn (موجود عندك في requirements)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class AnswerSynthesizer:
    """
    مولّد محلي احترافي (بدون LLM):
    - يدمج ويكي + الويب + السياق المحلي.
    - يجزّئ إلى جمل، ويحسب صلة كل جملة بالسؤال عبر TF-IDF.
    - يزيل التكرار (MMR بسيط) ويبني جوابًا منظّمًا بأساليب مختلفة.
    - يضيف قسم "🛠 خطوات عملية" تلقائيًا عند وجود أفعال أمر/تنفيذ.
    """

    def __init__(self):
        self.style = "friendly"  # friendly | formal | brief

    # ---------- أسلوب الكتابة ----------
    def set_style(self, mode: str):
        if mode in ("friendly", "formal", "brief"):
            self.style = mode

    def _wrap_style(self, text: str) -> str:
        if self.style == "formal":
            return "إليك عرضًا منظّمًا:\n\n" + text
        if self.style == "brief":
            return text
        return "بكل ود، هذه الإجابة:\n\n" + text

    # ---------- أدوات مساعدة ----------
    _URL_RE = re.compile(r"https?://\S+")
    _BOX_URL_RE = re.compile(r"\[(https?://[^\]]+)\]")  # نمط [https://...]
    _WS_RE = re.compile(r"[ \t]+")
    _NL_RE = re.compile(r"\n{3,}")
    _SPLIT_RE = re.compile(r"(?<=[\.!\؟\?])\s+|\n+")  # تقسيم جمل عربي/إنجليزي مبسّط

    # تبسيط عربي بسيط (بدون حركات)
    _DIAC_RE = re.compile(r"[\u064B-\u065F\u0670]")  # التشكيل
    _ALEF_RE = re.compile(r"[إأآا]")
    _TAH_RE = re.compile(r"ة")
    _YA_RE = re.compile(r"[يى]")

    # أفعال/محثّات على الخطوات العملية
    _ACTION_TRIGGERS = (
        "نفّذ", "نفذ", "ثبّت", "ثبت", "ابدأ", "ابدا", "اعمل",
        "أنشئ", "انشئ", "ابنِ", "ابني", "ابن", "احصل", "خطوات", "طريقة", "كيف"
    )

    # مؤشرات الجُمل الإجرائية
    _STEP_HINTS = (
        "خطوة", "الخطوة", "ابدأ", "قم ب", "نفّذ", "نفذ", "ثبّت", "ثبت",
        "إنشئ", "أنشئ", "انشئ", "ابنِ", "ابني", "فعّل", "فعل", "أضف", "اضف",
        "حمّل", "حمل", "شغّل", "شغل", "استخدم", "هيّئ", "هيئ", "اذهب إلى", "افتح", "اختَر", "اختر"
    )

    def _normalize(self, s: str) -> str:
        s = self._DIAC_RE.sub("", s or "")
        s = self._ALEF_RE.sub("ا", s)
        s = self._TAH_RE.sub("ه", s)
        s = self._YA_RE.sub("ي", s)
        return s

    def _clean_text(self, s: str) -> str:
        s = self._URL_RE.sub("", s or "")
        s = self._WS_RE.sub(" ", s)
        s = self._NL_RE.sub("\n\n", s)
        return s.strip()

    def _domain(self, url: str) -> str:
        try:
            netloc = urlparse(url).netloc
            return netloc.lstrip("www.")
        except Exception:
            return url

    def _extract_urls_from_snippets(self, web_snippets: List[str]) -> List[str]:
        urls: List[str] = []
        for sn in web_snippets or []:
            m = self._BOX_URL_RE.search(sn)
            if m:
                urls.append(m.group(1))
        seen, out = set(), []
        for u in urls:
            if u not in seen:
                seen.add(u); out.append(u)
        return out

    # ---------- تحويل إلى جمل مرشّحة ----------
    def _sentences_from_sources(self, wiki: str, web_snippets: List[str], context: str) -> Tuple[List[str], List[str], List[str]]:
        def split_clean(text: str) -> List[str]:
            text = self._clean_text(text)
            parts = [p.strip() for p in self._SPLIT_RE.split(text) if p.strip()]
            return [p for p in parts if len(p) >= 20]

        wiki_sents = split_clean(wiki) if wiki else []
        web_sents = []
        for sn in web_snippets or []:
            s = sn.lstrip("- ").split("[http", 1)[0].strip()
            web_sents.extend(split_clean(s))
        ctx_sents = split_clean(context) if context else []
        return wiki_sents, web_sents, ctx_sents

    # ---------- ترتيب الجمل حسب الصلة (TF-IDF) + إزالة التكرار ----------
    def _rank_and_dedup(self, query: str, candidates: List[str], top_n: int = 12, sim_th: float = 0.8) -> List[str]:
        if not candidates:
            return []
        norm_query = self._normalize(query)
        norm_cands = [self._normalize(c) for c in candidates]
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95)
        X = vec.fit_transform([norm_query] + norm_cands)
        qv, cv = X[0:1], X[1:]
        sims = cosine_similarity(qv, cv).ravel()
        order = sims.argsort()[::-1]

        selected, selected_vecs = [], []
        for idx in order:
            sent = candidates[idx]
            v = cv[idx:idx + 1]
            if selected_vecs:
                dup = cosine_similarity(v, selected_vecs).max()
                if dup >= sim_th:
                    continue
            selected.append(sent)
            selected_vecs.append(v)
            if len(selected) >= top_n:
                break
        return selected

    # ---------- كشف نية "الخطوات العملية" ----------
    def _wants_steps(self, query: str) -> bool:
        q = self._normalize(query)
        return any(t in q for t in self._ACTION_TRIGGERS)

    # ---------- استخراج جمل إجرائية كخطوات ----------
    def _extract_steps(self, query: str, web_top: List[str], ctx_top: List[str], wiki_top: List[str], max_steps: int = 6) -> List[str]:
        # نعطي الأولوية للجمل التي تحتوي على مؤشرات إجرائية
        def is_step_like(s: str) -> bool:
            s_norm = self._normalize(s)
            return any(h in s_norm for h in self._STEP_HINTS) or s_norm.startswith(("ابدأ", "ابدا", "قم", "افتح", "اختَر", "اختر", "استخدم"))

        pools = [web_top, ctx_top, wiki_top]  # الأولوية: الويب ثم السياق ثم ويكي
        raw: List[str] = []
        for pool in pools:
            for s in pool:
                if is_step_like(s):
                    raw.append(s)
        # إن لم نجد جملًا واضحة، نأخذ أول جمل متنوّعة كبدائل خطوات
        if not raw:
            for pool in pools:
                raw.extend(pool[:3])
                if len(raw) >= max_steps:
                    break

        # ترتيب إضافي بالصلَة للسؤال (إعادة ترتيب خفيف)
        ranked = self._rank_and_dedup(query, raw, top_n=max_steps, sim_th=0.85)
        # تنظيف وتعداد
        steps = []
        for i, s in enumerate(ranked[:max_steps], 1):
            s = s.rstrip(" .،")
            steps.append(f"{i}) {s}")
        return steps

    # ---------- بناء الأقسام ----------
    def _build_sections(self, query: str, wiki_top: List[str], web_top: List[str], ctx_top: List[str], include_steps: bool) -> Tuple[str, List[str], List[str], List[str]]:
        """
        يُرجع: (الخلاصة السريعة، أهم النقاط، التحذيرات، الخطوات العملية)
        """
        # الخلاصة
        summary = ""
        for pool in (wiki_top, web_top, ctx_top):
            if pool:
                summary = pool[0]; break
        if not summary:
            summary = "لا توجد بيانات كافية لتوليد خلاصة موثوقة للسؤال."

        # أهم النقاط
        bullets = []
        for src in (wiki_top, web_top, ctx_top):
            for s in src[:4]:
                bullets.append(s)
                if len(bullets) >= 7:
                    break
            if len(bullets) >= 7:
                break

        # تحذيرات
        warns = []
        low_evidence = (len(wiki_top) + len(web_top) + len(ctx_top)) < 3
        if low_evidence:
            warns.append("قد تكون بعض التفاصيل غير مكتملة بسبب محدودية السياق المتاح.")
        if any(k in query for k in ["أفضل", "أحسن", "أقوى", "ultimate", "best"]):
            warns.append("الاختيار 'الأفضل' قد يختلف باختلاف المتطلبات والقيود العملية.")
        if any(k in query for k in ["سريع", "بسرعة", "فوري"]):
            warns.append("السرعة قد تؤثر على الدقة والجودة—وازن بين الزمن والدقة.")

        # خطوات عملية
        steps: List[str] = []
        if include_steps:
            steps = self._extract_steps(query, web_top, ctx_top, wiki_top, max_steps=6)
            if not steps:
                # قالب عام في حال ندرة المعلومات
                steps = [
                    "1) حدّد الهدف والمتطلبات بدقة (المدخلات/المخرجات/الزمن/الميزانية).",
                    "2) جهّز البيئة والأدوات اللازمة للتنفيذ، وتحقق من الإصدارات.",
                    "3) طبّق الخطوة الأساسية الأولى (ابدأ بأبسط نسخة قابلة للعمل).",
                    "4) اختبر النتائج مبكرًا، وسجّل الملاحظات والأخطاء.",
                    "5) حسّن الأداء/الدقة تدرّجيًا وأعد الاختبار.",
                    "6) وثّق ما تمّ وتأكد من قابلية التكرار والنشر."
                ]

        return summary, bullets, warns, steps

    # ---------- الواجهة الرئيسية (مطابقة لـ main.py) ----------
    def answer(
        self,
        *,
        query: str,
        context: str,
        intent: str,
        sentiment: str,
        web_snippets: List[str],
        wiki: str,
    ) -> str:
        """
        توليد محلي احترافي بالكامل:
        1) تحويل (ويكي/الويب/السياق) إلى جمل مرشّحة.
        2) ترتيب الجمل حسب صلتها بالسؤال عبر TF-IDF.
        3) إزالة التكرار وبناء الأقسام (خلاصة/نقاط/تحذيرات/خطوات).
        4) إضافة سطر مصادر نظيفة من الروابط (إن وجدت).
        """
        web_snippets = web_snippets or []

        # مصادر نظيفة
        urls = self._extract_urls_from_snippets(web_snippets)[:6]
        domains_line = ""
        if urls:
            domains = [self._domain(u) for u in urls]
            domains_line = " — المصادر: " + " | ".join(domains)

        # جمل مرشّحة
        wiki_s, web_s, ctx_s = self._sentences_from_sources(wiki, web_snippets, context)

        # ترتيب وإزالة تكرار
        wiki_top = self._rank_and_dedup(query, wiki_s, top_n=4, sim_th=0.82)
        web_top  = self._rank_and_dedup(query, web_s,  top_n=6, sim_th=0.82)
        ctx_top  = self._rank_and_dedup(query, ctx_s,  top_n=6, sim_th=0.82)

        # هل نعرض "خطوات عملية"؟
        include_steps = self._wants_steps(query)

        # بناء الأقسام
        summary, bullets, warns, steps = self._build_sections(query, wiki_top, web_top, ctx_top, include_steps)

        # تركيب النص النهائي
        parts: List[str] = []
        parts.append(f"❓ السؤال: {query}")
        parts.append("📘 الخلاصة السريعة:\n" + summary)

        if bullets:
            parts.append("🔹 أهم النقاط:\n" + "\n".join(f"- {b}" for b in bullets))

        if steps:
            parts.append("🛠 خطوات عملية:\n" + "\n".join(steps))

        if warns:
            parts.append("⚠️ تنبيهات:\n" + "\n".join(f"- {w}" for w in warns))

        meta = f"🧠 النية: {intent} — المشاعر: {sentiment}"
        if domains_line:
            meta += domains_line
        parts.append(meta)

        text = "\n\n".join(parts)
        text = self._clean_text(text)
        return self._wrap_style(text)
