# core/code_team.py — Code Team (Planner + NLU + Developer + Reviewer)
from __future__ import annotations
from typing import Dict, Any, List
from textwrap import dedent
from core.coder import generate_code

def _norm(s: str) -> str:
    return (s or "").replace("أ","ا").replace("إ","ا").replace("آ","ا").replace("ة","ه").lower()

def detect_intent(prompt: str) -> Dict[str, Any]:
    """فهم نية المستخدم (موقع / API / سكربت / لغة معيّنة...)."""
    p = _norm(prompt)
    intent = {"type": "script", "lang": None}
    if any(w in p for w in ["موقع","صفحه","صفحة","landing","html","واجهة"]):
        intent["type"] = "webpage"
    if any(w in p for w in ["api","واجهه برمجيه","خادم","سيرفر","backend","باك اند"]):
        intent["type"] = "api"
    langs = ["html","css","javascript","js","typescript","python","fastapi","flask","php","java","kotlin","swift","c#","csharp","go","golang","rust","cpp","c++","c","dart","sql"]
    for l in langs:
        if l in p or (" "+l) in p:
            intent["lang"] = l
            break
    return intent

def plan_steps(intent: Dict[str,Any]) -> List[str]:
    return [
        "فهم الهدف والمتطلبات من نصّ المستخدم",
        "تحديد نوع المشروع (صفحة/خادم/API/سكربت)",
        "توليد ملفات أساسية مناسبة",
        "مراجعة بسيطة للكود الناتج",
        "إرجاع الملفات + إرشادات التشغيل"
    ]

def build_project(prompt: str) -> Dict[str, Any]:
    """ينشئ مشروعًا كاملاً بملفات متعددة بحسب النية."""
    intent = detect_intent(prompt)
    t = intent["type"]
    files: Dict[str,str] = {}
    notes: List[str] = []
    tips = ""

    if t == "webpage":
        html = generate_code("html ترحيب")["code"]
        css  = dedent("""
            body{font-family:system-ui;background:#0b1220;color:#e7ecff;margin:0}
            .container{max-width:840px;margin:8vh auto;padding:24px}
            .card{background:#121b2d;border:1px solid #1e2b44;border-radius:14px;padding:24px}
            a{color:#9bd1ff}
        """).strip()
        js   = 'console.log("Site ready!");'
        files["index.html"] = html
        files["style.css"]  = css
        files["main.js"]    = js
        tips = "افتح index.html في المتصفح."

    elif t == "api":
        files["app.py"] = dedent("""
            from fastapi import FastAPI
            app = FastAPI(title="Simple API")
            @app.get("/hello")
            def hello(name: str = "العالم"): return {"msg": f"مرحباً يا {name}!"}
            if __name__ == "__main__":
                import uvicorn
                uvicorn.run(app, host="0.0.0.0", port=8000)
        """).strip()
        tips = "pip install fastapi uvicorn && python app.py"

    else:
        code = generate_code(prompt)["code"]
        files["main.txt" if code.startswith("⚙️") else "main.code"] = code
        tips = "انسخ الكود وشغّله باللغة المناسبة."

    issues = []
    for name, content in files.items():
        if len(content.strip()) < 20:
            issues.append(f"{name}: المحتوى قصير جداً.")
        if name.endswith(".html") and "<html" not in content.lower():
            issues.append(f"{name}: ملف HTML يبدو ناقص الوسوم الأساسية.")

    return {
        "ok": True,
        "plan": plan_steps(intent),
        "intent": intent,
        "files": files,
        "issues": issues,
        "tips": tips
    }
