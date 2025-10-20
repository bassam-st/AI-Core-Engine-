#!/usr/bin/env python3
# النواة الذكية المتقدمة - إصدار Render المتوافق

import os
import json
import logging
import requests
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

class SmartAICore:
    def __init__(self):
        self.setup_directories()
        self.load_knowledge()
        self.conversation_memory = []
        self.user_profiles = {}
        
    def setup_directories(self):
        """إنشاء المجلدات الأساسية"""
        dirs = ['knowledge', 'memory', 'projects']
        for dir_name in dirs:
            os.makedirs(dir_name, exist_ok=True)
    
    def load_knowledge(self):
        """تحميل المعرفة"""
        try:
            with open('knowledge/elite_knowledge.json', 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
            print("✅ تم تحميل المعرفة بنجاح!")
        except Exception as e:
            print(f"⚠️ تعذر تحميل المعرفة: {e}")
            self.knowledge = self.create_basic_knowledge()
    
    def create_basic_knowledge(self):
        """إنشاء معرفة أساسية"""
        return {
            "expert_qa": {
                "برمجة": {
                    "كيف أنشئ API؟": "لإنشاء API: 1) استخدم Flask أو FastAPI 2) أضف endpoints 3) تعامل مع JSON 4) اختبر باستخدام Postman",
                    "ما هي Python؟": "Python لغة برمجة سهلة التعلم وقوية، تستخدم في الويب، البيانات، الذكاء الاصطناعي، والأتمتة.",
                    "كيف أتعلم البرمجة؟": "ابدأ بأساسيات Python، ثم تعلم هياكل البيانات، ثم تخصص في مجال يهمك.",
                    "ما الفرق بين List و Tuple؟": "List قابلة للتعديل، Tuple ثابتة. List تستخدم [] و Tuple تستخدم ()",
                    "كيف أنشئ موقع ويب؟": "1) HTML للهيكل 2) CSS للتنسيق 3) JavaScript للتفاعل 4) Flask أو Django للخادم"
                },
                "شبكات": {
                    "ما هو IP؟": "عنوان IP هو عنوان فريد يحدد جهازك على الشبكة.",
                    "كيف يعمل DNS؟": "DNS يحول أسماء النطاقات (مثل google.com) إلى عناوين IP رقمية.",
                    "ما الفرق بين TCP و UDP؟": "TCP موثوق مع تأكيد الاستلام، UDP سريع بدون تأكيد.",
                    "ما هي شبكة LAN؟": "شبكة محلية تربط أجهزة في منطقة صغيرة مثل المنزل أو المكتب.",
                    "كيف أحمي شبكتي؟": "1) كلمة مرور قوية 2) تحديث البرامج 3) جدار حماية 4) تشفير WiFi"
                },
                "أنظمة": {
                    "ما هو Linux؟": "Linux نظام تشغيل مفتوح المصدر، مستقر وآمن، يستخدم في الخوادم.",
                    "كيف أراقب أداء النظام؟": "استخدم أدوات مثل: top, htop, ps, df -h لمراقبة الموارد.",
                    "ما هي الحاوية؟": "الحاوية (Container) حزمة تحتوي على تطبيق وكل اعتماداته.",
                    "كيف أنشئ خادم ويب؟": "1) ثبت Apache أو Nginx 2) ضبط الإعدادات 3) نشر التطبيق 4) تأمين الخادم"
                }
            },
            "code_templates": {
                "python_basic": "print('مرحباً بالعالم!')",
                "python_web": "from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'مرحباً من Flask!'\n\nif __name__ == '__main__':\n    app.run(debug=True)",
                "python_data": "import pandas as pd\nimport matplotlib.pyplot as plt\n\ndata = pd.read_csv('data.csv')\nprint(data.head())\ndata.plot()\nplt.show()",
                "html_basic": "<!DOCTYPE html>\n<html>\n<head>\n    <title>موقعي</title>\n</head>\n<body>\n    <h1>مرحباً!</h1>\n    <p>هذا موقعي الأول</p>\n</body>\n</html>"
            }
        }
    
    def semantic_similarity(self, text1, text2):
        """تشابه نصي بسيط وفعال"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        common = words1.intersection(words2)
        return len(common) / max(len(words1), len(words2)) if words1 or words2 else 0
    
    def analyze_sentiment(self, text):
        """تحليل المشاعر"""
        positive_words = ['جيد', 'ممتاز', 'رائع', 'شكرا', 'جميل', 'مذهل']
        negative_words = ['سيء', 'مشكلة', 'خطأ', 'لا يعمل', 'صعب']
        
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        if positive_count > negative_count:
            return "إيجابي"
        elif negative_count > positive_count:
            return "سلبي"
        else:
            return "محايد"
    
    def find_best_answer(self, question):
        """إيجاد أفضل إجابة"""
        best_score = 0
        best_answer = None
        
        for category, qa_pairs in self.knowledge.get("expert_qa", {}).items():
            for q, a in qa_pairs.items():
                score = self.semantic_similarity(question, q)
                if score > best_score and score > 0.3:
                    best_score = score
                    best_answer = a
        
        return best_answer
    
    def generate_learning_path(self, topic):
        """توليد مسار تعلم"""
        paths = {
            "برمجة": ["أساسيات البرمجة", "هياكل البيانات", "قواعد البيانات", "تطوير الويب", "مشاريع عملية"],
            "شبكات": ["أساسيات الشبكات", "بروتوكولات الشبكة", "أجهزة الشبكة", "أمن الشبكات", "شبكات متقدمة"],
            "أنظمة": ["أساسيات الأنظمة", "إدارة الخوادم", "الأمن النظامي", "الحاويات", "السحابة"]
        }
        
        if topic in paths:
            return f"🎯 مسار تعلم {topic}:\n\n" + "\n".join([f"• {item}" for item in paths[topic]])
        return "أستطيع إنشاء مسارات للبرمجة، الشبكات، والأنظمة."
    
    def code_review(self, code):
        """مراجعة الكود"""
        issues = []
        
        if "password" in code.lower() and "encrypt" not in code.lower():
            issues.append("🔒 كلمات المرور يجب تشفيرها")
        
        if "select *" in code.lower():
            issues.append("🗃️ تجنب SELECT *، حدد الأعمدة المطلوبة")
        
        if "eval(" in code.lower():
            issues.append("⚠️ تجنب eval() لأسباب أمنية")
        
        return "🔍 مراجعة الكود:\n" + "\n".join(issues) if issues else "✅ الكود يبدو جيداً!"
    
    def generate_project_idea(self, field):
        """توليد أفكار مشاريع"""
        ideas = {
            "برمجة": ["منصة مدونة", "متجر إلكتروني", "تطبيق مهام", "بوت دردشة", "أداة تحليل بيانات"],
            "شبكات": ["ماسح شبكة", "مراقب اتصال", "أداة تحليل حزم", "خادم VPN", "نظام مراقبة"],
            "أنظمة": ["أداة نسخ احتياطي", "مراقب أداء", "مدير عمليات", "منصة نشر", "نظام مراقبة"]
        }
        
        if field in ideas:
            import random
            idea = random.choice(ideas[field])
            return f"💡 فكرة مشروع {field}: {idea}"
        return "أستطيع اقتراح مشاريع للبرمجة، الشبكات، والأنظمة."
    
    def process_message(self, message, user_id="default"):
        """معالجة الرسالة الرئيسية"""
        message_lower = message.lower()
        sentiment = self.analyze_sentiment(message)
        
        # تحديث ملف المستخدم
        self.update_user_profile(user_id, message)
        
        # البحث عن إجابة
        answer = self.find_best_answer(message)
        if answer:
            response = f"🎯 {answer}"
        
        elif "مسار تعلم" in message_lower:
            topic = "برمجة"
            if "شبكات" in message_lower:
                topic = "شبكات"
            elif "أنظمة" in message_lower:
                topic = "أنظمة"
            response = self.generate_learning_path(topic)
        
        elif "راجع الكود" in message_lower or "حلل الكود" in message_lower:
            code = self.extract_code(message)
            response = self.code_review(code) if code else "أرسل الكود الذي تريد مراجعته"
        
        elif "فكرة مشروع" in message_lower:
            field = "برمجة"
            if "شبكات" in message_lower:
                field = "شبكات"
            elif "أنظمة" in message_lower:
                field = "أنظمة"
            response = self.generate_project_idea(field)
        
        elif "أنشئ لي" in message_lower and "كود" in message_lower:
            response = self.generate_smart_code(message)
        
        elif any(word in message_lower for word in ['مرحب', 'اهلا', 'سلام']):
            response = "مرحباً بك! 👋 أنا النواة الذكية. أستطيع مساعدتك في:\n• البرمجة والتطوير\n• الشبكات والاتصالات\n• إدارة الأنظمة\n• مراجعة الأكواد\n• أفكار المشاريع"
        
        else:
            response = f"🧠 أفهم أنك تقول: '{message}'\n\nأستطيع المساعدة في:\n• البرمجة (Python, HTML, الخ)\n• الشبكات (IP, DNS, TCP/IP)\n• الأنظمة (Linux, الخوادم)\n• مراجعة الأكواد\n• مسارات التعلم\n\nما المجال الذي تفضله؟"
        
        # حفظ المحادثة
        self.save_conversation(user_id, message, response, sentiment)
        
        return {
            "message": response,
            "analysis": {
                "sentiment": sentiment,
                "user_level": self.get_user_level(user_id)
            }
        }
    
    def extract_code(self, message):
        """استخراج الكود من الرسالة"""
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', message, re.DOTALL)
        return code_blocks[0] if code_blocks else None
    
    def generate_smart_code(self, message):
        """توليد كود ذكي"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["موقع", "ويب", "web"]):
            return f"🌐 كود موقع ويب:\n\n```python\n{self.knowledge['code_templates']['python_web']}\n```"
        
        elif any(word in message_lower for word in ["بيانات", "تحليل", "data"]):
            return f"📊 كود تحليل بيانات:\n\n```python\n{self.knowledge['code_templates']['python_data']}\n```"
        
        elif any(word in message_lower for word in ["html", "صفحة"]):
            return f"📄 كود HTML:\n\n```html\n{self.knowledge['code_templates']['html_basic']}\n```"
        
        else:
            return f"💻 كود Python أساسي:\n\n```python\n{self.knowledge['code_templates']['python_basic']}\n```"
    
    def update_user_profile(self, user_id, message):
        """تحديث ملف المستخدم"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "join_date": datetime.now().isoformat(),
                "interaction_count": 0,
                "interests": [],
                "last_activity": datetime.now().isoformat()
            }
        
        profile = self.user_profiles[user_id]
        profile["interaction_count"] += 1
        profile["last_activity"] = datetime.now().isoformat()
    
    def get_user_level(self, user_id):
        """تحديد مستوى المستخدم"""
        if user_id not in self.user_profiles:
            return "مبتدئ"
        
        interactions = self.user_profiles[user_id]["interaction_count"]
        if interactions > 20:
            return "خبير"
        elif interactions > 10:
            return "متوسط"
        else:
            return "مبتدئ"
    
    def save_conversation(self, user_id, user_message, response, sentiment):
        """حفظ المحادثة"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "response": response,
            "sentiment": sentiment
        }
        
        self.conversation_memory.append(conversation)

# تهيئة النواة
ai_core = SmartAICore()

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
        
        result = ai_core.process_message(user_message, user_id)
        
        return jsonify({
            'response': result['message'],
            'analysis': result['analysis'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>')
def get_user_profile(user_id):
    """الحصول على ملف المستخدم"""
    profile = ai_core.user_profiles.get(user_id, {})
    return jsonify({
        'profile': profile,
        'level': ai_core.get_user_level(user_id)
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'running',
        'version': 'smart_1.0',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
