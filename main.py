#!/usr/bin/env python3
# النواة الذكية المتقدمة - إصدار النخبة

import os
import json
import logging
import requests
import re
import base64
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
import numpy as np
import nltk
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
import io
import csv
import sqlite3

# تحميل النماذج المتقدمة
try:
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    MODEL_LOADED = True
    print("✅ تم تحميل النماذج المتقدمة بنجاح!")
except Exception as e:
    print(f"⚠️  تعذر تحميل النماذج المتقدمة: {e}")
    MODEL_LOADED = False

app = Flask(__name__)

class EliteAICore:
    def __init__(self):
        self.setup_directories()
        self.load_advanced_knowledge()
        self.setup_nltk()
        self.conversation_memory = []
        self.user_profiles = {}
        
    def setup_directories(self):
        """إنشاء مجلدات متقدمة"""
        dirs = ['knowledge', 'memory', 'models', 'cache', 'projects', 'uploads']
        for dir_name in dirs:
            os.makedirs(dir_name, exist_ok=True)
    
    def setup_nltk(self):
        """إعداد NLTK المتقدم"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
    
    def load_advanced_knowledge(self):
        """تحميل معرفة النخبة"""
        try:
            with open('knowledge/elite_knowledge.json', 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
            print("✅ تم تحميل المعرفة المتقدمة بنجاح!")
        except Exception as e:
            print(f"⚠️  تعذر تحميل المعرفة: {e}")
            self.knowledge = self.create_elite_knowledge()
    
    def create_elite_knowledge(self):
        """إنشاء معرفة النخبة"""
        elite_knowledge = {
            "expert_qa": {
                "برمجة متقدمة": {
                    "كيف أنشئ API متقدم؟": "لإنشاء API متقدم: 1) استخدم FastAPI أو Flask-RESTful 2) أضف المصادقة JWT 3) نفذ rate limiting 4) وثق API باستخدام Swagger",
                    "ما هي microservices؟": "هندسة microservices تقسم التطبيق إلى خدمات صغيرة مستقلة، كل خدمة تركز على وظيفة محددة وتتواصل عبر APIs.",
                    "كيف أحسن أداء قاعدة البيانات؟": "1) فهرسة الجداول 2) استخدم queries فعالة 3) اضبط إعدادات cache 4) استخدم connection pooling",
                    "ما هو Docker وكيف أستخدمه؟": "Docker نظام containerization يحزم التطبيق واعتماداته في حاوية قابلة للنشر على أي نظام.",
                    "كيف أنشئ تطبيق تعلم آلي؟": "1) جمع البيانات 2) تنظيف البيانات 3) اختيار النموذج 4) التدريب 5) التقييم 6) النشر"
                },
                "أمن سيبراني": {
                    "كأحمي خادمي؟": "1) تحديث النظام 2) جدار حماية 3) fail2ban 4) تعطيل login بالroot 5) استخدام SSH keys",
                    "ما هي هجمات DDoS؟": "هجمات الحرمان من الخدمة تهدف لإغراق الخادم بطلبات زائفة لمنع الوصول للخدمة الحقيقية.",
                    "كيف أكتشف الاختراقات؟": "راقب سجلات النظام، استخدم أنظمة كشف التسلل، افحص العمليات غير المعتادة، تتبع اتصالات الشبكة.",
                    "ما هو penetration testing؟": "اختبار الاختراق هو محاكاة هجمات حقيقية لاكتشاف الثغرات الأمنية في النظام."
                },
                "ذكاء اصطناعي": {
                    "ما هو الفرق بين AI و ML؟": "الذكاء الاصطناعي مفهوم أوسع، التعلم الآلي جزء منه يركز على تعلم النماذج من البيانات.",
                    "كيف أعمل نموذج تعلم عميق؟": "1) TensorFlow/PyTorch 2) بناء architecture 3) تدريب النموذج 4) ضبط hyperparameters 5) التقييم",
                    "ما هي الشبكات العصبية؟": "محاكاة للدماغ البشري، تتكون من طبقات عصبونية تتعلم الأنماط المعقدة من البيانات."
                }
            },
            "code_templates": {
                "python_ai_chatbot": """import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

class AdvancedChatBot:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.knowledge_base = {
            'greetings': ['مرحباً', 'أهلاً', 'اهلاوسهلا'],
            'questions': {
                'ما هو اسمك': 'أنا بوت الدردشة الذكي!',
                'كيف حالك': 'أنا بخير، شكراً لسؤالك!'
            }
        }
    
    def respond(self, message):
        # محاكاة ذكاء اصطناعي بسيط
        if any(greet in message for greet in self.knowledge_base['greetings']):
            return 'مرحباً بك! كيف يمكنني مساعدتك؟'
        
        for question, answer in self.knowledge_base['questions'].items():
            if question in message:
                return answer
        
        return 'هذا سؤال مثير للاهتمام! دعني أفكر في إجابة مناسبة.'

# استخدام البوت
bot = AdvancedChatBot()
print(bot.respond('مرحباً'))""",

                "react_components": """import React, { useState, useEffect } from 'react';
import './App.css';

function AdvancedApp() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/data')
      .then(response => response.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>جاري التحميل...</div>;

  return (
    <div className="app">
      <h1>تطبيق React متقدم</h1>
      <div className="data-grid">
        {data.map(item => (
          <div key={item.id} className="card">
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AdvancedApp;""",

                "nodejs_api": """const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const app = express();

app.use(express.json());

// قاعدة بيانات مؤقتة
const users = [];
const posts = [];

// middleware المصادقة
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'الوصول مرفوض' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'رمز غير صالح' });
    req.user = user;
    next();
  });
};

// routes
app.post('/register', async (req, res) => {
  try {
    const hashedPassword = await bcrypt.hash(req.body.password, 10);
    const user = { 
      id: users.length + 1, 
      username: req.body.username, 
      password: hashedPassword 
    };
    users.push(user);
    res.status(201).json({ message: 'تم إنشاء الحساب بنجاح' });
  } catch {
    res.status(500).json({ error: 'خطأ في الخادم' });
  }
});

app.listen(3000, () => {
  console.log('الخادم يعمل على port 3000');
});"""
            },
            "learning_paths": {
                "مطور ويب متكامل": [
                    "HTML5 & CSS3 المتقدم",
                    "JavaScript ES6+",
                    "React أو Vue.js", 
                    "Node.js و Express",
                    "قواعد البيانات SQL/NoSQL",
                    "DevOps والنشر"
                ],
                "خبير أمن سيبراني": [
                    "أساسيات الشبكات",
                    "أنظمة التشغيل",
                    "أدوات الأمن",
                    "اختبار الاختراق",
                    "تحقيق جرائم رقمية",
                    "تأمين السحابة"
                ],
                "مهندس تعلم آلي": [
                    "Python للإحصاء",
                    "رياضيات التعلم الآلي",
                    "مكتبات ML (scikit-learn)",
                    "التعلم العميق",
                    "معالجة اللغة الطبيعية",
                    "نشر النماذج"
                ]
            }
        }
        
        self.save_knowledge(elite_knowledge)
        return elite_knowledge
    
    def save_knowledge(self, knowledge=None):
        """حفظ المعرفة"""
        if knowledge is None:
            knowledge = self.knowledge
        
        try:
            with open('knowledge/elite_knowledge.json', 'w', encoding='utf-8') as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطأ في الحفظ: {e}")
    
    def web_search_simulation(self, query):
        """محاكاة بحث ويب ذكي"""
        search_results = {
            "أحدث تقنيات البرمجة 2024": "أهم التقنيات: 1) AI-assisted coding 2) Low-code platforms 3) WebAssembly 4) Serverless architecture 5) Edge computing",
            "مستقبل الذكاء الاصطناعي": "الاتجاهات: 1) Generative AI 2) Multimodal models 3) AI ethics 4) Quantum machine learning 5) Autonomous systems",
            "أفضل ممارسات الأمن": "1) Zero Trust Architecture 2) Multi-factor authentication 3) Regular security audits 4) Employee training 5) Incident response planning"
        }
        
        for topic, content in search_results.items():
            if any(word in query for word in topic.split()):
                return f"🔍 نتائج البحث عن '{query}':\n\n{content}"
        
        return f"🔍 لم أجد نتائج دقيقة لـ '{query}'. جرب البحث عن: أحدث تقنيات البرمجة، مستقبل الذكاء الاصطناعي، أو أفضل ممارسات الأمن."
    
    def analyze_sentiment(self, text):
        """تحليل مشاعر النص"""
        positive_words = ['جيد', 'ممتاز', 'رائع', 'شكرا', 'جميل', 'مذهل']
        negative_words = ['سيء', 'مشكلة', 'خطأ', 'لا يعمل', 'صعب', 'معقد']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "إيجابي"
        elif negative_count > positive_count:
            return "سلبي"
        else:
            return "محايد"
    
    def generate_learning_path(self, topic, level="مبتدئ"):
        """توليد مسار تعلم مخصص"""
        paths = {
            "برمجة": {
                "مبتدئ": ["مقدمة في البرمجة", "أساسيات Python", "مشاريع بسيطة", "تعلم Git"],
                "متوسط": ["هياكل البيانات", "قواعد البيانات", "APIs", "مشاريع متوسطة"],
                "متقدم": ["هندسة البرمجيات", "التصميم patterns", "الخوارزميات", "مشاريع معقدة"]
            },
            "شبكات": {
                "مبتدئ": ["أساسيات الشبكات", "بروتوكول TCP/IP", "أجهزة الشبكة", "تصميم شبكات صغيرة"],
                "متوسط": ["شبكات enterprise", "الأمن الشبكي", "بروتوكولات التوجيه", "إدارة الشبكات"],
                "متقدم": ["شبكات متقدمة", "virtualization", "SDN", "أمن متقدم"]
            }
        }
        
        if topic in paths and level in paths[topic]:
            path = paths[topic][level]
            return f"🎯 مسار تعلم {topic} للمستوى {level}:\n\n" + "\n".join([f"• {item}" for item in path])
        
        return f"أستطيع إنشاء مسارات تعلم للبرمجة، الشبكات، الأمن السيبراني، والذكاء الاصطناعي. أي مجال تفضل؟"
    
    def code_review(self, code):
        """مراجعة وتحليل الكود"""
        issues = []
        
        # فحص أخطاء شائعة
        if "import os" in code and "subprocess" in code:
            issues.append("⚠️ استخدام مكتبات نظام قد يحتاج تحقق أمني")
        
        if "password" in code.lower() and "encrypt" not in code.lower():
            issues.append("🔒 كلمات المرور يجب تشفيرها")
        
        if "select *" in code.lower():
            issues.append("🗃️ تجنب SELECT *، حدد الأعمدة المطلوبة فقط")
        
        if issues:
            return "🔍 مراجعة الكود:\n" + "\n".join(issues)
        else:
            return "✅ الكود يبدو جيداً! لا توجد مشاكل واضحة."
    
    def generate_project_idea(self, field, complexity="medium"):
        """توليد أفكار مشاريع"""
        projects = {
            "برمجة": {
                "easy": ["آلة حاسبة", "قائمة مهام", "محول العملات", "تطبيق طقس"],
                "medium": ["منصة مدونة", "متجر إلكتروني", "نظام حجوزات", "تطبيق دردشة"],
                "hard": ["منصة تعلم", "نظام توصيات", "بوت ذكي", "تطبيق تعلم آلي"]
            },
            "شبكات": {
                "easy": ["ماسح شبكة", "أداة ping متقدمة", "محلل حزم بسيط"],
                "medium": ["جدار حماية", "نظام مراقبة شبكة", "خادم VPN"],
                "hard": ["نظام كشف تسلل", "شبكة افتراضية", "منصة أمن متكاملة"]
            }
        }
        
        if field in projects and complexity in projects[field]:
            ideas = projects[field][complexity]
            idea = np.random.choice(ideas)
            return f"💡 فكرة مشروع {field} ({complexity}):\n\n{idea}\n\nمستوى الصعوبة: {complexity}"
        
        return "أستطيع اقتراح مشاريع في البرمجة، الشبكات، الأمن، والذكاء الاصطناعي."
    
    def process_advanced_message(self, message, user_id="default"):
        """معالجة متقدمة للرسائل"""
        message_lower = message.lower()
        
        # تحديث ملف المستخدم
        self.update_user_profile(user_id, message)
        
        # تحليل متقدم
        sentiment = self.analyze_sentiment(message)
        intent = self.analyze_advanced_intent(message)
        
        # توليد رد متقدم
        if "ابحث عن" in message or "ما هي آخر" in message:
            response = self.web_search_simulation(message)
        
        elif "مسار تعلم" in message or "كيف أتعلم" in message:
            topic = self.extract_topic(message)
            level = "مبتدئ" if "مبتدئ" in message else "متوسط"
            response = self.generate_learning_path(topic, level)
        
        elif "راجع الكود" in message or "حلل الكود" in message:
            code = self.extract_code(message)
            response = self.code_review(code) if code else "أرسل الكود الذي تريد مراجعته"
        
        elif "فكرة مشروع" in message:
            field = self.extract_field(message)
            complexity = "medium"
            response = self.generate_project_idea(field, complexity)
        
        elif "أنشئ لي" in message and "كود" in message:
            response = self.generate_elite_code(message)
        
        else:
            # البحث في الأسئلة الخبيرة
            answer = self.find_expert_answer(message)
            response = answer if answer else self.generate_creative_response(message, sentiment)
        
        # حفظ الذاكرة
        self.save_to_memory(user_id, message, response, intent, sentiment)
        
        return {
            "message": response,
            "analysis": {
                "intent": intent,
                "sentiment": sentiment,
                "user_level": self.get_user_level(user_id),
                "response_type": "advanced_ai"
            }
        }
    
    def extract_topic(self, message):
        """استخراج الموضوع من الرسالة"""
        topics = ["برمجة", "شبكات", "أمن", "ذكاء اصطناعي", "قواعد بيانات"]
        for topic in topics:
            if topic in message:
                return topic
        return "برمجة"
    
    def extract_field(self, message):
        """استخراج المجال من الرسالة"""
        fields = ["برمجة", "شبكات", "أمن", "ويب", "جوال"]
        for field in fields:
            if field in message:
                return field
        return "برمجة"
    
    def extract_code(self, message):
        """استخراج الكود من الرسالة"""
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', message, re.DOTALL)
        return code_blocks[0] if code_blocks else None
    
    def find_expert_answer(self, question):
        """البحث في الأسئلة الخبيرة"""
        best_score = 0
        best_answer = None
        
        for category, qa_pairs in self.knowledge["expert_qa"].items():
            for q, a in qa_pairs.items():
                score = self.semantic_similarity(question, q)
                if score > best_score and score > 0.4:
                    best_score = score
                    best_answer = f"🎓 {a}"
        
        return best_answer
    
    def generate_elite_code(self, message):
        """توليد أكواد النخبة"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["بوت", "chatbot", "دردشة"]):
            return f"🤖 كود بوت ذكي متقدم:\n\n```python\n{self.knowledge['code_templates']['python_ai_chatbot']}\n```"
        
        elif any(word in message_lower for word in ["react", "واجهة", "frontend"]):
            return f"⚛️ كود React متقدم:\n\n```jsx\n{self.knowledge['code_templates']['react_components']}\n```"
        
        elif any(word in message_lower for word in ["api", "خادم", "server"]):
            return f"🔗 كود Node.js API متقدم:\n\n```javascript\n{self.knowledge['code_templates']['nodejs_api']}\n```"
        
        else:
            return "أستطيع إنشاء: بوتات ذكية، واجهات React، APIs متقدمة، وأنظمة معقدة. ما الذي تريد بالضبط؟"
    
    def generate_creative_response(self, message, sentiment):
        """توليد ردود إبداعية"""
        creative_responses = [
            "🤔 هذا سؤال عميق! دعني أفكر في أفضل طريقة للإجابة...",
            "🎯 أرى أنك تبحث عن معرفة متقدمة. هذا ممتاز!",
            "💡 فكرة رائعة! هل تريدني أن أعمق أكثر في هذا الموضوع؟",
            "🚀 هذا يذكرني بتقنيات متقدمة في المجال. هل تريد استكشافها؟",
            "🔍 سأبحث في أحدث التطورات حول هذا الموضوع وأعود إليك بمعلومات شاملة."
        ]
        
        return np.random.choice(creative_responses) + f"\n\n(تحليل المشاعر: {sentiment})"
    
    def analyze_advanced_intent(self, message):
        """تحليل النية المتقدم"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["ابحث", "أخبار", "جديد", "مستجد"]):
            return "بحث_معلومات"
        elif any(word in message_lower for word in ["مسار", "تعلم", "كورس", "دورة"]):
            return "تعلم_وتطوير"
        elif any(word in message_lower for word in ["راجع", "حلل", "افحص", "كود"]):
            return "مراجعة_كود"
        elif any(word in message_lower for word in ["مشروع", "فكرة", "بناء", "أنشئ"]):
            return "إبداع_مشاريع"
        elif any(word in message_lower for word in ["كود", "برمجة", "سكريبت"]):
            return "توليد_كود"
        else:
            return "استفسار_عام"
    
    def update_user_profile(self, user_id, message):
        """تحديث ملف المستخدم المتقدم"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "join_date": datetime.now().isoformat(),
                "interaction_count": 0,
                "expertise_areas": [],
                "preferred_complexity": "medium",
                "learning_goals": [],
                "last_activity": datetime.now().isoformat()
            }
        
        profile = self.user_profiles[user_id]
        profile["interaction_count"] += 1
        profile["last_activity"] = datetime.now().isoformat()
        
        # تحديث مجالات الخبرة
        areas = ["برمجة", "شبكات", "أمن", "ذكاء اصطناعي", "قواعد بيانات"]
        for area in areas:
            if area in message and area not in profile["expertise_areas"]:
                profile["expertise_areas"].append(area)
    
    def get_user_level(self, user_id):
        """تحديد مستوى المستخدم"""
        if user_id not in self.user_profiles:
            return "مبتدئ"
        
        interactions = self.user_profiles[user_id]["interaction_count"]
        if interactions > 50:
            return "خبير"
        elif interactions > 20:
            return "متوسط"
        else:
            return "مبتدئ"
    
    def save_to_memory(self, user_id, user_message, ai_response, intent, sentiment):
        """حفظ في الذاكرة المتقدمة"""
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "intent": intent,
            "sentiment": sentiment,
            "user_level": self.get_user_level(user_id)
        }
        
        self.conversation_memory.append(memory_entry)
        
        # حفظ الذاكرة للملف
        try:
            with open(f'memory/{user_id}_memory.json', 'w', encoding='utf-8') as f:
                json.dump(self.conversation_memory[-100:], f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def semantic_similarity(self, text1, text2):
        """التشابه الدلالي"""
        if not MODEL_LOADED:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            common = words1.intersection(words2)
            return len(common) / max(len(words1), len(words2))
        
        emb1 = semantic_model.encode(text1, convert_to_tensor=True)
        emb2 = semantic_model.encode(text2, convert_to_tensor=True)
        return util.pytorch_cos_sim(emb1, emb2).item()

# تهيئة النواة المتطورة
ai_core = EliteAICore()

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
        
        # معالجة متقدمة
        result = ai_core.process_advanced_message(user_message, user_id)
        
        return jsonify({
            'response': result['message'],
            'analysis': result['analysis'],
            'model_loaded': MODEL_LOADED,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"خطأ في المعالجة المتقدمة: {e}")
        return jsonify({'error': 'حدث خطأ في المعالجة'}), 500

@app.route('/api/user/profile/<user_id>')
def get_user_profile(user_id):
    """الحصول على ملف المستخدم"""
    profile = ai_core.user_profiles.get(user_id, {})
    return jsonify({
        'profile': profile,
        'level': ai_core.get_user_level(user_id),
        'total_interactions': len(ai_core.conversation_memory)
    })

@app.route('/api/learning/path')
def get_learning_path():
    """الحصول على مسار تعلم"""
    topic = request.args.get('topic', 'برمجة')
    level = request.args.get('level', 'مبتدئ')
    
    path = ai_core.generate_learning_path(topic, level)
    return jsonify({'learning_path': path})

@app.route('/api/project/idea')
def get_project_idea():
    """الحصول على فكرة مشروع"""
    field = request.args.get('field', 'برمجة')
    complexity = request.args.get('complexity', 'medium')
    
    idea = ai_core.generate_project_idea(field, complexity)
    return jsonify({'project_idea': idea})

@app.route('/health')
def health_check():
    """فحص صحة النظام"""
    return jsonify({
        'status': 'running',
        'model_loaded': MODEL_LOADED,
        'version': 'elite_2.0.0',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
