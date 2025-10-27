# engine/generator.py
from __future__ import annotations
from typing import List, Tuple
import re
from urllib.parse import urlparse


class AnswerSynthesizer:
    """
    مولِّد إجابات بسيط بدون نماذج ضخمة:
    - يكوّن خلاصة قصيرة من (ويكي -> الويب -> السياق المحلي)
    - ينسّق الفقرات النهائية
    - ينظّف الروابط الطويلة ويعرض قائمة مصادر مختصرة
    - يدعم أساليب الكتابة: ودود/رسمي/مختصر
    """

    def __init__(self):
        self.style = "friendly"

    # ---------- تنسيق الأسلوب ----------
    def set_style(self, mode: str):
        if mode in ("friendly", "formal", "brief"):
            self.style = mode

    def _style_wrap(self, text: str) -> str:
        if self.style == "formal":
            return "إليك خلاصة منظَّمة:\n\n" + text
        if self.style == "brief":
            return text
        return "بكل ود، هذه الإجابة:\n\n" + text

    # ---------- أدوات مساعدة ----------
    _URL_RE = re.compile(r"https?://\S+")
    _BOX_URL_RE = re.compile(r"\[(https?://[^\]]+)\]")  # نمط [https://...]
    _WS_RE = re.compile(r"[ \t]+")
    _NL_RE = re.compile(r"\n{3,}")

    def _clean_text(self, s: str) -> str:
        # نحذف الروابط الخام الطويلة ونرتّب المسافات
        s = self._URL_RE.sub("", s)
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
            # لدينا تنسيق "- مقطع … [url]" من مسار /chat
            m = self._BOX_URL_RE.search(sn)
            if m:
                urls.append(m.group(1))
        # إزالة التكرار مع الحفاظ على الترتيب
        seen = set()
        uniq = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                uniq.append(u)
        return uniq

    def _pick_short_answer(self, wiki: str, web_snippets: List[str], context: str) -> str:
        # الأولوية: ويكي → أول سطر واضح من الويب → جزء موجز من السياق المحلي
        # 1) من ويكي
        if wiki:
            w = self._clean_text(wiki)
            if w:
                return (w[:400] + "…") if len(w) > 430 else w

        # 2) من الويب (نحاول أخذ أول سطر قبل أي أقواس/روابط)
        for sn in web_snippets or []:
            # احذف البادئة "- "
            s = sn.lstrip("- ").strip()
            # افصل عند المربع الذي يحتوي على الرابط
            s = s.split("[http", 1)[0].strip()
            s = self._clean_text(s)
            if len(s) >= 40:  # سطر مفهوم
                return (s[:400] + "…") if len(s) > 430 else s

        # 3) من السياق المحلي
        if context:
            c = self._clean_text(context)
            return (c[:400] + "…") if len(c) > 430 else c

        return "لا توجد بيانات كافية لتوليد ملخص موثوق."

    # ---------- الواجهة الرئيسية ----------
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
        توليف إجابة نهائية مرتبة:
        - ❓ السؤال
        - 📘 خلاصة قصيرة (من ويكي/الويب/السياق)
        - 📌 أدلة مختصرة (حتى 3 عناصر)
        - 🔗 مصادر بروابط نظيفة (حتى 5)
        - 🧠 النية/المشاعر
        """
        web_snippets = web_snippets or []

        # 1) خلاصة قصيرة
        short_answer = self._pick_short_answer(wiki, web_snippets, context)

        # 2) أدلة مختصرة (نأخذ أول 2-3 أسطر موجزة من الويب/السياق)
        evidence: List[str] = []
        for sn in web_snippets[:3]:
            s = sn.lstrip("- ").split("[http", 1)[0].strip()
            s = self._clean_text(s)
            if s:
                evidence.append(s[:180] + ("…" if len(s) > 200 else ""))
        if not evidence and context:
            c_first = self._clean_text(context)[:180]
            if c_first:
                evidence.append(c_first + ("…" if len(c_first) >= 180 else ""))

        # 3) مصادر نظيفة
        urls = self._extract_urls_from_snippets(web_snippets)[:5]
        sources_line = ""
        if urls:
            domains = [self._domain(u) for u in urls]
            sources_line = " — المصادر: " + " | ".join(domains)

        # 4) بناء النص النهائي
        body_parts: List[str] = [
            f"❓ السؤال: {query}",
            "📘 الخلاصة:\n" + short_answer,
        ]
        if evidence:
            ev_str = "\n".join(f"- {e}" for e in evidence)
            body_parts.append("📌 أدلة مختصرة:\n" + ev_str)

        meta = f"🧠 النية: {intent} — المشاعر: {sentiment}"
        if sources_line:
            meta += sources_line

        body_parts.append(meta)

        final_text = "\n\n".join(body_parts)
        final_text = self._clean_text(final_text)

        return self._style_wrap(final_text)
