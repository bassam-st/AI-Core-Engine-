#!/usr/bin/env python3
# النواة الذكية المتقدمة - إصدار محسّن

import os
import json
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

class SmartAICore:
    def __init__(self):
        self.setup_directories()
        self.load_knowledge()
        self.conversation_memory = []
        
    def setup_directories(self):
        """إنشاء المجلدات الأساسية"""
        os.makedirs('knowledge', exist_ok=True)
        os.makedirs('memory', exist_ok=True)
    
    def load_knowledge(self):
        """تحميل المعرفة"""
        try:
            with open('knowledge/elite_knowledge.json', 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
        except:
            self.knowledge = self.create_basic_knowledge()
    
    def create_basic_knowledge(self):
        """إنشاء معرفة أساسية"""
        return {
            "expert_qa": {
                "برمجة": {
                    "كيف أنشئ API؟": "لإنشاء API: 1) استخدم Flask 2) أضف routes 3) تعامل مع JSON 4) اختبر API",
                    "ما هي Python؟": "لغة برمجة سهلة وقوية للويب، البيانات، والذكاء الاصطناعي",
                    "كيف أبدأ البرمجة؟": "ابدأ بPython، ثم هياكل البيانات، ثم تخصص في مجال"
                }
            },
            "code_templates": {
                "python_basic": "print('مرحباً بالعالم!')",
                "python_web": "from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'مرحباً!'\n\nif __name__ == '__main__':\n    app.run(debug=True)",
                "python_calculator": "def add(a, b): return a + b\ndef subtract(a, b): return a - b\nprint(add(5, 3))"
            }
        }
    
    def process_message(self, message, user_id="default"):
        """معالجة الرسالة - النسخة المحسنة"""
        message_lower = message.lower().strip()
        
        print(f"🔍 معالجة الرسالة: '{message}'")  # للتdebug
        
        # طلبات الأكواد - أولوية عالية
        if any(word in message_lower for word in ["انشئ", "اصنع", "أنشئ لي", "اكتب", "مثّل", "كود", "برمجة", "بايثون", "python"]):
            if any(word in message_lower for word in ["حساب", "جمع", "طرح", "آلة حاسبة", "calculator"]):
                return self.generate_calculator()
            elif any(word in message_lower for word in ["موقع", "ويب", "web", "فلاسك", "flask"]):
                return self.generate_web_app()
            elif any(word in message_lower for word in ["بوت", "دردشة", "chatbot"]):
                return self.generate_chatbot()
            elif any(word in message_lower for word in ["بيانات", "data", "تحليل"]):
                return self.generate_data_analysis()
            else:
                return self.generate_basic_code()
        
        # مسارات التعلم
        elif any(word in message_lower for word in ["مسار", "مسارات", "تعلم", "تعليم", "كيف اتعلم"]):
            return self.generate_learning_path()
        
        # مراجعة الأكواد
        elif any(word in message_lower for word in ["راجع", "حلل", "افحص الكود"]):
            code = self.extract_code(message)
            return self.code_review(code) if code else "📝 أرسل الكود الذي تريد مراجعته بين ```"
        
        # أفكار مشاريع
        elif any(word in message_lower for word in ["فكرة", "مشروع", "مقترح"]):
            return self.generate_project_idea()
        
        # تحليل المشاعر
        elif any(word in message_lower for word in ["شعور", "مشاعر", "رأيك"]):
            sentiment = self.analyze_sentiment(message)
            return f"🎭 تحليل المشاعر: {sentiment}"
        
        # البحث
        elif any(word in message_lower for word in ["ابحث", "بحث", "معلومات عن"]):
            return self.web_search(message)
        
        # الترحيب
        elif any(word in message_lower for word in ["مرحب", "اهلا", "سلام", "hello", "hi"]):
            return self.get_welcome_message()
        
        # الرد الذكي البديل
        else:
            return self.generate_smart_response(message)
    
    def generate_calculator(self):
        """توليد كود آلة حاسبة"""
        code = """# 🧮 آلة حاسبة متقدمة

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} × {b} = {result}")
        return result
    
    def divide(self, a, b):
        if b == 0:
            return "خطأ: لا يمكن القسمة على صفر!"
        result = a / b
        self.history.append(f"{a} ÷ {b} = {result}")
        return result
    
    def show_history(self):
        for operation in self.history:
            print(operation)

# الاستخدام
calc = Calculator()
print("10 + 5 =", calc.add(10, 5))
print("10 × 3 =", calc.multiply(10, 3))
calc.show_history()
"""
        return f"🧮 كود آلة حاسبة متقدمة:\n\n```python\n{code}\n```"
    
    def generate_web_app(self):
        """توليد كود تطبيق ويب"""
        code = """from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>تطبيقي</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>مرحباً بك! 🌟</h1>
            <p>هذا تطبيق ويب يعمل بـ Flask</p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/data')
def get_data():
    return {"message": "مرحباً من API!", "status": "success"}

if __name__ == '__main__':
    app.run(debug=True)
"""
        return f"🌐 كود تطبيق ويب كامل:\n\n```python\n{code}\n```"
    
    def generate_chatbot(self):
        """توليد كود بوت دردشة"""
        code = """class ChatBot:
    def __init__(self):
        self.responses = {
            'مرحباً': 'أهلاً وسهلاً! كيف يمكنني مساعدتك؟',
            'كيف الحال': 'أنا بخير، شكراً لسؤالك! 😊',
            'ما اسمك': 'أنا بوت الدردشة الذكي!',
            'مساعدة': 'أستطيع الإجابة على أسئلتك والتحدث معك.',
            'وداعاً': 'مع السلامة! كان حديثاً ممتعاً 🫡'
        }
    
    def respond(self, message):
        message_lower = message.lower()
        
        for pattern, response in self.responses.items():
            if pattern in message_lower:
                return response
        
        return 'هذا مثير للاهتمام! هل يمكنك شرح المزيد؟'

# استخدام البوت
bot = ChatBot()
print(bot.respond('مرحباً'))
print(bot.respond('كيف الحال؟'))
"""
        return f"🤖 كود بوت دردشة ذكي:\n\n```python\n{code}\n```"
    
    def generate_data_analysis(self):
        """توليد كود تحليل بيانات"""
        code = """import pandas as pd
import matplotlib.pyplot as plt

# بيانات مثال
data = {
    'الشهر': ['يناير', 'فبراير', 'مارس', 'أبريل'],
    'المبيعات': [120, 150, 180, 200],
    'العملاء': [50, 65, 80, 95]
}

df = pd.DataFrame(data)
print("📊 البيانات:")
print(df)

print("\\n📈 الإحصائيات:")
print(df.describe())

# رسم بياني
plt.figure(figsize=(10, 6))
plt.plot(df['الشهر'], df['المبيعات'], marker='o', label='المبيعات')
plt.plot(df['الشهر'], df['العملاء'], marker='s', label='العملاء')
plt.title('تحليل الأداء')
plt.xlabel('الشهر')
plt.ylabel('القيمة')
plt.legend()
plt.grid(True)
plt.show()
"""
        return f"📊 كود تحليل بيانات:\n\n```python\n{code}\n```"
    
    def generate_basic_code(self):
        """توليد كود أساسي"""
        code = """# 🐍 كود Python مفيد

# 1. العمليات الحسابية
def calculate(a, b):
    print(f"{a} + {b} = {a + b}")
    print(f"{a} - {b} = {a - b}")
    print(f"{a} × {b} = {a * b}")
    if b != 0:
        print(f"{a} ÷ {b} = {a / b}")

# 2. إدارة القوائم
fruits = ['تفاح', 'موز', 'برتقال']
print("الفواكه:", fruits)
fruits.append('فراولة')
print("بعد الإضافة:", fruits)

# 3. العمل مع الملفات
with open('example.txt', 'w', encoding='utf-8') as f:
    f.write('مرحباً بالعالم!\\n')

# التشغيل
calculate(10, 5)
"""
        return f"💻 كود Python أساسي:\n\n```python\n{code}\n```"
    
    def generate_learning_path(self):
        """توليد مسار تعلم"""
        path = """🎯 مسار تعلم البرمجة المتكامل:

1️⃣ **المستوى المبتدئ:**
   • أساسيات Python (المتغيرات، الشروط، الحلقات)
   • هياكل البيانات (List, Dictionary, Tuple, Set)
   • الدوال ووحدات Python

2️⃣ **المستوى المتوسط:**
   • البرمجة كائنية التوجه (OOP)
   • العمل مع الملفات والقواعد البيانية
   • واجهات برمجة التطبيقات (APIs)
   • إطار العمل Flask

3️⃣ **المستوى المتقدم:**
   • الخوارزميات وهياكل البيانات المتقدمة
   • التصميم patterns
   • testing والجودة
   • DevOps والنشر

💡 **نصيحة:** ابدأ بمشاريع صغيرة وتدرج إلى مشاريع أكبر!"""
        return path
    
    def code_review(self, code):
        """مراجعة الكود"""
        issues = []
        
        if "password" in code.lower() and "encrypt" not in code.lower():
            issues.append("🔒 كلمات المرور يجب تشفيرها")
        
        if "select *" in code.lower():
            issues.append("🗃️ تجنب SELECT *، حدد الأعمدة المطلوبة")
        
        if "eval(" in code.lower():
            issues.append("⚠️ تجنب eval() لأسباب أمنية")
        
        if "hardcode" in code.lower():
            issues.append("📝 تجنب القيم الثابتة، استخدم متغيرات")
        
        return "🔍 مراجعة الكود:\n" + "\n".join(issues) if issues else "✅ الكود يبدو جيداً! لا توجد مشاكل واضحة."
    
    def generate_project_idea(self):
        """توليد فكرة مشروع"""
        ideas = [
            "💡 نظام إدارة المهام اليومية",
            "💡 تطبيق قائمة التسوق الذكية", 
            "💡 منصة مدونة شخصية",
            "💡 أداة تحويل العملات",
            "💡 تطبيق تنبيهات الطقس",
            "💡 نظام حجز مواعيد",
            "💡 أداة تحليل النصوص",
            "💡 مسجل المصروفات الشهرية"
        ]
        import random
        return random.choice(ideas) + "\n\n🚀 الميزات: واجهة مستخدم، حفظ البيانات، تقارير، إشعارات"
    
    def analyze_sentiment(self, text):
        """تحليل المشاعر"""
        positive = ['جيد', 'ممتاز', 'رائع', 'شكرا', 'جميل', 'مذهل']
        negative = ['سيء', 'مشكلة', 'خطأ', 'لا يعمل', 'صعب']
        
        pos_count = sum(1 for word in positive if word in text.lower())
        neg_count = sum(1 for word in negative if word in text.lower())
        
        if pos_count > neg_count: return "إيجابي 😊"
        elif neg_count > pos_count: return "سلبي 😔"
        else: return "محايد 😐"
    
    def web_search(self, query):
        """محاكاة بحث ويب"""
        topics = {
            "برمجة": "أحدث تقنيات 2024: Python, AI, Web3, Cloud",
            "شبكات": "الاتجاهات: 5G, IoT, الأمن السيبراني, SDN", 
            "أنظمة": "التطورات: الحاويات, Kubernetes, DevOps, السحابة"
        }
        
        for topic, info in topics.items():
            if topic in query:
                return f"🔍 معلومات عن {topic}:\n{info}"
        
        return "🔍 لم أجد نتائج دقيقة. جرب: برمجة، شبكات، أنظمة"
    
    def get_welcome_message(self):
        """رسالة ترحيب"""
        return """🚀 **مرحباً بك في النواة الذكية!**

أستطيع مساعدتك في:

💻 **البرمجة:**
   - إنشاء أكواد Python كاملة
   - تطبيقات ويب، بوتات، أدوات
   - مراجعة وتحليل الأكواد

🎯 **التعلم:**
   - مسارات تعلم مخصصة
   - شروحات مفصلة
   - نصائح تطوير

💡 **المشاريع:**
   - أفكار مشاريع إبداعية
   - تخطيط وتنفيذ
   - حل المشاكل

📝 **جرب أن تطلب:**
   - "أنشئ لي كود آلة حاسبة"
   - "اصنع بوت دردشة"
   - "مسار تعلم برمجة" 
   - "راجع هذا الكود: ```print('hello')```"

**ما الذي تريد أن تبدأ به؟**"""
    
    def generate_smart_response(self, message):
        """رد ذكي بديل"""
        return f"""🤔 لقد طلبت: "{message}"

لكن لم أفهم بالضبط ما تريد. هل تقصد:

💻 **برمجة؟** - "أنشئ لي كود [شيء محدد]"
🎓 **تعلم؟** - "مسار تعلم [مجال]"  
🔍 **مراجعة؟** - "راجع هذا الكود"
💡 **مشروع؟** - "فكرة مشروع"

أخبرني ما المجال الذي تريده وسأساعدك! 🚀"""
    
    def extract_code(self, message):
        """استخراج الكود من الرسالة"""
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', message, re.DOTALL)
        return code_blocks[0] if code_blocks else None

# تهيئة النواة
ai_core = SmartAICore()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'لا يوجد رسالة'}), 400
        
        result = ai_core.process_message(user_message)
        
        return jsonify({
            'response': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'running', 'version': 'smart_2.0'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
