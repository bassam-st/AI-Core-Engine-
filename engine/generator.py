from typing import List, Dict, Any, Tuple
INTRO = "إليك خلاصة مختصرة:"
class AnswerSynthesizer:
    def compose_answer(self, question: str, hits: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        if not hits:
            return ("لم يتم العثور على نتائج في المعرفة المحلية.", [])
        parts = [INTRO, ""]
        used = []
        for i, h in enumerate(hits, 1):
            snip = (h.get("snippet") or "").replace("\n", " ")
            parts.append(f"{i}) {snip[:300]}{'…' if len(snip)>300 else ''}")
            used.append(h)
        parts.append("\nالمصادر:")
        for h in used:
            parts.append(f"- {h['path']} (score={h['score']:.3f})")
        return "\n".join(parts), used
