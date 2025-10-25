# core/agents/planner.py — يخطّط خطوات عمل الفريق
from __future__ import annotations

def make_plan(goal: str, urls: list[str] | None = None) -> list[str]:
    steps = [
        "فهم الهدف وصياغة موجز قصير",
        "جمع معرفة: بحث ويب + قراءة الروابط المعطاة",
        "تلخيص النتائج واستخراج المتطلبات",
        "توليد ملفات أولية (HTML/CSS/JS أو Python حسب الهدف)",
        "مراجعة سريعة وتشغيل اختبارات بسيطة",
        "تغليف النتيجة وإرجاع المصادر والملفّات"
    ]
    if urls:
        steps.insert(1, f"قراءة {len(urls)} رابط مبدئي من المستخدم")
    return steps
