# core/agents/reviewer.py — مراجعة سريعة للملفات الناتجة
from __future__ import annotations

def review(files: dict[str,str]) -> list[str]:
    issues: list[str] = []
    for name, content in files.items():
        if name.endswith(".html") and "<html" not in content.lower():
            issues.append(f"{name}: ملف HTML بدون وسم <html>.")
        if name.endswith(".py") and "def " not in content and "print(" not in content:
            issues.append(f"{name}: سكربت بايثون بسيط بلا دالة/طباعة.")
        if len(content.strip()) < 20:
            issues.append(f"{name}: المحتوى قصير جدًا.")
    return issues
