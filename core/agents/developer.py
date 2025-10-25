# core/agents/developer.py — يُنشئ ملفات المشروع
from __future__ import annotations
from textwrap import dedent
from core.coder import generate_code

def build_files(goal: str, hints: list[str]) -> dict[str, str]:
    """
    يُرجع قاموس {اسم_ملف: محتوى}.
    يحاول استنتاج النوع: موقع (HTML/CSS/JS) أو سكربت Python.
    """
    g = goal.lower()
    files: dict[str, str] = {}

    if any(w in g for w in ["موقع","صفحة","html","landing"]):
        html = generate_code("html ترحيب")["code"]
        css = dedent("""
        body{font-family:system-ui;background:#0b1220;color:#e7ecff;margin:0}
        .container{max-width:820px;margin:8vh auto;padding:24px}
        .card{background:#121b2d;border:1px solid #1e2b44;border-radius:14px;padding:24px}
        a{color:#9bd1ff}
        """).strip()
        js = 'console.log("Site ready!");'
        files["index.html"] = html
        files["style.css"]  = css
        files["main.js"]    = js
        return files

    # افتراضي: بايثون
    code = generate_code("بايثون اطبع مرحبا")["code"]
    files["app.py"] = code
    return files
