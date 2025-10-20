# core/learner.py - نظام التعلم
import json
import os
from datetime import datetime

class AdaptiveLearner:
    def __init__(self):
        self.learning_data = self.load_learning_data()
    
    def load_learning_data(self):
        """تحميل بيانات التعلم"""
        try:
            with open('memory/learning_cache.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "user_preferences": {},
                "common_questions": {},
                "response_effectiveness": {},
                "learned_patterns": {}
            }
    
    def save_learning_data(self):
        """حفظ بيانات التعلم"""
        try:
            with open('memory/learning_cache.json', 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def learn_from_message(self, message, analysis, user_id):
        """التعلم من الرسالة"""
        # تعلم تفضيلات المستخدم
        if user_id not in self.learning_data["user_preferences"]:
            self.learning_data["user_preferences"][user_id] = {
                "preferred_topics": [],
                "interaction_count": 0,
                "last_interaction": datetime.now().isoformat()
            }
        
        user_data = self.learning_data["user_preferences"][user_id]
        user_data["interaction_count"] += 1
        user_data["last_interaction"] = datetime.now().isoformat()
        
        # إضافة المواضيع المفضلة
        for topic in analysis.get("topics", []):
            if topic not in user_data["preferred_topics"]:
                user_data["preferred_topics"].append(topic)
        
        # تعلم الأسئلة الشائعة
        question_key = message[:50]  # استخدام أول 50 حرف كمفتاح
        if question_key in self.learning_data["common_questions"]:
            self.learning_data["common_questions"][question_key]["count"] += 1
        else:
            self.learning_data["common_questions"][question_key] = {
                "question": message,
                "count": 1,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "intent": analysis.get("intent", "general")
            }
        
        self.save_learning_data()
    
    def get_user_preferences(self, user_id):
        """الحصول على تفضيلات المستخدم"""
        return self.learning_data["user_preferences"].get(user_id, {})
    
    def get_common_questions(self, limit=5):
        """الحصول على الأسئلة الشائعة"""
        questions = list(self.learning_data["common_questions"].values())
        questions.sort(key=lambda x: x["count"], reverse=True)
        return questions[:limit]
