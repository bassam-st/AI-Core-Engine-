def _score(text: str) -> float:
    # قاموس صغير للميل الإيجابي/السلبي
    pos = ["ممتاز","جيد","رائع","شكرا","سعيد","افضل","جميل","نجاح"]
    neg = ["سيء","حزين","مشكل","خطأ","غضب","فشل","كارث","ضعيف"]
    s = text or ""
    sc = sum(1 for w in pos if w in s) - sum(1 for w in neg if w in s)
    return sc

class SentimentAnalyzer:
    def analyze(self, text: str) -> dict:
        s = _score(text)
        if s > 0: label = "positive"
        elif s < 0: label = "negative"
        else: label = "neutral"
        return {"label": label, "score": s}
