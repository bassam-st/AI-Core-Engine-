from typing import List

class AnswerSynthesizer:
    def __init__(self):
        self.style = "friendly"

    def set_style(self, mode: str):
        if mode in ("friendly","formal","brief"):
            self.style = mode

    def _style_wrap(self, text: str) -> str:
        if self.style == "formal":
            return "إليك خلاصة منظمة:\n\n" + text
        if self.style == "brief":
            return text
        return "بكل ود، هذه الإجابة:\n\n" + text

    def answer(self, *, query: str, context: str, intent: str, sentiment: str,
               web_snippets: List[str], wiki: str) -> str:
        parts = []
        if context:
            parts.append("📚 من ملفاتك:\n" + context[:1200])
        if wiki:
            parts.append("📘 من ويكيبيديا:\n" + wiki[:800])
        if web_snippets:
            parts.append("🌐 من الويب:\n" + "\n".join(web_snippets[:6]))
        parts.append(f"\n🔎 النية المتوقعة: {intent} — الحالة: {sentiment}")
        core = "\n\n".join(parts) if parts else "لم أعثر على سياق كافٍ، أستطيع البحث أكثر عند رغبتك."
        return self._style_wrap(core)
