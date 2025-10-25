# core/brain.py — النواة الذكية المتقدمة
from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import logging
import re
from datetime import datetime

from core.memory import search_memory, add_fact, save_conv, get_context
from core.web_search import web_search, fetch_text, wiki_summary_ar
from core.code_team import build_project
from core.coder import generate_code
from core.learn_loop import learn_from_conversation

# إعداد التسجيل
logger = logging.getLogger(__name__)

class IntentAnalyzer:
    """محلل نوايا متقدم"""
    
    def __init__(self):
        self.code_patterns = [
            r"(اكتب|انشئ|اصنع|برمج)(.*)(كود|برنامج|دالة|سكريبت)",
            r"(كود|برمجة|شفرة)\s+(ل|في)\s+",
            r"(python|javascript|java|html|css|sql)\s+"
        ]
        
        self.project_patterns = [
            r"(ابني|انشئ|اصنع)(.*)(مشروع|نظام|تطبيق|موقع)",
            r"(مشروع|تطبيق)\s+(ل|في)\s+",
            r"(تصميم|برمجة)\s+(موقع|تطبيق)"
        ]
        
        self.question_patterns = [
            r"(ما هو|ماهو|ما هي|ماهي|كيف|لماذا|أين|متى)",
            r"(شرح|تعريف|مفهوم)\s+",
            r"(ما رأيك|ما تقول)\s+في"
        ]

    def analyze(self, text: str) -> Dict:
        """تحليل النوايا مع تقييم الثقة"""
        text = self._normalize_text(text)
        
        intents = []
        
        # تحليل النوايا
        if self._matches_patterns(text, self.code_patterns):
            intents.append({"type": "code", "confidence": 0.85})
        
        if self._matches_patterns(text, self.project_patterns):
            intents.append({"type": "project", "confidence": 0.80})
            
        if self._matches_patterns(text, self.question_patterns):
            intents.append({"type": "question", "confidence": 0.75})
        
        # إذا لم توجد نوايا واضحة
        if not intents:
            if len(text.split()) <= 4:
                intents.append({"type": "small_talk", "confidence": 0.90})
            else:
                intents.append({"type": "general_search", "confidence": 0.70})
        
        # ترتيب حسب الثقة
        intents.sort(key=lambda x: x["confidence"], reverse=True)
        return intents[0] if intents else {"type": "unknown", "confidence": 0.5}

    def _normalize_text(self, text: str) -> str:
        """تنقية النص للتحليل"""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return ' '.join(text.split())

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """التحقق من تطابق الأنماط"""
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

class ResponseGenerator:
    """مولد ردود ذكي"""
    
    def __init__(self):
        self.openers = {
            "code": "🔧 هذا الكود الذي طلبته:",
            "project": "🚀 بدأت بناء مشروعك:",
            "question": "📚 إليك ما وجدته:",
            "general_search": "🔍 هذه المعلومات المتاحة:",
            "small_talk": "👋 "
        }
        
        self.fallbacks = {
            "code": "لم أستطع توليد كود مناسب. يمكنك توضيح المتطلبات أكثر؟",
            "project": "أحتاج مزيداً من التفاصيل عن المشروع المطلوب.",
            "question": "لم أجد معلومات كافية. جرب صياغة أخرى أو اسأل عن موضوع مختلف.",
            "general_search": "لم أتمكن من العثور على معلومات كافية. هل يمكنك إعادة الصياغة؟"
        }

    def generate_opener(self, intent_type: str) -> str:
        """توليد مقدمة مناسبة للنوايا"""
        return self.openers.get(intent_type, "💡 ")

    def generate_fallback(self, intent_type: str) -> str:
        """توليد رد بديل عندما لا توجد نتائج"""
        return self.fallbacks.get(intent_type, "لم أتمكن من المعالجة. حاول مرة أخرى.")

class ConversationManager:
    """مدير المحادثات المتقدم"""
    
    def __init__(self):
        self.context_history = []
        self.max_context_length = 5

    def add_context(self, user_msg: str, bot_msg: str):
        """إضافة سياق للمحادثة"""
        context = {
            "user": user_msg,
            "bot": bot_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.context_history.append(context)
        
        # الحفاظ على طول معقول للسياق
        if len(self.context_history) > self.max_context_length:
            self.context_history.pop(0)

    def get_recent_context(self) -> List[Dict]:
        """الحصول على السياق الحديث"""
        return self.context_history[-2:] if len(self.context_history) >= 2 else []

# الكائنات العالمية
intent_analyzer = IntentAnalyzer()
response_generator = ResponseGenerator()
conversation_manager = ConversationManager()

def enhanced_chat_answer(q: str) -> Tuple[str, List[dict]]:
    """
    نسخة محسنة من chat_answer مع تحليل نوايا متقدم
    """
    q = (q or "").strip()
    if not q:
        return "الرجاء إدخال سؤال أو طلب.", []

    logger.info(f"معالجة رسالة: {q}")

    try:
        # 1. تحليل النوايا
        intent = intent_analyzer.analyze(q)
        logger.info(f"تم تحليل النوايا: {intent}")

        # 2. معالجة حسب النوايا
        if intent["type"] == "code" and intent["confidence"] > 0.7:
            return handle_code_request(q, intent)
            
        elif intent["type"] == "project" and intent["confidence"] > 0.7:
            return handle_project_request(q, intent)
            
        elif intent["type"] == "question":
            return handle_question_request(q, intent)
            
        else:
            return handle_general_request(q, intent)

    except Exception as e:
        logger.error(f"خطأ في المعالجة: {e}")
        return "حدث خطأ في المعالجة. الرجاء المحاولة مرة أخرى.", []

def handle_code_request(q: str, intent: Dict) -> Tuple[str, List[dict]]:
    """معالجة طلبات الأكواد"""
    try:
        result = generate_code(q)
        
        if result and result.get("code"):
            code = result["code"]
            lang = result.get("lang", "غير محدد")
            title = result.get("title", "كود مطلوب")
            
            # تحسين جودة الكود
            if is_valid_code(code, lang):
                response = f"{response_generator.generate_opener('code')}\n\n"
                response += f"**{title}** ({lang})\n\n"
                response += f"```{lang}\n{code}\n```"
                
                # حفظ في الذاكرة
                add_fact(f"كود {lang}: {title}", source="code_generation")
                save_conv(q, response)
                
                return response, []
            else:
                return "الكود المُولد يحتاج تحسين. هل يمكنك توضيح المتطلبات؟", []
        else:
            return response_generator.generate_fallback("code"), []

    except Exception as e:
        logger.error(f"خطأ في توليد الكود: {e}")
        return "حدث خطأ في توليد الكود. حاول مرة أخرى.", []

def handle_project_request(q: str, intent: Dict) -> Tuple[str, List[dict]]:
    """معالجة طلبات المشاريع"""
    try:
        result = build_project(q)
        
        if result.get("ok"):
            files = result.get("files", {})
            issues = result.get("issues", [])
            tips = result.get("tips", "")
            
            response = f"{response_generator.generate_opener('project')}\n\n"
            response += f"📁 **الملفات:** {', '.join(files.keys())}\n"
            response += f"⚠️ **الملاحظات:** {len(issues)}\n"
            response += f"💡 **نصيحة:** {tips}\n\n"
            
            # عرض أول ملف كمثال
            if files:
                first_file = list(files.keys())[0]
                file_content = files[first_file][:500] + "..." if len(files[first_file]) > 500 else files[first_file]
                response += f"**مثال من {first_file}:**\n```\n{file_content}\n```"
            
            # حفظ في الذاكرة
            for filename in list(files.keys())[:3]:
                add_fact(f"ملف مشروع: {filename}", source="project_builder")
            
            save_conv(q, response)
            return response, []
        else:
            return response_generator.generate_fallback("project"), []

    except Exception as e:
        logger.error(f"خطأ في بناء المشروع: {e}")
        return "حدث خطأ في بناء المشروع. حاول مرة أخرى.", []

def handle_question_request(q: str, intent: Dict) -> Tuple[str, List[dict]]:
    """معالجة الأسئلة والاستفسارات"""
    # البحث في الذاكرة أولاً
    mem_results = search_memory(q, limit=8)
    mem_texts = [r["text"] for r in mem_results if r["score"] > 0.2]
    
    # إذا كانت الذاكرة كافية
    if mem_texts and any(r["score"] > 1.0 for r in mem_results):
        response = f"{response_generator.generate_opener('question')}\n"
        response += "\n".join([f"• {text}" for text in mem_texts[:3]])
        save_conv(q, response)
        return response, []

    # البحث في الويب إذا لزم الأمر
    try:
        web_results = web_search(q, max_results=5)
        sources = []
        
        if web_results:
            # استخراج المعلومات المفيدة
            useful_info = extract_useful_info(web_results[:3])
            if useful_info:
                response = f"{response_generator.generate_opener('question')}\n"
                response += "\n".join([f"• {info}" for info in useful_info[:4]])
                sources = [{"title": r.get("title", ""), "url": r.get("url", "")} for r in web_results[:3]]
                
                # التعلم من المعلومات الجديدة
                for info in useful_info[:2]:
                    if should_learn_info(info):
                        add_fact(info, source="web_learning")
                
                save_conv(q, response)
                return response, sources

    except Exception as e:
        logger.error(f"خطأ في البحث: {e}")

    return response_generator.generate_fallback("question"), []

def handle_general_request(q: str, intent: Dict) -> Tuple[str, List[dict]]:
    """معالجة الطلبات العامة"""
    # البحث المباشر في الذاكرة والويب
    mem_results = search_memory(q, limit=5)
    mem_texts = [r["text"] for r in mem_results if r["score"] > 0.1]
    
    try:
        web_results = web_search(q, max_results=4)
        useful_info = extract_useful_info(web_results[:2]) if web_results else []
        
        all_info = mem_texts + useful_info
        
        if all_info:
            response = f"{response_generator.generate_opener('general_search')}\n"
            response += "\n".join([f"• {info}" for info in all_info[:5]])
            sources = [{"title": r.get("title", ""), "url": r.get("url", "")} for r in web_results[:3]] if web_results else []
            
            save_conv(q, response)
            return response, sources
        else:
            return response_generator.generate_fallback("general_search"), []

    except Exception as e:
        logger.error(f"خطأ في المعالجة العامة: {e}")
        return "لم أتمكن من العثور على معلومات. جرب صياغة أخرى.", []

def is_valid_code(code: str, lang: str) -> bool:
    """التحقق من جودة الكود"""
    if not code or len(code.strip()) < 10:
        return False
        
    if lang == "html" and not any(tag in code for tag in ["<html", "<body", "<div"]):
        return False
        
    if lang == "python" and not any(char in code for char in [":", "def ", "import "]):
        return False
        
    return True

def extract_useful_info(web_results: List[Dict]) -> List[str]:
    """استخراج المعلومات المفيدة من نتائج الويب"""
    useful_info = []
    
    for result in web_results:
        snippet = result.get("snippet", "") or result.get("body", "")
        if snippet and len(snippet) > 50:
            # تقسيم إلى جمل مفيدة
            sentences = [s.strip() for s in snippet.split(".") if 20 < len(s.strip()) < 200]
            useful_info.extend(sentences[:2])
    
    return useful_info[:6]  # الحد الأقصى 6 جمل

def should_learn_info(info: str) -> bool:
    """تحديد إذا كانت المعلومات تستحق التعلم"""
    if len(info) < 30:
        return False
        
    excluded_phrases = ["انقر هنا", "للمزيد", "اشترك الآن", "إعلان"]
    if any(phrase in info for phrase in excluded_phrases):
        return False
        
    return True

# دالة التوافق مع الإصدار السابق
def chat_answer(q: str) -> Tuple[str, List[dict]]:
    """واجهة متوافقة مع الإصدار السابق"""
    return enhanced_chat_answer(q)
