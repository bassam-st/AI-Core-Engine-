import textwrap

class AnswerSynthesizer:
    def answer(self, query: str, context: str, intent: str, sentiment: str, web_snippets, wiki: str) -> str:
        if not (context or web_snippets or wiki):
            return "لم أجد سياقًا كافيًا بعد. ارفع ملفاتك عبر /ingest أو فعّل البحث على الويب، ثم أعد المحاولة."

        parts = []
        if context:
            parts.append(f"### سياق محلي\n{ (textwrap.shorten(context, width=1500, placeholder=' …')) }")
        if web_snippets:
            parts.append("### مقتطفات من الويب\n" + "\n".join(web_snippets[:5]))
        if wiki:
            parts.append(f"### خلاصة ويكي\n{wiki[:600]}…")

        return f"""# الإجابة
**النية:** {intent} | **المشاعر:** {sentiment}

{'\n\n'.join(parts)}

## خلاصة مركبة
- تم بناء الإجابة من المراجع أعلاه دون استخدام مفاتيح خارجية.
- لتحسين الدقة، أضف مستنداتك الخاصة عبر /ingest، وسأسترجع منها مباشرة.
"""
