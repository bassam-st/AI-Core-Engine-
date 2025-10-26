# main.py - نسخة مؤقتة للتأكد من العمل
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="النواة الذكية")

@app.get("/")
async def home():
    return HTMLResponse("""
    <html dir='rtl'>
        <head><title>النواة الذكية</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🧠 النواة الذكية تعمل!</h1>
            <p>✅ النظام يعمل بنجاح - الإصدار الأساسي</p>
            <p><a href='/docs'>الوثائق التفاعلية</a></p>
            <p><a href='/ping'>اختبار الخدمة</a></p>
        </body>
    </html>
    """)

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "النظام يعمل ✅", "version": "1.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
