# engine/generator.py
import textwrap
from engine.style import StyleModel

class AnswerSynthesizer:
    """
    يركّب الإجابة النهائية من:
    - سياق محلي مسترجَع
    - مقتطفات الويب
    - خلاصة الويكي
    ويمررها عبر StyleModel لإخراج أسلوب عربي بشري (ودود/رسمي/مختصر).
    """

    def __init__(self):
        # الوضع الافتراضي: ودود
        self.styler = StyleModel(mode="friendly")

    def set_style(self, mode: str):
        """تغيير الأسلوب أثناء التشغيل: friendly | formal | brief"""
        self.styler.set_mode(mode)

    def answer(self, query: str, context: str, intent: str, sentiment: str,
               web_snippets, wiki: str) -> str:
        """
        يجمّع المصادر ويولّد خلاصة مركبة، ثم ينسّق الأسلوب.
        """
        if not (context or web_snippets or wiki):
            # لا يوجد سياق كافٍ
            msg = (
                "لم أجد سياقًا كافيًا بعد. "
                "ارفع ملفاتك عبر /ingest أو /ingest/url أو فعّل البحث على الويب، ثم أعد المحاولة."
            )
            return self.styler.postprocess(msg, intent, sentiment)

        parts = []

        if context:
            parts.append(
                "### سياق محلي\n" +
                textwrap.shorten(context, width=1500, placeholder=" …")
            )

        if web_snippets:
            parts.append(
                "### مقتطفات من الويب\n" +
                "\n".join(web_snippets[:5])
            )

        if wiki:
            parts.append(
                "### خلاصة ويكي\n" +
                (wiki[:600] + "…")
            )

        merged = "\n\n".join(parts)

        raw = f"""# الإجابة
**النية:** {intent} | **المشاعر:** {sentiment}

{merged}

## خلاصة مركّبة
- تم تركيب الرد من المصادر أعلاه (محلية/ويب/ويكي) بدون مفاتيح مدفوعة افتراضيًا.
- لرفع الدقة، أضف مستنداتك الخاصة عبر /ingest أو /ingest/url.
"""
        return self.styler.postprocess(raw, intent, sentiment)
