#!/usr/bin/env python3
# النواة الذكية المتقدمة - AI Core Engine
# نسخة متوافقة مع Android

import os
import sys
import logging
import json
from datetime import datetime

# إضافة المسارات للمشروع
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from core.brain import AICoreBrain
    from utils.logger import setup_logging
except ImportError as e:
    print(f"خطأ في استيراد المكتبات: {e}")
    # سننشئ البدائل الأساسية

class BasicAICore:
    def __init__(self):
        self.setup_directories()
        self.load_knowledge()
        
    def setup_directories(self):
        """إنشاء المجلدات الضرورية"""
        dirs = ['knowledge', 'memory', 'logs']
        for dir_name in dirs:
            os.makedirs(dir_name, exist_ok=True)
    
    def load_knowledge(self):
        """تحميل قاعدة المعرفة"""
        try:
            with open('knowledge/knowledge_base.json', 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
        except:
            self.knowledge = {
                "greetings": ["مرحباً!", "أهلاً وسهلاً!", "مرحباً بك في النواة الذكية"],
                "help": "أستطيع مساعدتك في البرمجة، الشبكات، الأنظمة، والأمن السيبراني"
            }
    
    def process_message(self, message):
        """معالجة الرسالة الأساسية"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['مرحب', 'اهلا', 'سلام']):
            return "مرحباً بك! 👋 أنا النواة الذكية. كيف يمكنني مساعدتك اليوم؟"
        
        elif any(word in message_lower for word in ['برمجة', 'كود', 'code']):
            return "أستطيع مساعدتك في كتابة الأكواد. أخبرني ما الذي تريد برمجته؟"
        
        elif any(word in message_lower for word in ['شبكة', 'network']):
            return "مجال الشبكات متاح! يمكنني شرح المفاهيم أو مساعدتك في تحليل الشبكات."
        
        elif any(word in message_lower for word in ['نظام', 'system']):
            return "إدارة الأنظمة؟ ممتاز! أستطيع مساعدتك في تحليل وإدارة الأنظمة."
        
        elif any(word in message_lower for word in ['أمن', 'security']):
            return "الأمن السيبراني مجال مهم! كيف يمكنني مساعدتك في تأمين أنظمتك؟"
        
        else:
            return f"أفهم أنك تقول: '{message}'. دعني أساعدك في:\n- البرمجة والتطوير\n- الشبكات والاتصالات\n- إدارة الأنظمة\n- الأمن السيبراني\n\nأي مجال تفضل؟"

def main():
    """الدالة الرئيسية للتشغيل على Android"""
    print("=" * 50)
    print("🚀 النواة الذكية المتقدمة - AI Core Engine")
    print("📱 نسخة متوافقة مع Samsung S24 Ultra")
    print("=" * 50)
    print("\nالمجالات المتاحة:")
    print("🔹 البرمجة وتطوير الأكواد")
    print("🔹 الشبكات والاتصالات") 
    print("🔹 إدارة الأنظمة")
    print("🔹 الأمن السيبراني")
    print("🔹 إدارة المشاريع")
    print("=" * 50)
    print("اكتب 'خروج' للإنهاء")
    print("=" * 50)
    
    try:
        ai_core = AICoreBrain()
        print("✅ النواة المتقدمة جاهزة!")
    except:
        ai_core = BasicAICore()
        print("✅ النواة الأساسية جاهزة!")
    
    while True:
        try:
            user_input = input("\n👤 أنت: ").strip()
            
            if user_input.lower() in ['خروج', 'exit', 'quit']:
                print("👋 مع السلامة! إلى اللقاء.")
                break
                
            if not user_input:
                continue
                
            # معالجة الرسالة
            if hasattr(ai_core, 'process_message'):
                response = ai_core.process_message(user_input)
            else:
                response = "النظام قيد التطوير..."
                
            print(f"🤖 النواة: {response}")
            
        except KeyboardInterrupt:
            print("\n\n⏹️ تم إيقاف البرنامج")
            break
        except Exception as e:
            print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    main()
