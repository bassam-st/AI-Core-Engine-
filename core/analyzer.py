# core/analyzer.py - محلل النصوص
import re
import json

class AdvancedAnalyzer:
    def __init__(self):
        self.setup_patterns()
    
    def setup_patterns(self):
        """إعداد أنماط التحليل"""
        self.patterns = {
            "code_request": [r"اكتب.*كود", r"انشئ.*برنامج", r"سكريبت", r"برمجة"],
            "network_request": [r"شبكة", r"انترنت", r"اتصال", r"راوتر", r"ip"],
            "system_request": [r"نظام", r"خادم", r"سيرفر", r"أوبنتو", r"لينكس"],
            "security_request": [r"أمن", r"حماية", r"اختراق", r"فايروس"],
            "project_request": [r"مشروع", r"بدء", r"إنشاء", r"جديد"]
        }
    
    def analyze(self, message, user_id="default"):
        """تحليل متقدم للرسالة"""
        message_lower = message.lower()
        
        analysis = {
            "intent": "general",
            "urgency": "low",
            "complexity": "medium",
            "topics": [],
            "needs_code": False,
            "needs_explanation": False,
            "user_id": user_id
        }
        
        # تحليل النية
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    analysis["intent"] = intent.replace("_request", "")
                    break
        
        # تحليل المواضيع
        topics = self.extract_topics(message)
        analysis["topics"] = topics
        
        # تحليل التعقيد
        word_count = len(message.split())
        if word_count > 20:
            analysis["complexity"] = "high"
        elif word_count > 10:
            analysis["complexity"] = "medium"
        else:
            analysis["complexity"] = "low"
        
        # تحليل الاستعجال
        urgent_words = ["ضروري", "عاجل", "الآن", "سريع", "مشكلة"]
        if any(word in message_lower for word in urgent_words):
            analysis["urgency"] = "high"
        
        # تحليل الاحتياجات
        if any(word in message_lower for word in ["كود", "برنامج", "سكريبت"]):
            analysis["needs_code"] = True
        
        if any(word in message_lower for word in ["شرح", "كيف", "لماذا", "ماذا"]):
            analysis["needs_explanation"] = True
        
        return analysis
    
    def extract_topics(self, message):
        """استخراج المواضيع من الرسالة"""
        topics = []
        topic_keywords = {
            "python": ["بايثون", "python"],
            "web": ["ويب", "موقع", "web"],
            "network": ["شبكة", "انترنت", "network"],
            "security": ["أمن", "حماية", "security"],
            "linux": ["لينكس", "أوبنتو", "linux"],
            "database": ["قاعدة بيانات", "داتابيس", "database"]
        }
        
        message_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    topics.append(topic)
                    break
        
        return topics
