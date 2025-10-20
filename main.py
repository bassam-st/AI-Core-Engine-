#!/usr/bin/env python3
# النواة الذكية المتقدمة - إصدار مع دمج نموذج Hugging Face + حماية وأخطاء

import os, json, re, time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import requests

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # تأكد أنه مضاف في Render
# موديلات عامة تعمل عبر Inference API (اختر واحد)
DEFAULT_HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
# مهلة الشبكة حتى لا تتجمد النواة
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "35"))

app = Flask(__name__)

# ====== طبقة الاتصال بـ Hugging Face ======
def hf_generate(prompt: str,
                model: str = DEFAULT_HF_MODEL,
                max_new_tokens: int = 256,
                temperature: float = 0.4,
                retries: int = 2) -> str:
    """
    تستدعي نموذج Hugging Face مع تخفيض المخاطر:
    - قراءة المفتاح من البيئة فقط
    - مهلات + محاولات إعادة
    - رسائل خطأ واضحة بدون إسقاط الخدمة
    """
    if not HF_API_KEY:
        return "⚠️ مفتاح HUGGINGFACE_API_KEY غير موجود في البيئة."

    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": f"### Instruction:\n{prompt}\n\n### Response:",
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "return_full_text": False
        }
    }

    last_err = None
    for _ in range(retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=HTTP_TIMEOUT)
            # 503 تعني أن الموديل يحمّل للمرة الأولى؛ ننتظر قليلاً ثم نكرر
            if r.status_code in (503, 524):
                last_err = f"Model warming up (status {r.status_code})"
                time.sleep(3)
                continue
            if r.status_code == 401:
                return "⛔ مفتاح Hugging Face غير صالح أو الصلاحيات غير كافية."
            r.raise_for_status()
            data = r.json()
            # صيغ الاستجابة تختلف باختلاف الموديل؛ نتعامل مع الأكثر شيوعًا
            if isinstance(data, list) and data and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"].strip()
            # في بعض الأحيان تكون الاستجابة قائمة من dicts داخلها 'generated_token_count' فقط
            return json.dumps(data, ensure_ascii=False)[:2000]
        except requests.exceptions.Timeout:
            last_err = "⏳ انتهت مهلة الاتصال بالموديل."
        except Exception as e:
            last_err = f"❗ خطأ أثناء الاتصال بالموديل: {e}"
        time.sleep(1)

    return last_err or "⚠️ تعذّر الحصول على استجابة من الموديل."

# ====== النواة المنطقية المحلية ======
class SmartAICore:
    def __init__(self):
        self.setup_directories()
        self.load_knowledge()
        self.conversation_memory = []

    def setup_directories(self):
        os.makedirs('knowledge', exist_ok=True)
        os.makedirs('memory', exist_ok=True)

    def load_knowledge(self):
        try:
            with open('knowledge/elite_knowledge.json', 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
        except Exception:
            self.knowledge = self.create_basic_knowledge()

    def create_basic_knowledge(self):
        return {
            "expert_qa": {
                "برمجة": {
                    "كيف أنشئ API؟": "Flask → routes → JSON → test",
                    "ما هي Python؟": "لغة برمجة قوية وبسيطة للويب والبيانات وAI",
                    "كيف أبدأ البرمجة؟": "ابدأ بـ Python ثم هياكل البيانات ثم تخصّص"
                }
            },
            "code_templates": {
                "python_basic": "print('مرحباً بالعالم!')",
                "python_web": "from flask import Flask\napp = Flask(__name__)\n@app.route('/')\ndef home():\n    return 'مرحباً!'\n\nif __name__=='__main__':\n    app.run()",
                "python_calculator": "def add(a,b): return a+b\nprint(add(5,3))"
            }
        }

    def process_message(self, message, user_id="default"):
        msg = message.lower().strip()
        # مشغل صريح للنموذج السحابي
        # أمثلة: "نموذج: اكتب رسالة ترحيب" أو "model: summarize ..."
        if msg.startswith("نموذج:") or msg.startswith("model:") or "جرّب الموديل" in msg or "شغّل النموذج" in msg:
            pure = message.split(":", 1)[1].strip() if ":" in message else message
            return hf_generate(pure)

        # كلمات مفتاحية → كود جاهز
        if any(w in msg for w in ["انشئ", "اصنع", "اكتب", "كود", "python", "بايثون"]):
            if any(w in msg for w in ["حساب", "جمع", "طرح", "آلة حاسبة", "calculator"]):
                return self.generate_calculator()
            elif any(w in msg for w in ["موقع", "ويب", "web", "فلاسك", "flask"]):
                return self.generate_web_app()
            elif any(w in msg for w in ["بوت", "دردشة", "chatbot"]):
                return self.generate_chatbot()
            elif any(w in msg for w in ["بيانات", "data", "تحليل"]):
                return self.generate_data_analysis()
            else:
                return self.generate_basic_code()

        if any(w in msg for w in ["مسار", "تعلم", "تعليم"]):
            return self.generate_learning_path()

        if any(w in msg for w in ["راجع", "حلل", "افحص الكود"]):
            code = self.extract_code(message)
            return self.code_review(code) if code else "📝 أرسل الكود الذي تريد مراجعته بين ```"

        if any(w in msg for w in ["فكرة", "مشروع", "مقترح"]):
            return self.generate_project_idea()

        if any(w in msg for w in ["شعور", "مشاعر", "رأيك"]):
            return f"🎭 تحليل المشاعر: {self.analyze_sentiment(message)}"

        if any(w in msg for w in ["ابحث", "بحث", "معلومات عن"]):
            return self.web_search(message)

        if any(w in msg for w in ["مرحب", "اهلا", "سلام", "hello", "hi"]):
            return self.get_welcome_message()

        # الافتراضي: جرّب الموديل السحابي أولًا، ثم سقط على رد محلي
        cloud = hf_generate(message)
        if cloud and not cloud.startswith(("⚠️", "⛔", "❗", "⏳")):
            return cloud
        return self.generate_smart_response(message)

    # ======= باقي مولدات الكود/المحتوى (بدون تغيير جوهري) =======
    def generate_calculator(self):
        code = """class Calculator:
    def __init__(self): self.history=[]
    def add(self,a,b): r=a+b; self.history.append(f"{a}+{b}={r}"); return r
    def subtract(self,a,b): r=a-b; self.history.append(f"{a}-{b}={r}"); return r
    def multiply(self,a,b): r=a*b; self.history.append(f"{a}×{b}={r}"); return r
    def divide(self,a,b):
        if b==0: return "خطأ: قسمة على صفر"
        r=a/b; self.history.append(f"{a}÷{b}={r}"); return r
    def show_history(self): print("\\n".join(self.history))

calc=Calculator(); print("10+5=",calc.add(10,5)); calc.show_history()"""
        return f"🧮 كود آلة حاسبة:\n\n```python\n{code}\n```"

    def generate_web_app(self):
        code = """from flask import Flask
app=Flask(__name__)
@app.route('/')
def home():
    return '<h1>مرحباً بك! 🌟</h1><p>هذا تطبيق Flask بسيط.</p>'
if __name__=='__main__': app.run()"""
        return f"🌐 كود تطبيق ويب:\n\n```python\n{code}\n```"

    def generate_chatbot(self):
        code = """class ChatBot:
    def __init__(self):
        self.responses={'مرحباً':'أهلاً وسهلاً!','كيف الحال':'أنا بخير 😊','ما اسمك':'أنا بوت الدردشة!','وداعاً':'مع السلامة!'}
    def respond(self,msg):
        m=msg.lower()
        for k,v in self.responses.items():
            if k in m: return v
        return 'هل توضح سؤالك أكثر؟'
bot=ChatBot(); print(bot.respond('مرحباً'))"""
        return f"🤖 كود بوت دردشة:\n\n```python\n{code}\n```"

    def generate_data_analysis(self):
        code = """import pandas as pd, matplotlib.pyplot as plt
df=pd.DataFrame({'الشهر':['يناير','فبراير','مارس','أبريل'],'المبيعات':[120,150,180,200]})
print(df); print(df.describe()); df.plot(x='الشهر',y='المبيعات',marker='o'); plt.show()"""
        return f"📊 كود تحليل بيانات:\n\n```python\n{code}\n```"

    def generate_basic_code(self):
        code = """def calculate(a,b):
    print(f"{a}+{b}={a+b}"); print(f"{a}-{b}={a-b}"); print(f"{a}×{b}={a*b}")
    if b!=0: print(f"{a}÷{b}={a/b}")
with open('example.txt','w',encoding='utf-8') as f: f.write('مرحباً!\\n')
calculate(10,5)"""
        return f"💻 كود Python أساسي:\n\n```python\n{code}\n```"

    def generate_learning_path(self):
        return "🎯 مسار تعلم: أساسيات Python → هياكل البيانات → OOP → Flask/APIs → قواعد بيانات → مشاريع عملية"

    def code_review(self, code):
        issues=[]
        if not code: return "أرسل الكود بين ```"
        low=code.lower()
        if "password" in low and "encrypt" not in low: issues.append("🔒 شفّر كلمات المرور.")
        if "select *" in low: issues.append("🗃️ تجنّب SELECT *.")
        if "eval(" in low: issues.append("⚠️ تجنّب eval().")
        return "🔍 مراجعة الكود:\n" + ("\n".join(issues) if issues else "✅ لا مشاكل واضحة.")

    def generate_project_idea(self):
        return "💡 فكرة: نظام مهام مع إشعارات وتقرير أسبوعي."

    def analyze_sentiment(self, text):
        pos = any(w in text for w in ['جيد','ممتاز','رائع','جميل'])
        neg = any(w in text for w in ['سيء','مشكلة','خطأ','لا يعمل'])
        if pos and not neg: return "إيجابي 😊"
        if neg and not pos: return "سلبي 😔"
        return "محايد 😐"

    def web_search(self, query):
        topics={"برمجة":"Python, AI, Web3","شبكات":"5G, IoT, الأمن السيبراني","أنظمة":"Containers, Kubernetes, DevOps"}
        for t,info in topics.items():
            if t in query: return f"🔍 {t}: {info}"
        return "🔍 جرّب كلمات: برمجة / شبكات / أنظمة"

    def get_welcome_message(self):
        return "🚀 أهلاً بك في النواة الذكية! اكتب: «نموذج: اكتب رسالة ترحيب لمشروع بسام» لتجربة الموديل."

    def generate_smart_response(self, message):
        return f"🤔 طلبت: «{message}». يمكنك قول: «نموذج: …» أو «أنشئ كود …»."

    def extract_code(self, message):
        blocks=re.findall(r'```[\\w]*\\n(.*?)\\n```', message, re.DOTALL)
        return blocks[0] if blocks else None

# ====== تهيئة النواة ======
ai_core = SmartAICore()

# ====== المسارات ======
@app.route('/')
def home():
    # صفحة بسيطة (لو لديك templates/index.html سيعمل render_template)
    try:
        return render_template('index.html')
    except Exception:
        return "<h2>Bassam AI Core</h2><p>أرسل POST إلى /api/chat أو /api/generate</p>"

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json(force=True)
        user_message = (data.get('message') or "").strip()
        if not user_message:
            return jsonify({'error': 'لا يوجد رسالة'}), 400
        result = ai_core.process_message(user_message)
        return jsonify({'response': result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# مسار مباشر لاستدعاء الموديل (للاختبارات/الفرونت)
@app.route('/api/generate', methods=['POST'])
def generate_api():
    data = request.get_json(force=True)
    prompt = (data.get("prompt") or "").strip()
    model = (data.get("model") or DEFAULT_HF_MODEL).strip()
    if not prompt:
        return jsonify({"error": "الرجاء إرسال prompt"}), 400
    text = hf_generate(prompt, model=model)
    return jsonify({"model": model, "output": text, "ts": datetime.now().isoformat()})

@app.route('/health')
def health_check():
    return jsonify({'status': 'running', 'version': 'smart_hf_2.1', 'model': DEFAULT_HF_MODEL})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
