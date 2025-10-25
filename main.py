# main.py — نواة بسّام الذكية: واجهة + دردشة + فريق إنشاء المشاريع + تعلم تلقائي
from __future__ import annotations
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from typing import Dict, Any

# 🔧 إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("al-core-engine")

# 📦 استيراد جميع الوحدات مع معالجة الأخطاء
try:
    from core.brain import chat_answer, trigger_learning
    from core.memory import init_db, add_fact, search_memory, manage_memory_size
    from core.learn_loop import run_once, continuous_learning_pipeline, learn_from_conversations
    from core.code_team import build_project
    from core.coder import generate_code
    from core.web_search import web_search, wiki_summary_ar
    MODULES_LOADED = True
    logger.info("✅ جميع الوحدات تم تحميلها بنجاح")
except ImportError as e:
    logger.warning(f"⚠️ بعض الوحدات غير متوفرة: {e}")
    MODULES_LOADED = False

app = FastAPI(
    title="AI Core Engine — Bassam", 
    version="2.0.0",
    description="نواة ذكية قابلة للتعلم الذاتي - بحث، تحليل، توليد أكواد، وإنشاء مشاريع"
)

# 🌍 CORS للتواصل مع الواجهات
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 مجلدات الثابت والقوالب
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    logger.info("✅ مجلدات static و templates جاهزة")
except Exception as e:
    logger.warning(f"⚠️ مشكلة في مجلدات الثابت: {e}")
    templates = None

# 🗃️ تهيئة النظام
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        logger.info("✅ قاعدة البيانات مهيأة")
        
        # إنشاء مجلد knowledge إذا لم يكن موجوداً
        os.makedirs("knowledge", exist_ok=True)
        logger.info("✅ مجلد knowledge جاهز")
        
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة النظام: {e}")

# 🏠 الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    try:
        if templates:
            return templates.TemplateResponse("index.html", {"request": request})
        else:
            return HTMLResponse("""
            <html dir='rtl'>
                <head><title>نواة بسّام الذكية</title></head>
                <body>
                    <h1>🧠 نواة بسّام الذكية - Al-Core-Engine</h1>
                    <p>النظام يعمل بنجاح! الإصدار 2.0.0</p>
                    <p><a href='/docs'>التوثيق التفاعلي</a></p>
                </body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(f"<h1>النظام يعمل</h1><p>خطأ في القالب: {e}</p>")

# 💬 دردشة الذكاء الرئيسية
@app.post("/api/chat")
async def api_chat(request: Request):
    try:
        if not MODULES_LOADED:
            return JSONResponse(
                status_code=200,
                content={"ok": False, "error": "modules_not_loaded", "reply": "النظام قيد التهيئة..."}
            )
        
        data = await request.json()
        msg = (data.get("message") or "").strip()
        
        if not msg:
            return {"ok": False, "error": "empty_message", "reply": "الرجاء إدخال رسالة"}
        
        # معالجة الرسالة عبر الدماغ الرئيسي
        reply, sources = chat_answer(msg)
        
        return {
            "ok": True, 
            "reply": reply, 
            "sources": sources,
            "modules_used": len(sources) > 0
        }
        
    except Exception as e:
        logger.error(f"خطأ في الدردشة: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "ok": False, 
                "error": "internal_error", 
                "detail": str(e)[:200],
                "reply": "حدث خطأ في المعالجة. الرجاء المحاولة مرة أخرى."
            },
        )

# 🧠 إدارة التعلم والذاكرة
@app.post("/api/learn")
async def api_learn(request: Request):
    try:
        data = await request.json()
        txt = (data.get("text") or "").strip()
        src = (data.get("source") or "manual").strip()
        
        if not txt:
            return {"ok": False, "error": "empty_text"}
        
        add_fact(txt, source=src)
        
        return {"ok": True, "added": 1, "message": "تمت إضافة المعلومة إلى الذاكرة"}
        
    except Exception as e:
        logger.error(f"خطأ في إضافة المعرفة: {e}")
        return JSONResponse(
            status_code=200,
            content={"ok": False, "error": "internal_error", "detail": str(e)[:200]},
        )

# 🔍 البحث في الذاكرة
@app.get("/api/memory/search")
async def api_memory_search(q: str = "", limit: int = 5):
    try:
        if not q:
            return {"ok": False, "error": "empty_query"}
        
        results = search_memory(q, limit=limit)
        
        return {
            "ok": True, 
            "query": q, 
            "results": results, 
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"خطأ في البحث: {e}")
        return {"ok": False, "error": str(e)[:200]}

# 🚀 فريق الإنشاء: يخطّط/يبحث/ينتج ملفات
@app.post("/api/team/build")
async def api_team_build(request: Request):
    try:
        if not MODULES_LOADED:
            return {"ok": False, "error": "code_team_not_available"}
        
        data = await request.json()
        goal = (data.get("goal") or "").strip()
        
        if not goal:
            return {"ok": False, "error": "empty_goal"}
        
        result = build_project(goal)
        logger.info(f"تم بناء مشروع: {goal}")
        
        return result
        
    except Exception as e:
        logger.error(f"خطأ في بناء المشروع: {e}")
        return JSONResponse(
            status_code=200,
            content={"ok": False, "error": "internal_error", "detail": str(e)[:200]},
        )

# ⚡ توليد كود مباشر
@app.post("/api/code/generate")
async def api_code_generate(request: Request):
    try:
        if not MODULES_LOADED:
            return {"ok": False, "error": "coder_not_available"}
        
        data = await request.json()
        description = (data.get("description") or "").strip()
        
        if not description:
            return {"ok": False, "error": "empty_description"}
        
        result = generate_code(description)
        logger.info(f"تم توليد كود: {description[:50]}...")
        
        return {"ok": True, "result": result}
        
    except Exception as e:
        logger.error(f"خطأ في توليد الكود: {e}")
        return {"ok": False, "error": str(e)[:200]}

# 🔄 التعلم التلقائي
@app.post("/api/learning/trigger")
async def api_learning_trigger():
    try:
        if not MODULES_LOADED:
            return {"ok": False, "error": "learning_modules_not_available"}
        
        result = continuous_learning_pipeline()
        
        return {
            "ok": True, 
            "message": "تمت عملية التعلم التلقائي",
            "details": result
        }
        
    except Exception as e:
        logger.error(f"خطأ في التعلم التلقائي: {e}")
        return {"ok": False, "error": str(e)[:200]}

# 📊 حالة النظام
@app.get("/api/system/status")
async def api_system_status():
    try:
        from core.memory import _memory_cache
        
        status = {
            "ok": True,
            "status": "running",
            "version": "2.0.0",
            "modules_loaded": MODULES_LOADED,
            "memory_facts": len(_memory_cache) if MODULES_LOADED else 0,
            "system": "Al-Core-Engine Enhanced"
        }
        
        return status
        
    except Exception as e:
        logger.error(f"خطأ في حالة النظام: {e}")
        return {"ok": False, "status": "error", "detail": str(e)[:200]}

# 🗃️ إدارة الذاكرة
@app.post("/api/memory/cleanup")
async def api_memory_cleanup():
    try:
        manage_memory_size()
        from core.memory import _memory_cache
        
        return {
            "ok": True,
            "message": "تمت إدارة الذاكرة",
            "current_facts": len(_memory_cache)
        }
        
    except Exception as e:
        logger.error(f"خطأ في تنظيف الذاكرة: {e}")
        return {"ok": False, "error": str(e)[:200]}

# 🏓 اختبار النظام
@app.get("/ping")
def ping():
    return {
        "status": "alive", 
        "message": "نظام النواة يعمل ✅",
        "version": "2.0.0",
        "modules": MODULES_LOADED
    }

# 📋 توثيق API
@app.get("/api/endpoints")
async def api_endpoints():
    endpoints = [
        {"path": "/api/chat", "method": "POST", "description": "الدردشة الذكية الرئيسية"},
        {"path": "/api/learn", "method": "POST", "description": "إضافة معرفة يدوية"},
        {"path": "/api/memory/search", "method": "GET", "description": "البحث في الذاكرة"},
        {"path": "/api/team/build", "method": "POST", "description": "بناء مشروع كامل"},
        {"path": "/api/code/generate", "method": "POST", "description": "توليد كود مباشر"},
        {"path": "/api/learning/trigger", "method": "POST", "description": "تشغيل التعلم التلقائي"},
        {"path": "/api/system/status", "method": "GET", "description": "حالة النظام"},
        {"path": "/api/memory/cleanup", "method": "POST", "description": "إدارة الذاكرة"},
    ]
    return {"endpoints": endpoints}

# 🚀 تشغيل الخادم
if __name__ == "__main__":
    logger.info("🚀 بدء تشغيل نواة بسّام الذكية...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True
    )
