# engine/style.py
import re

class StyleModel:
    """
    طبقة تنسيق الأسلوب البشري: عربي واضح، علامات ترقيم، خيارات أسلوب.
    modes: 'friendly' | 'formal' | 'brief'
    """

    def __init__(self, mode: str = "friendly"):
        self.mode = mode

    def set_mode(self, mode: str):
        if mode in ("friendly", "formal", "brief"):
            self.mode = mode

    def _norm_ar(self, s: str) -> str:
        s = re.sub(r"\s+", " ", s)
        s = s.replace(" ,", ",").replace(" .", ".").replace(" ؛", "؛").replace(" :", ":")
        s = re.sub(r"\s+([،؛:.!?])", r"\1", s)
        return s.strip()

    def postprocess(self, answer: str, intent: str = "", sentiment: str = "") -> str:
        t = self._norm_ar(answer or "")
        if self.mode == "brief":
            lines = [ln.strip("•- ") for ln in t.splitlines() if ln.strip()]
            t = " • " + "\n • ".join(lines[:6])
            return t

        if self.mode == "formal":
            prefix = "بكل احترام، إليك الخلاصة:\n"
            return prefix + t

        # friendly
        prefix = "بالضبط! إليك الجواب بشكل بسيط:\n"
        return prefix + t
