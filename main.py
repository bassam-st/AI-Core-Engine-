#!/usr/bin/env python3
# النواة الذكية المتقدمة - إصدار Render

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

class SmartCore:
    def __init__(self):
        self.knowledge_file = 'knowledge/memory.json'
        self.setup_directories()
        self.load_knowledge()
        self.conversation_history = []
    
    def setup_directories(self):
        """إنشاء المجلدات الضرورية"""
        os.makedirs('knowledge', exist_ok=True)
        os.makedirs('memory', exist_ok=True)
    
    def load_knowledge(self):
        """تحميل المعرفة"""
        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
        except:
            self.knowledge = {
                "user_preferences": {},
                "learned_patterns": {},
                "common_questions": {},
                "code_templates": {
                    "python_web": "from flask import Flask\\napp = Flask(__name__)\\n\\n@app.route('/')\\ndef home():\\n    return 'مرحباً!'\\n\\nif __name__ == '__main__':\\n    app.run(debug=True)",
                    "python_script": "#!/usr/bin/env python3\\nprint('مرحباً بالعالم!')",
                    "html_basic": "<!DOCTYPE html>\\n<html>\\n<head>\\n    <title>موقعي</title>\\n</head>\\n<body>\\n    <h1>مرحباً!</h1>\\n</body>\\n</html>"
                }
            }
    
    def save_knowledge(self):
        """حفظ المعرفة"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def analyze_message(self, message):
        """تحليل الرسالة"""
        message_lower = message.lower()
        
        analysis = {
            "intent": "general",
            "needs_code": False,
            "topics": [],
            "complexity": "medium"
        }
        
        # تحليل النية
        intents = {
            "programming": ["برمجة", "كود", "بايثون", "برمج", "سكريبت"],
            "networking": ["شبكة", "انترنت", "اتصال", "راوتر", "ip"],
            "systems": ["نظام", "خادم", "سيرفر", "أوبنتو"],
            "learning": ["تعلم", "تعليم", "اشرح", "ما هو"]
        }
        
        for intent, keywords in intents.items():
            for keyword in keywords:
                if keyword in message_lower:
                    analysis["intent"] = intent
                    break
        
        # تحليل الحاجة للكود
        if any(word in message_lower for word in ["اكتب", "انشئ", "اصنع", "كود"]):
            analysis["needs_code"] = True
        
        # استخراج المواضيع
        topics = ["python", "html", "شبكة", "نظام", "أمن"]
        for topic in topics:
            if topic in message_lower:
                analysis["topics"].append(topic)
        
        return analysis
    
    def learn_from_conversation(self, message, response, user_id="web_user"):
        """التعلم من المحادثة"""
        if user_id not in self.knowledge["user_preferences"]:
            self.knowledge["user_preferences"][user_id] = {
                "interaction_count": 0,
                "preferred_topics": [],
                "last_interaction": datetime.now().isoformat()
            }
        
        user_data = self.knowledge["user_preferences"][user_id]
        user_data["interaction_count"] += 1
        user_data["last_interaction"] = datetime.now().isoformat()
        
        # تعلم الأسئلة الشائعة
        question_key = message[:30]
        if question_key in self.knowledge["common_questions"]:
            self.knowledge["common_questions"][question_key]["count"] += 1
        else:
            self.knowledge["common_questions"][question_key] = {
                "question": message,
                "response": response,
                "count": 1,
                "first_seen": datetime.now().isoformat()
            }
        
        self.save_knowledge()
    
    def generate_code(self, requirements, language="python"):
        """توليد كود"""
        template_key = f"{language}_basic"
        if template_key in self.knowledge["code_templates"]:
            base_code = self.knowledge["code_templates"][template_key]
        else:
            base_code = f"# كود {language}\\nprint('مرحباً!')"
        
        code = f"# 🎯 الكود المطلوب: {requirements}\\n\\n{base_code}"
        
        return {
            "code": code,
            "language": language,
            "requirements": requirements
        }
    
    def process_message(self, message, user_id="web_user"):
        """معالجة الرسالة الرئيسية"""
        analysis = self.analyze_message(message)
        
        # توليد الرد
        if analysis["needs_code"]:
            language = "python"
            if "html" in message.lower():
                language = "html"
            
            code_result = self.generate_code(message, language)
            response = f"📝 تم توليد كود {language}:\n\n```{language}\n{code_result['code']}\n```"
            
        elif analysis["intent"] == "programming":
            response = "💻 مجال البرمجة! أستطيع:\n• كتابة أكواد Python\n• تطوير تطبيقات ويب\n• إنشاء سكريبتات أتمتة\n• حل مشاكل برمجية\n\nما الذي تريد برمجته؟"
        
        elif analysis["intent"] == "networking":
            response = "🌐 مجال الشبكات! أستطيع:\n• شرح مفاهيم الشبكات\n• تحليل مشاكل الاتصال\n• تصميم هياكل الشبكات\n• تأمين الشبكات\n\nما استفسارك الشبكي؟"
        
        elif analysis["intent"] == "systems":
            response = "🖥️ مجال الأنظمة! أستطيع:\n• إدارة الخوادم\n• تحليل أداء النظام\n• حل مشاكل النظام\n• نصائح تحسين الأداء\n\nكيف أساعد؟"
        
        else:
            response = f"🧠 أفهم أنك تقول: '{message}'\n\nأستطيع مساعدتك في:\n• البرمجة والتطوير\n• الشبكات والاتصالات\n• إدارة الأنظمة\n• الأمن السيبراني\n\nأي مجال تفضل؟"
        
        # التعلم من المحادثة
        self.learn_from_conversation(message, response, user_id)
        
        # حفظ المحادثة
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "response": response,
            "analysis": analysis
        })
        
        return {
            "message": response,
            "analysis": analysis,
            "learned": True
        }

# تهيئة النواة الذكية
ai_core = SmartCore()

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
        
        # معالجة الرسالة بالنواة الذكية
        result = ai_core.process_message(user_message, user_id)
        
        return jsonify({
            'response': result['message'],
            'analysis': result['analysis'],
            'learned': result['learned'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"خطأ في معالجة الرسالة: {e}")
        return jsonify({'error': 'حدث خطأ في المعالجة'}), 500

@app.route('/api/knowledge')
def get_knowledge():
    """عرض المعرفة المكتسبة"""
    return jsonify({
        'user_preferences': ai_core.knowledge.get('user_preferences', {}),
        'common_questions': ai_core.knowledge.get('common_questions', {}),
        'total_conversations': len(ai_core.conversation_history)
    })

@app.route('/api/generate-code', methods=['POST'])
def generate_code_api():
    """واجهة توليد الكود"""
    try:
        data = request.get_json()
        requirements = data.get('requirements', '')
        language = data.get('language', 'python')
        
        code_result = ai_core.generate_code(requirements, language)
        
        return jsonify({
            'code': code_result['code'],
            'language': code_result['language'],
            'requirements': code_result['requirements']
        })
        
    except Exception as e:
        return jsonify({'error': f'خطأ في توليد الكود: {e}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
