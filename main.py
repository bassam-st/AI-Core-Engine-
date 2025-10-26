# main.py - نسخة مؤكدة العمل
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(
    title="النواة الذكية - بسام",
    description="منصة ذكاء اصطناعي متكاملة",
    version="1.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>النواة الذكية</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
            }
            h1 {
                color: #4CAF50;
                margin-bottom: 20px;
            }
            .btn {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 12px 25px;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 النواة الذكية</h1>
            <p>✅ النظام يعمل بنجاح!</p>
            <p>منصة الذكاء الاصطناعي المتكاملة</p>
            <div>
                <a href="/docs" class="btn">📚 الوثائق</a>
                <a href="/api/chat" class="btn">💬 الدردشة</a>
            </div>
        </div>
    </body>
    </html>
    """

# نقطة الدردشة الأساسية
@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if "موقع" in message or "ويب" in message:
            response = "🛠️ سأبني لك موقع ويب رائع! هذا كود HTML مبتدئ:\n\n```html\n<!DOCTYPE html>\n<html>\n<head>\n    <title>موقعي</title>\n</head>\n<body>\n    <h1>مرحباً!</h1>\n</body>\n</html>\n```"
        elif "دالة" in message or "برمجة" in message:
            response = "🐍 هذا كود Python لدالة الجمع:\n\n```python\ndef جمع(أ, ب):\n    return أ + ب\n\nنتيجة = جمع(5, 3)\nprint(نتيجة)  # 8\n```"
        else:
            response = "🧠 أهلاً! أنا النواة الذكية. يمكنني مساعدتك في:\n• برمجة وتطوير المواقع\n• كتابة الأكواد\n• شرح مفاهيم البرمجة\n\nما الذي تريد أن أصنعه لك؟"
        
        return JSONResponse({
            "ok": True,
            "reply": response,
            "intent": "understood"
        })
        
    except Exception as e:
        return JSONResponse({
            "ok": False,
            "reply": "⚠️ حدث خطأ. حاول مرة أخرى.",
            "error": str(e)
        })

# نقطة الصحية
@app.get("/ping")
async def ping():
    return {"status": "active", "message": "✅ النظام يعمل", "version": "1.0.0"}

# نقطة حالة النظام
@app.get("/api/status")
async def status():
    return {
        "status": "running",
        "version": "1.0.0",
        "modules": ["chat", "code_generation"],
        "ready": True
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
