#!/usr/bin/env python3
# النواة الذكية - إصدار مبسط للنشر

import os
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

class SimpleAICore:
    def process_message(self, message):
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['مرحب', 'اهلا', 'سلام']):
            return "مرحباً بك! 👋 أنا النواة الذكية على Render. كيف يمكنني مساعدتك؟"
        
        elif any(word in message_lower for word in ['برمجة', 'كود', 'بايثون']):
            return "💻 مجال البرمجة! أستطيع مساعدتك في كتابة أكواد Python وتطوير التطبيقات."
        
        elif any(word in message_lower for word in ['شبكة', 'انترنت', 'اتصال']):
            return "🌐 مجال الشبكات! أستطيع شرح مفاهيم الشبكات وتحليل مشاكل الاتصال."
        
        elif any(word in message_lower for word in ['نظام', 'خادم', 'سيرفر']):
            return "🖥️ مجال الأنظمة! أستطيع مساعدتك في إدارة الأنظمة ومراقبة الأداء."
        
        else:
            return f"🧠 أفهم أنك تقول: '{message}'. أستطيع مساعدتك في البرمجة، الشبكات، والأنظمة."

ai_core = SimpleAICore()

@app.route('/')
def home():
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
                background: linear-gradient(135deg, #667eea, #764ba2);
                margin: 0;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .chat-box {
                border: 2px solid #ddd;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                background: #f9f9f9;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 النواة الذكية</h1>
                <p>AI Core Engine - الإصدار المبسط</p>
            </div>
            
            <div class="chat-box" id="chatBox">
                <div><strong>النواة:</strong> مرحباً! أنا جاهز للمساعدة.</div>
            </div>
            
            <input type="text" id="userInput" placeholder="اكتب رسالتك هنا..." onkeypress="if(event.key=='Enter') sendMessage()">
            <button onclick="sendMessage()">إرسال</button>
        </div>

        <script>
            function sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value.trim();
                if (!message) return;
                
                // عرض رسالة المستخدم
                const chatBox = document.getElementById('chatBox');
                chatBox.innerHTML += `<div style='text-align: left; margin: 10px 0;'><strong>أنت:</strong> ${message}</div>`;
                
                // إرسال للخادم
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                })
                .then(r => r.json())
                .then(data => {
                    chatBox.innerHTML += `<div style='margin: 10px 0;'><strong>النواة:</strong> ${data.response}</div>`;
                    chatBox.scrollTop = chatBox.scrollHeight;
                })
                .catch(error => {
                    chatBox.innerHTML += `<div style='color: red;'><strong>خطأ:</strong> تعذر الاتصال</div>`;
                });
                
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        response = ai_core.process_message(user_message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'response': '⚠️ حدث خطأ في المعالجة',
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'running',
        'service': 'AI Core Engine',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
