# main.py - أبسط نسخة مؤكدة العمل
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="النواة الذكية")

@app.get("/")
async def home():
    return HTMLResponse("""
    <html>
    <head><title>النواة الذكية</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🧠 النواة الذكية</h1>
        <p><strong>✅ النظام يعمل بنجاح!</strong></p>
        <p>منصة الذكاء الاصطناعي المتكاملة</p>
        <p>
            <a href="/docs" style="margin: 10px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">الوثائق</a>
            <a href="/ping" style="margin: 10px; padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px;">اختبار</a>
        </p>
    </body>
    </html>
    """)

@app.get("/ping")
async def ping():
    return {"status": "active", "message": "✅ النظام يعمل"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
