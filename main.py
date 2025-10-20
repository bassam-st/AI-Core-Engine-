#!/usr/bin/env python3
# النواة الذكية المتقدمة - AI Core Engine
# نسخة متوافقة مع Render

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template

# إضافة المسارات للمشروع
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

app = Flask(__name__)

try:
    from core.brain import AICoreBrain
    ai_core = AICoreBrain()
    CORE_LOADED = True
except ImportError as e:
    print(f"⚠️  تحذير: تعذر تحميل النواة المتقدمة: {e}")
    CORE_LOADED = False

class BasicAICore:
    def __init__(self):
        self.setup_directories()
        
    def setup_directories(self):
        """إنشاء المجلدات الضرورية"""
        dirs = ['knowledge', 'memory', 'logs']
        for dir_name in dirs:
            os.makedirs(dir_name, exist_ok=True)
    
    def process_message(self, message):
        """معالجة الرسالة الأساسية"""
        message_lower = message.lower()
        
        responses = {
            'greeting': "مرحباً بك! 👋 أنا النواة الذكية على Render. كيف يمكنني مساعدتك؟",
            'programming': "💻 مجال البرمجة! أستطيع مساعدتك في:\n• Python\n• تطبيقات ويب\n• سكريبتات أتمتة\n• حل مشاكل برمجية",
            'networking': "🌐 مجال الشبكات! أستطيع:\n• شرح مفاهيم الشبكات\n• تحليل مشاكل الاتصال\n• تصميم شبكات",
            'systems': "🖥️ مجال الأنظمة! أستطيع:\n• إدارة الخوادم\n• تحليل الأداء\n• حل مشاكل النظام",
            'security': "🔒 الأمن السيبراني! أستطيع:\n• تحليل الثغرات\n• نصائح أمنية\n• تأمين التطبيقات",
            'default': f"🧠 أفهم أنك تقول: '{message}'. أستطيع مساعدتك في البرمجة، الشبكات، الأنظمة، والأمن السيبراني."
        }
        
        if any(word in message_lower for word in ['مرحب', 'اهلا', 'سلام']):
            return responses['greeting']
        elif any(word in message_lower for word in ['برمجة', 'كود', 'code']):
            return responses['programming']
        elif any(word in message_lower for word in ['شبكة', 'network']):
            return responses['networking']
        elif any(word in message_lower for word in ['نظام', 'system']):
            return responses['systems']
        elif any(word in message_lower for word in ['أمن', 'security']):
            return responses['security']
        else:
            return responses['default']

# إنشاء نسخة من النواة
if CORE_LOADED:
    ai_engine = ai_core
else:
    ai_engine = BasicAICore()

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>النواة الذكية - AI Core Engine</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                color: #2c3e50;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                color: #7f8c8d;
                font-size: 1.2em;
            }
            .chat-container {
                border: 2px solid #e0e0e0;
                border-radius: 15px;
                padding: 20px;
                background: white;
                margin-bottom: 20px;
            }
            .messages {
                height: 300px;
                overflow-y: auto;
                margin-bottom: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            .message {
                margin-bottom: 15px;
                padding: 12px;
                border-radius: 10px;
                max-width: 80%;
            }
            .user-message {
                background: #007bff;
                color: white;
                margin-left: auto;
                text-align: left;
            }
            .bot-message {
                background: #e9ecef;
                color: #333;
                margin-right: auto;
                white-space: pre-line;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            input[type="text"] {
                flex: 1;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus {
                border-color: #007bff;
            }
            button {
                padding: 15px 25px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }
            button:hover {
                background: #0056b3;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }
            .feature {
                background: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s;
            }
            .feature:hover {
                transform: translateY(-5px);
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 النواة الذكية</h1>
                <p>AI Core Engine - نظام ذكي متكامل للبرمجة، الشبكات، والأنظمة</p>
            </div>
            
            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message bot-message">
                        مرحباً! 👋 أنا النواة الذكية. أستطيع مساعدتك في:
                        • البرمجة والتطوير
                        • الشبكات والاتصالات  
                        • إدارة الأنظمة
                        • الأمن السيبراني
                        • إدارة المشاريع
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" id="userInput" placeholder="اكتب رسالتك هنا..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">إرسال</button>
                </div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">💻</div>
                    <h3>البرمجة</h3>
                    <p>توليد الأكواد وحل المشاكل البرمجية</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🌐</div>
                    <h3>الشبكات</h3>
                    <p>تحليل الشبكات وحل مشاكل الاتصال</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🖥️</div>
                    <h3>الأنظمة</h3>
                    <p>إدارة الأنظمة ومراقبة الأداء</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔒</div>
                    <h3>الأمن</h3>
                    <p>تحليل الثغرات وتأمين الأنظمة</p>
                </div>
            </div>
        </div>

        <script>
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            function sendMessage() {
                const userInput = document.getElementById('userInput');
                const message = userInput.value.trim();
                
                if (!message) return;

                // إضافة رسالة المستخدم
                addMessage(message, 'user');
                userInput.value = '';

                // إرسال للخادم
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.response, 'bot');
                })
                .catch(error => {
                    addMessage('❌ حدث خطأ في الاتصال', 'bot');
                    console.error('Error:', error);
                });
            }

            function addMessage(text, sender) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = text;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """واجهة المحادثة مع النواة الذكية"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'لا يوجد رسالة'}), 400
        
        # معالجة الرسالة
        if hasattr(ai_engine, 'process_message'):
            if CORE_LOADED:
                response_data = ai_engine.process_message(user_message, 'web_user')
                response_text = response_data['message']
            else:
                response_text = ai_engine.process_message(user_message)
        else:
            response_text = "النظام قيد التطوير..."
        
        return jsonify({
            'response': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"خطأ في معالجة الرسالة: {e}")
        return jsonify({'error': 'حدث خطأ في المعالجة'}), 500

@app.route('/api/health')
def health_check():
    """فحص صحة التطبيق"""
    return jsonify({
        'status': 'running',
        'core_loaded': CORE_LOADED,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
