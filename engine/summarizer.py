import re
from typing import List

def _clean(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip())

class Summarizer:
    def summarize(self, text: str, max_sent: int = 6) -> str:
        # ملخّص بسيط قائم على أفضل الجمل (طول/تكرار كلمات)
        sents = re.split(r"(?<=[.!؟\n])\s+", text or "")
        sents = [_clean(s) for s in sents if len(_clean(s)) > 0]
        if len(sents) <= max_sent: 
            return _clean(text)
        scores = [(i, len(s)) for i, s in enumerate(sents)]
        top = [s for _, s in sorted(scores, key=lambda x: x[1], reverse=True)[:max_sent]]
        return " ".join(top)

    def combine_and_summarize(self, chunks: List[str]) -> str:
        combined = "\n\n".join(chunks or [])
        return self.summarize(combined, max_sent=8)
