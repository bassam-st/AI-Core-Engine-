# main.py — نواة بسّام الذكية المتكاملة
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# 🔧 إعداد التسجيل المتقدم
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("ai-core-engine")

# 🎯 حالة النظام
class SystemStatus:
    def __init__(self):
        self.start_time = datetime.now()
        self.requests_count = 0
        self.modules_status = {}
        self.last_error = None

system_status = SystemStatus()

# 📦 تحميل الوحدات الذكية مع التعافي من الأخطاء
def load_modules_safely():
    """تحميل الوحدات مع التعافي الذكي من الأخطاء"""
    modules = {}
    
    # الوحدات الأساسية (مطلوبة)
    core_modules = {
        'brain': ['chat_answer', 'trigger_learning'],
        'coder': ['generate_code'],
        'memory': ['init_db', 'add_fact', 'search_memory']
    }
    
    # الوحدات المتقدمة (اختيارية)
    advanced_modules = {
        'intent_analyzer': ['analyze_intent'],
        'web_search': ['web_search', 'wiki_summary_ar'],
        'learn_loop': ['continuous_learning_pipeline'],
        'executor': ['execute_task'],
        'analyzer': ['analyze_content']
    }
    
    # تحميل الوحدات الأساسية
    for module_name, functions in core_modules.items():
        try:
            module = __import__(f'core.{module_name}', fromlist=functions)
            loaded_functions = {}
            for func in functions:
                if hasattr(module, func):
                    loaded_functions[func] = getattr(module, func)
                else:
                    logger.warning(f"الوظيفة {func} غير موجودة في {module_name}")
            
            modules[module_name] = {
                'loaded': True,
                'functions': loaded_functions,
                'error': None
            }
            logger.info(f"✅ تم تحميل {module_name} بنجاح")
            
        except Exception as e:
            modules[module_name] = {
                'loaded': False,
                'functions': {},
                'error': str(e)
            }
            logger.error(f"❌ فشل تحميل {module_name}: {e}")
    
    # تحميل الوحدات المتقدمة
    for module_name, functions in advanced_modules.items():
        try:
            module = __import__(f'core.{module_name}', fromlist=functions)
            loaded_functions = {}
            for func in functions:
                if hasattr(module, func):
                    loaded_functions[func] = getattr(module, func)
            
            modules[module_name] = {
                'loaded': True,
                'functions': loaded_functions,
                'error': None
            }
            logger.info(f"✅ تم تحميل {module_name} بنجاح")
            
        except Exception as e:
            modules[module_name] = {
                'loaded': False,
                'functions': {},
                'error': str(e)
            }
            logger.warning(f"⚠️ وحدة {module_name} غير متاحة: {e}")
    
    return modules

# تحميل جميع الوحدات
MODULES = load_modules_safely()
system_status.modules_status = {name: info['loaded'] for name, info in MODULES.items()}

# 🚀 تطبيق FastAPI
app = FastAPI(
    title="النواة الذكية - بسّام",
    description="منصة ذكاء اصطناعي متكاملة للبرمجة، التحليل، والتعلم الذاتي",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json"
)

# 🌍 إعدادات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 إعداد الملفات الثابتة والقوالب
try:
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")
    logger.info("✅ تم إعداد المجلدات الثابتة بنجاح")
except Exception as e:
    logger.warning(f"⚠️ مشكلة في المجلدات الثابتة: {e}")
    templates = None

# 🗃️ حدث بدء التشغيل
@app.on_event("startup")
async def startup_event():
    """تهيئة النظام عند البدء"""
    try:
        # تهيئة قاعدة البيانات إذا كانت الذاكرة متاحة
        if MODULES['memory']['loaded']:
            MODULES['memory']['functions']['init_db']()
            logger.info("✅ تم تهيئة قاعدة البيانات")
        
        # إنشاء المجلدات اللازمة
        os.makedirs("knowledge", exist_ok=True)
        os.makedirs("projects", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        logger.info("🚀 النظام جاهز للعمل!")
        
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة النظام: {e}")

# 🏠 الصفحة الرئيسية - واجهة احترافية
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """الصفحة الرئيسية مع لوحة تحكم تفاعلية"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>النواة الذكية - بسّام</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }
            .logo {
                font-size: 4em;
                margin-bottom: 15px;
            }
            h1 {
                color: #4CAF50;
                margin-bottom: 10px;
                font-size: 2.8em;
            }
            .subtitle {
                color: #666;
                font-size: 1.3em;
                margin-bottom: 20px;
            }
            .dashboard {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }
            .card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
            }
            .card:hover {
                transform: translateY(-5px);
            }
            .card h3 {
                color: #333;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .module-list {
                list-style: none;
            }
            .module-item {
                padding: 12px;
                margin: 8px 0;
                background: #f8f9fa;
                border-radius: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .status-online { color: #4CAF50; }
            .status-offline { color: #f44336; }
            .btn {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 14px 28px;
                border: none;
                border-radius: 50px;
                text-decoration: none;
                font-size: 1.1em;
                margin: 8px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(76, 175, 80, 0.3);
            }
            .btn-secondary {
                background: #2196F3;
            }
            .btn-danger {
                background: #f44336;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .stat-item {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #4CAF50;
            }
            .chat-demo {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                margin-top: 20px;
            }
            .chat-input {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 25px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🧠</div>
                <h1>النواة الذكية - بسّام</h1>
                <p class="subtitle">منصة ذكاء اصطناعي متكاملة للبرمجة والتحليل</p>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number" id="modulesCount">0</div>
                        <div>الوحدات النشطة</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="uptime">0</div>
                        <div>ثانية من التشغيل</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="requestsCount">0</div>
                        <div>طلب معالج</div>
                    </div>
                </div>
                
                <div>
                    <a href="/docs" class="btn">
                        <i class="fas fa-book"></i> الوثائق التفاعلية
                    </a>
                    <a href="/api/system/status" class="btn btn-secondary">
                        <i class="fas fa-chart-bar"></i> حالة النظام
                    </a>
                    <a href="/api/endpoints" class="btn">
                        <i class="fas fa-list"></i> نقاط الخدمة
                    </a>
                </div>
            </div>
            
            <div class="dashboard">
                <div class="card">
                    <h3><i class="fas fa-brain"></i> الوحدات النشطة</h3>
                    <ul class="module-list" id="modulesList">
                        <!-- سيتم ملؤها بالجافاسكريبت -->
                    </ul>
                </div>
                
                <div class="card">
                    <h3><i class="fas fa-rocket"></i> الخدمات السريعة</h3>
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <button class="btn" onclick="testChat()">
                            <i class="fas fa-comment"></i> اختبار الدردشة
                        </button>
                        <button class="btn btn-secondary" onclick="testCoder()">
                            <i class="fas fa-code"></i> توليد كود
                        </button>
                        <button class="btn" onclick="testSearch()">
                            <i class="fas fa-search"></i> بحث ذكي
                        </button>
                    </div>
                </div>
                
                <div class="card">
                    <h3><i class="fas fa-terminal"></i> تجربة سريعة</h3>
                    <div class="chat-demo">
                        <input type="text" class="chat-input" id="demoInput" 
                               placeholder="اكتب رسالة هنا...">
                        <button class="btn" onclick="sendDemoMessage()">
                            <i class="fas fa-paper-plane"></i> إرسال
                        </button>
                        <div id="demoResponse" style="margin-top: 15px; padding: 15px; background: white; border-radius: 10px;"></div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // تحديث الإحصائيات
            function updateStats() {
                fetch('/api/system/status')
                    .then(r => r.json())
                    .then(data => {
                        if (data.ok) {
                            document.getElementById('modulesCount').textContent = 
                                Object.values(data.modules).filter(Boolean).length;
                            document.getElementById('requestsCount').textContent = 
                                data.requests_count || 0;
                            document.getElementById('uptime').textContent = 
                                Math.floor((new Date() - new Date(data.start_time)) / 1000);
                            
                            // تحديث قائمة الوحدات
                            const modulesList = document.getElementById('modulesList');
                            modulesList.innerHTML = '';
                            for (const [module, status] of Object.entries(data.modules)) {
                                const li = document.createElement('li');
                                li.className = 'module-item';
                                li.innerHTML = `
                                    <span>${module}</span>
                                    <span class="${status ? 'status-online' : 'status-offline'}">
                                        <i class="fas fa-${status ? 'check-circle' : 'times-circle'}"></i>
                                        ${status ? 'نشط' : 'غير نشط'}
                                    </span>
                                `;
                                modulesList.appendChild(li);
                            }
                        }
                    });
            }
            
            // اختبار الدردشة
            async function testChat() {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: 'مرحباً! قدم نفسك'})
                });
                const data = await response.json();
                alert(data.reply || 'تم الاختبار!');
            }
            
            // اختبار مولد الأكواد
            async function testCoder() {
                const response = await fetch('/api/code/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({description: 'دالة Python لجمع رقمين'})
                });
                const data = await response.json();
                if (data.ok) {
                    alert('✅ تم توليد الكود بنجاح!');
                } else {
                    alert('❌ ' + (data.reply || data.error));
                }
            }
            
            // إرسال رسالة تجريبية
            async function sendDemoMessage() {
                const input = document.getElementById('demoInput');
                const responseDiv = document.getElementById('demoResponse');
                
                if (!input.value.trim()) {
                    alert('الرجاء إدخال رسالة');
                    return;
                }
                
                responseDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري المعالجة...';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: input.value})
                    });
                    const data = await response.json();
                    
                    if (data.ok) {
                        responseDiv.innerHTML = `
                            <strong>✅ الرد:</strong><br>
                            <div style="margin-top: 10px;">${data.reply}</div>
                        `;
                    } else {
                        responseDiv.innerHTML = `
                            <strong>❌ خطأ:</strong><br>
                            <div style="margin-top: 10px;">${data.reply || data.error}</div>
                        `;
                    }
                } catch (error) {
                    responseDiv.innerHTML = `<strong>❌ خطأ في الاتصال:</strong> ${error}`;
                }
            }
            
            // تحديث كل 5 ثواني
            updateStats();
            setInterval(updateStats, 5000);
            
            // تفعيل زر الإدخال عند الضغط على Enter
            document.getElementById('demoInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendDemoMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 💬 نقطة الدردشة الرئيسية
@app.post("/api/chat")
async def api_chat(request: Request):
    """معالجة طلبات الدردشة الذكية"""
    system_status.requests_count += 1
    
    try:
        data = await request.json()
        message = (data.get("message") or "").strip()
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "empty_message", "reply": "الرجاء إدخال رسالة."}
            )
        
        # استخدام محلل النية إذا كان متاحاً
        intent = "general"
        if MODULES['intent_analyzer']['loaded']:
            try:
                intent_result = MODULES['intent_analyzer']['functions']['analyze_intent'](message)
                intent = intent_result.get('intent', 'general')
            except Exception as e:
                logger.warning(f"⚠️ خطأ في تحليل النية: {e}")
        
        # المعالجة عبر الدماغ الرئيسي
        if MODULES['brain']['loaded']:
            reply = MODULES['brain']['functions']['chat_answer'](message)
        else:
            reply = "🧠 أنا النواة الذكية - نظام الذكاء الاصطناعي المتكامل. كيف يمكنني مساعدتك اليوم؟"
        
        logger.info(f"💬 دردشة: '{message[:50]}...' → النية: {intent}")
        
        return {
            "ok": True,
            "reply": reply,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في الدردشة: {e}")
        system_status.last_error = str(e)
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "chat_error",
                "reply": "⚠️ حدث خطأ في المعالجة. يرجى المحاولة مرة أخرى."
            }
        )

# 💻 توليد الأكواد
@app.post("/api/code/generate")
async def api_code_generate(request: Request):
    """توليد أكواد برمجية بناءً على الوصف"""
    system_status.requests_count += 1
    
    try:
        data = await request.json()
        description = (data.get("description") or "").strip()
        
        if not description:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "empty_description", "reply": "الرجاء وصف الكود المطلوب."}
            )
        
        if not MODULES['coder']['loaded']:
            return JSONResponse(
                status_code=503,
                content={"ok": False, "error": "coder_unavailable", "reply": "خدمة توليد الأكواد غير متاحة حالياً."}
            )
        
        result = MODULES['coder']['functions']['generate_code'](description)
        
        logger.info(f"💻 تم توليد كود: '{description[:50]}...'")
        
        return {
            "ok": True,
            "result": result,
            "reply": f"✅ تم توليد الكود بنجاح! 📝 {result.get('title', 'كود مخصص')}"
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في توليد الكود: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "code_generation_error",
                "reply": "❌ حدث خطأ في توليد الكود. حاول مرة أخرى."
            }
        )

# 🔍 البحث الذكي
@app.post("/api/search")
async def api_search(request: Request):
    """الب
