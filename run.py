#!/usr/bin/env python3
"""
ملف تشغيل نواة بسّام الذكية
تشغيل: python run.py
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 بدء تشغيل نواة بسّام الذكية - Al-Core-Engine")
    print("📍 الخادم يعمل على: http://localhost:8000")
    print("📚 التوثيق التفاعلي: http://localhost:8000/docs")
    print("💬 واجهة الشات: http://localhost:8000")
    print("🛑 لإيقاف الخادم: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
