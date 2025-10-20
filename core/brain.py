# core/brain.py - المحرك الرئيسي
import json
import os
from datetime import datetime

class AICoreBrain:
    def __init__(self):
        self.setup_directories()
        self.load_knowledge()
        self.conversation_history = []
        
    def setup_directories(self):
        """إنشاء المجلدات الضرورية"""
        dirs = ['knowledge', 'memory', 'logs', 'projects']
        for dir_name in dirs:
            os.makedirs(dir_name, exist_ok=True)
    
    def load_knowledge(self):
        """تحميل قاعدة المعرفة"""
        knowledge_path = 'knowledge/knowledge_base.json'
        if os.path.exists(knowledge_path):
            try:
                with open(knowledge_path, 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
            except:
                self.create_default_knowledge()
        else:
            self.create_default_knowledge()
    
    def create_default_knowledge(self):
        """إنشاء معرفة افتراضية"""
        self.knowledge = {
            "intents": {
                "programming": ["برمجة", "كود", "برمج", "تطوير", "سكريبت"],
                "networking": ["شبكة", "انترنت", "اتصال", "راوتر", "ip"],
                "systems": ["نظام", "خادم", "سيرفر", "لينكس", "أوبنتو"],
                "security": ["أمن", "حماية", "اختراق", "فايروس", "أمان"],
                "projects": ["مشروع", "بدء", "إنشاء", "جديد"]
            },
            "responses": {
                "programming": "🎯 مجال البرمجة! أستطيع:\n• كتابة أكواد Python\n• تطوير واجهات ويب\n• إنشاء سكريبتات أتمتة\n• حل مشاكل البرمجة\n\nما الذي تريد برمجته؟",
                "networking": "🌐 مجال الشبكات! أستطيع:\n• شرح مفاهيم الشبكات\n• تحليل مشاكل الاتصال\n• تصميم شبكات\n• تأمين الشبكات\n\nما استفسارك؟",
                "systems": "🖥️ مجال الأنظمة! أستطيع:\n• إدارة الخوادم\n• تحليل أداء النظام\n• حل مشاكل النظام\n• نصائح تحسين الأداء\n\nكيف أساعد؟",
                "security": "🔒 الأمن السيبراني! أستطيع:\n• تحليل الثغرات\n• نصائح أمنية\n• تأمين التطبيقات\n• مراجعة الأكواد\n\nما الذي تحتاج؟",
                "projects": "🚀 إدارة المشاريع! أستطيع:\n• إنشاء مشاريع جديدة\n• تنظيم الملفات\n• تخطيط المشاريع\n• إدارة المهام\n\nأخبرني عن مشروعك"
            },
            "code_templates": {
                "python_web": "from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return 'مرحباً!'\n\nif __name__ == '__main__':\n    app.run(debug=True)",
                "python_script": "#!/usr/bin/env python3\n# سكريبت Python مفيد\n\nimport os\nimport sys\n\ndef main():\n    print('مرحباً بالعالم!')\n\nif __name__ == '__main__':\n    main()"
            }
        }
        self.save_knowledge()
    
    def save_knowledge(self):
        """حفظ المعرفة"""
        with open('knowledge/knowledge_base.json', 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    def analyze_intent(self, message):
        """تحليل نية المستخدم"""
        message_lower = message.lower()
        
        for intent, keywords in self.knowledge["intents"].items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent
        
        return "general"
    
    def process_message(self, message, user_id="default"):
        """معالجة الرسالة الرئيسية"""
        intent = self.analyze_intent(message)
        
        # حفظ المحادثة
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "intent": intent,
            "user_id": user_id
        }
        self.conversation_history.append(conversation)
        self.save_conversation()
        
        # توليد الرد
        if intent in self.knowledge["responses"]:
            response = self.knowledge["responses"][intent]
        else:
            response = f"🧠 أفهم أنك تقول: '{message}'\n\nأستطيع مساعدتك في:\n{self.list_capabilities()}"
        
        return {
            "message": response,
            "type": intent,
            "suggestions": self.generate_suggestions(intent)
        }
    
    def list_capabilities(self):
        """عرض القدرات المتاحة"""
        return "• 🤖 البرمجة وتطوير الأكواد\n• 🌐 الشبكات والاتصالات\n• 🖥️ إدارة الأنظمة\n• 🔒 الأمن السيبراني\n• 🚀 إدارة المشاريع"
    
    def generate_suggestions(self, intent):
        """توليد اقتراحات متعلقة"""
        suggestions_map = {
            "programming": ["أنشئ لي سكريبت Python", "ساعدني في حل خطأ برمجي", "أنشئ موقع ويب بسيط"],
            "networking": ["اشرح مفهوم TCP/IP", "كيف أصلح مشكلة اتصال", "تصميم شبكة صغيرة"],
            "systems": ["تحليل أداء النظام", "إعداد خادم ويب", "حل مشكلة في الذاكرة"],
            "security": ["فحص أمان تطبيق", "نصائح أمنية مهمة", "كيف أحمي شبكتي"],
            "general": ["مساعدتي في البرمجة", "شرح مفاهيم الشبكات", "تحليل نظام"]
        }
        return suggestions_map.get(intent, ["كيف يمكنني مساعدتك؟"])
    
    def save_conversation(self):
        """حفظ المحادثة"""
        try:
            with open('memory/conversation_memory.json', 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history[-100:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def generate_code(self, requirements, language="python"):
        """توليد كود"""
        template = self.knowledge["code_templates"].get("python_script", "# كود Python\nprint('مرحباً!')")
        
        return {
            "code": f"# 🎯 الكود المطلوب: {requirements}\n\n{template}",
            "explanation": f"هذا كود {language} ينفذ: {requirements}",
            "language": language
        }
