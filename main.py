#!/usr/bin/env python3
# النواة الذكية المتقدمة - بنماذج مفتوحة المصدر

import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import numpy as np
import nltk
from sentence_transformers import SentenceTransformer, util

# تحميل نماذج مفتوحة المصدر
try:
    # نموذج للفهم الدلالي (أخف وأسرع)
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    MODEL_LOADED = True
except:
    MODEL_LOADED = False

app = Flask(__name__)

class AdvancedAICore:
    def __init__(self):
        self.setup_directories()
        self.load_knowledge()
        self.setup_nltk()
        self.conversation_history = []
        
    def setup_directories(self):
        """إنشاء المجلدات الضرورية"""
        os.makedirs('knowledge', exist_ok=True)
        os.makedirs('memory', exist_ok=True)
        os.makedirs('models', exist_ok=True)
    
    def setup_nltk(self):
        """إعداد NLTK"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def load_knowledge(self):
        """تحميل المعرفة الموسعة"""
        try:
            with open('knowledge/advanced_knowledge.json', 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
        except:
            self.knowledge = {
                "qa_pairs": {
                    "برمجة": {
                        "ما هو بايثون؟": "بايثون لغة برمجة عالية المستوى سهلة التعلم، تستخدم في تطوير الويب، تحليل البيانات، الذكاء الاصطناعي، والأتمتة.",
                        "كيف أنشئ موقع ويب؟": "لإنشاء موقع ويب: 1) تعلم HTML/CSS/JavaScript 2) اختر إطار عمل مثل Flask أو Django 3) استخدم قواعد البيانات 4) انشر على خادم ويب",
                        "ما الفرق بين list و tuple؟": "List قابلة للتعديل، Tuple ثابتة لا يمكن تعديلها. List تستخدم [] و Tuple تستخدم ()"
                    },
                    "شبكات": {
                        "ما هو IP؟": "عنوان IP هو عنوان فريد يحدد جهازك على الشبكة، مثل عنوان المنزل في العالم الحقيقي.",
                        "كيف يعمل DNS؟": "DNS يحول أسماء النطاقات (مثل google.com) إلى عناوين IP رقمية يمكن للأجهزة فهمها.",
                        "ما الفرق بين TCP و UDP؟": "TCP موثوق مع تأكيد الاستلام، UDP سريع بدون تأكيد - مناسب للمكالمات الصوتية والفيديو"
                    },
                    "أنظمة": {
                        "ما هو Linux؟": "Linux نظام تشغيل مفتوح المصدر، مستقر وآمن، يستخدم في الخوادم والأجهزة المدمجة.",
                        "كيف أراقب أداء النظام؟": "استخدم أدوات مثل: top, htop, ps, vmstat لمراقبة استخدام المعالج والذاكرة والقرص.",
                        "ما هي الحاوية؟": "الحاوية (Container) حزمة تحتوي على تطبيق وكل اعتماداته، تعمل بشكل معزول عن النظام المضيف."
                    }
                },
                "code_templates": {
                    "python_web": """from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return {'message': 'مرحباً من API!'}

if __name__ == '__main__':
    app.run(debug=True)""",
                    
                    "python_data_analysis": """import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# تحميل البيانات
data = pd.read_csv('data.csv')

# تحليل أساسي
print("معلومات البيانات:")
print(data.info())
print("\\nالإحصائيات:")
print(data.describe())

# تصور البيانات
plt.figure(figsize=(10, 6))
data.plot()
plt.title('تحليل البيانات')
plt.show()""",
                    
                    "html_responsive": """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>موقعي المتجاوب</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 1rem; text-align: center; }
        @media (max-width: 768px) {
            .container { padding: 10px; }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>مرحباً بك في موقعي</h1>
    </header>
    <div class="container">
        <p>هذا موقع متجاوب يعمل على جميع الأجهزة</p>
    </div>
</body>
</html>"""
                },
                "user_profiles": {},
                "learning_data": {}
            }
            self.save_knowledge()
    
    def save_knowledge(self):
        """حفظ المعرفة"""
        try:
            with open('knowledge/advanced_knowledge.json', 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def semantic_similarity(self, text1, text2):
        """حساب التشابه الدلالي بين نصين"""
        if not MODEL_LOADED:
            # طريقة بديلة بسيطة
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            common = words1.intersection(words2)
            return len(common) / max(len(words1), len(words2))
        
        # استخدام نموذج الجمل المحمل
        emb1 = semantic_model.encode(text1, convert_to_tensor=True)
        emb2 = semantic_model.encode(text2, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(emb1, emb2)
        return similarity.item()
    
    def find_best_answer(self, question, category=None):
        """إيجاد أفضل إجابة باستخدام التشابه الدلالي"""
        best_score = 0
        best_answer = None
        
        if category and category in self.knowledge["qa_pairs"]:
            categories = [category]
        else:
            categories = self.knowledge["qa_pairs"].keys()
        
        for cat in categories:
            for q, a in self.knowledge["qa_pairs"][cat].items():
                score = self.semantic_similarity(question, q)
                if score > best_score:
                    best_score = score
                    best_answer = a
        
        return best_answer if best_score > 0.3 else None
    
    def analyze_intent(self, message):
        """تحليل النية باستخدام نماذج متقدمة"""
        message_lower = message.lower()
        
        intents = {
            "code_generation": ["أنشئ", "اصنع", "اكتب", "برمجة", "كود", "سكريبت"],
            "explanation": ["ما هو", "ما هي", "اشرح", "كيف", "لماذا"],
            "problem_solving": ["مشكلة", "خطأ", "لا يعمل", "حل", "إصلاح"],
            "analysis": ["حلل", "حللي", "رأيك", "تحليل"],
            "learning": ["تعلم", "تعليم", "دورة", "كورس"]
        }
        
        for intent, keywords in intents.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent
        
        return "general"
    
    def generate_ai_response(self, message):
        """توليد رد ذكي باستخدام النماذج المحلية"""
        # البحث في الأسئلة الشائعة أولاً
        answer = self.find_best_answer(message)
        if answer:
            return answer
        
        # تحليل النية
        intent = self.analyze_intent(message)
        
        if intent == "code_generation":
            return self.generate_smart_code(message)
        elif intent == "explanation":
            return self.generate_explanation(message)
        else:
            return self.generate_contextual_response(message)
    
    def generate_smart_code(self, message):
        """توليد كود ذكي بناءً على الطلب"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["موقع", "ويب", "web"]):
            return f"🌐 كود موقع ويب متجاوب:\n\n```html\n{self.knowledge['code_templates']['html_responsive']}\n```"
        
        elif any(word in message_lower for word in ["بيانات", "تحليل", "data"]):
            return f"📊 كود تحليل بيانات:\n\n```python\n{self.knowledge['code_templates']['python_data_analysis']}\n```"
        
        elif any(word in message_lower for word in ["بوت", "دردشة", "chat"]):
            bot_code = """import requests

class ChatBot:
    def __init__(self):
        self.responses = {
            'مرحباً': 'أهلاً وسهلاً! كيف يمكنني مساعدتك؟',
            'كيف الحال': 'أنا بخير، شكراً لسؤالك!'
        }
    
    def respond(self, message):
        return self.responses.get(message, 'لم أفهم سؤالك')

# استخدام البوت
bot = ChatBot()
print(bot.respond('مرحباً'))"""
            return f"🤖 كود بوت دردشة:\n\n```python\n{bot_code}\n```"
        
        else:
            return f"💻 كود Python أساسي:\n\n```python\n{self.knowledge['code_templates']['python_web']}\n```"
    
    def generate_explanation(self, message):
        """توليد شرح ذكي"""
        concepts = {
            "python": "لغة برمجة سهلة التعلم وقوية، تستخدم في مجالات متعددة",
            "html": "لغة ترميز لإنشاء هيكل صفحات الويب",
            "css": "لغة تنسيق لتجميل صفحات الويب",
            "javascript": "لغة برمجة لإنشاء صفحات ويب تفاعلية",
            "شبكة": "مجموعة أجهزة متصلة معاً لتبادل البيانات",
            "خادم": "جهاز قوي يقدم خدمات للأجهزة الأخرى"
        }
        
        for concept, explanation in concepts.items():
            if concept in message.lower():
                return f"📚 شرح {concept}:\n{explanation}"
        
        return "أستطيع شرح: Python, HTML, CSS, JavaScript, الشبكات, الخوادم، وغيرها. ما الذي تريد شرحه؟"
    
    def generate_contextual_response(self, message):
        """توليد رد ذكي حسب السياق"""
        if not self.conversation_history:
            return "🧠 مرحباً! أنا النواة الذكية المتقدمة. أستطيع مساعدتك في البرمجة، الشبكات، الأنظمة، والأسئلة التقنية."
        
        # تحليل آخر محادثة
        last_conversation = self.conversation_history[-1]
        last_message = last_conversation.get('user_message', '')
        
        if "برمجة" in last_message.lower() or "كود" in last_message.lower():
            return "💻 هل تريد مساعدة إضافية في البرمجة؟ أستطيع إنشاء أكواد أو شرح مفاهيم."
        
        elif "شبكة" in last_message.lower():
            return "🌐 هل تحتاج لمزيد من المعلومات عن الشبكات؟ أستطيع شرح TCP/IP, DNS, الرواتر، وغيرها."
        
        else:
            return "🤔 هل يمكنك توضيح سؤالك أكثر؟ أستطيع المساعدة في مواضيع تقنية متعددة."
    
    def learn_from_conversation(self, message, response, user_id="default"):
        """التعلم من المحادثة"""
        if user_id not in self.knowledge["user_profiles"]:
            self.knowledge["user_profiles"][user_id] = {
                "interaction_count": 0,
                "preferences": [],
                "last_interaction": datetime.now().isoformat()
            }
        
        user_data = self.knowledge["user_profiles"][user_id]
        user_data["interaction_count"] += 1
        user_data["last_interaction"] = datetime.now().isoformat()
        
        # تحليل اهتمامات المستخدم
        if "برمجة" in message.lower():
            if "برمجة" not in user_data["preferences"]:
                user_data["preferences"].append("برمجة")
        
        self.save_knowledge()
    
    def process_message(self, message, user_id="default"):
        """معالجة الرسالة الرئيسية"""
        # توليد رد ذكي
        response = self.generate_ai_response(message)
        
        # التعلم من المحادثة
        self.learn_from_conversation(message, response, user_id)
        
        # حفظ المحادثة
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "ai_response": response,
            "user_id": user_id
        }
        self.conversation_history.append(conversation)
        
        return {
            "message": response,
            "analysis": {
                "model_used": "sentence_transformer" if MODEL_LOADED else "basic",
                "response_type": "ai_generated"
            }
        }

# تهيئة النواة المتقدمة
ai_core = AdvancedAICore()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'web_user')
        
        if not user_message:
            return jsonify({'error': 'لا يوجد رسالة'}), 400
        
        # معالجة الرسالة بالنواة المتقدمة
        result = ai_core.process_message(user_message, user_id)
        
        return jsonify({
            'response': result['message'],
            'analysis': result['analysis'],
            'model_loaded': MODEL_LOADED,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"خطأ في معالجة الرسالة: {e}")
        return jsonify({'error': 'حدث خطأ في المعالجة'}), 500

@app.route('/api/knowledge')
def get_knowledge():
    """عرض المعرفة المكتسبة"""
    return jsonify({
        'user_profiles': ai_core.knowledge.get('user_profiles', {}),
        'total_conversations': len(ai_core.conversation_history),
        'model_loaded': MODEL_LOADED
    })

@app.route('/api/health')
def health_check():
    """فحص صحة النظام"""
    return jsonify({
        'status': 'running',
        'model_loaded': MODEL_LOADED,
        'total_knowledge_items': sum(len(qa) for qa in ai_core.knowledge['qa_pairs'].values()),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
