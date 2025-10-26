from typing import Dict
import nltk

class SentimentAnalyzer:
    def __init__(self):
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            self.vader = SentimentIntensityAnalyzer()
        except Exception:
            self.vader = None

    def analyze(self, text: str) -> Dict[str, float]:
        if not self.vader or not text.strip():
            return {"label": "neutral", "score": 0.0}
        scores = self.vader.polarity_scores(text)
        comp = scores.get("compound", 0.0)
        label = "positive" if comp >= 0.2 else "negative" if comp <= -0.2 else "neutral"
        return {"label": label, "score": float(comp)}
