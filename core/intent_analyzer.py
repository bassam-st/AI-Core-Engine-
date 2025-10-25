# core/intent_analyzer.py
class AdvancedIntentAnalyzer:
    def analyze_intent(self, text: str) -> Dict:
        """تحليل متقدم للنوايا"""
        intents = {
            "question": self._is_question(text),
            "command": self._is_command(text), 
            "creation": self._is_creation_request(text),
            "analysis": self._is_analysis_request(text),
            "learning": self._is_learning_request(text)
        }
        return self._select_primary_intent(intents)
