# main.py - نسخة خالية من المشاكل
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def home():
    return HTMLResponse("""
    <html dir='rtl'>
    <head>
        <title>النواة الذكية</title>
        <style>
            body { 
                font-family: Arial; 
                background: #f0f0f0;
                margin: 0; 
                padding: 40px;
                text-align: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                max-width: 600px;
                margin: 0 auto;
            }
            h1 { color: #4CAF50; }
            .btn {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                margin: 10px;
                text-decoration: none;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 النواة الذكية</h1>
            <p><strong>✅ النظام يعمل بنجاح!</strong></p>
            <p>منصة الذكاء الاصطناعي المتكاملة</p>
            <div>
                <a href="/docs" class="btn">الوثائق</a>
                <a href="/chat" class="btn">الدردشة</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/chat")
async def chat():
    return {
        "message": "مرحباً! أنا النواة الذكية جاهز للمساعدة",
        "status": "active"
    }

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "النظام يعمل"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
