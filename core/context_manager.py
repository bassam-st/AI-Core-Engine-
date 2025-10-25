# core/context_manager.py — نظام إدارة السياق الذكي والمتقدم
from __future__ import annotations
import logging
import re
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# إعداد التسجيل
logger = logging.getLogger(__name__)

class ContextType(Enum):
    """أنواع السياقات المختلفة"""
    CONVERSATION = "conversation"
    USER_PREFERENCE = "user_preference"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    TEMPORAL = "temporal"
    GEOGRAPHICAL = "geographical"
    TECHNICAL = "technical"
    EMOTIONAL = "emotional"

class PriorityLevel(Enum):
    """مستويات أولوية السياق"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    BACKGROUND = 1

@dataclass
class ContextItem:
    """عنصر سياق فردي"""
    id: str
    type: ContextType
    content: Dict[str, Any]
    priority: PriorityLevel
    created_at: float
    expires_at: Optional[float] = None
    source: str = "system"
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.expires_at is None:
            # افتراضي: انتهاء بعد ساعة للسياقات المؤقتة
            self.expires_at = self.created_at + 3600

    def is_expired(self) -> bool:
        """التحقق من انتهاء صلاحية السياق"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "source": self.source,
            "confidence": self.confidence,
            "metadata": self.metadata
        }

class ContextManager:
    """مدير السياق المتقدم - يحافظ على فهم عميق للمحادثة"""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.context_store: Dict[str, ContextItem] = {}
        self.conversation_history: List[Dict] = []
        self.user_profile: Dict[str, Any] = {}
        self.domain_context: Dict[str, Any] = {}
        self.temporal_context: Dict[str, Any] = {}
        
        # إعدادات السياق
        self.max_conversation_history = 50
        self.max_context_items = 100
        self.context_ttl = 3600  # ثانية واحدة
        
        # أنماط الكشف التلقائي
        self.domain_patterns = {
            "programming": [r"كود", r"برمجة", r"بايثون", r"جافا", r"html", r"css", r"سكريبت"],
            "technology": [r"تقنية", r"تكنولوجيا", r"ذكاء", r"آلة", r"بيانات", r"سيرفر"],
            "science": [r"علم", r"بحث", r"دراسة", r"نظرية", r"تجربة"],
            "business": [r"تجارة", r"شركة", r"سوق", ر"ربح", ر"استثمار"],
            "education": [r"تعلم", r"دراسة", ر"مدرسة", ر"جامعة", ر"تعليم"]
        }
        
        logger.info(f"🚀 تم تهيئة مدير السياق للجلسة: {session_id}")

    def add_conversation_turn(self, user_message: str, bot_response: str, metadata: Dict = None):
        """إضافة دور محادثة جديد إلى التاريخ"""
        turn = {
            "user": user_message,
            "bot": bot_response,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(turn)
        
        # الحفاظ على طول معقول للسجل
        if len(self.conversation_history) > self.max_conversation_history:
            self.conversation_history.pop(0)
        
        # تحديث السياق تلقائياً
        self._auto_update_context(user_message, bot_response)
        
        logger.debug(f"📝 تم إضافة دور محادثة ({len(self.conversation_history)} أدوار)")

    def _auto_update_context(self, user_message: str, bot_response: str):
        """التحديث التلقائي للسياق بناءً على المحادثة"""
        
        # كشف المجال التلقائي
        detected_domains = self._detect_domains(user_message)
        for domain in detected_domains:
            self.update_domain_context(domain, {"last_mentioned": time.time()})
        
        # استخراج التفضيلات
        preferences = self._extract_preferences(user_message)
        for pref_key, pref_value in preferences.items():
            self.update_user_preference(pref_key, pref_value)
        
        # تحديث السياق العاطفي
        emotional_context = self._analyze_emotional_context(user_message, bot_response)
        if emotional_context:
            self.add_context_item(
                ContextType.EMOTIONAL,
                emotional_context,
                PriorityLevel.MEDIUM
            )

    def _detect_domains(self, text: str) -> List[str]:
        """كشف المجالات التلقائي من النص"""
        detected = []
        text_lower = text.lower()
        
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected.append(domain)
                    break
        
        return detected

    def _extract_preferences(self, text: str) -> Dict[str, Any]:
        """استخراج تفضيلات المستخدم من النص"""
        preferences = {}
        
        # كشف مستوى التفصيل المفضل
        detail_indicators = {
            "high_detail": [r"بالتفصيل", r"شرح مفصل", r"تفصيلي", r"كامل"],
            "low_detail": [r"باختصار", r"ملخص", ر"بشكل مختصر", ر"سريع"]
        }
        
        for level, indicators in detail_indicators.items():
            for indicator in indicators:
                if re.search(indicator, text.lower()):
                    preferences["preferred_detail_level"] = level
                    break
        
        # كشف نوع المساعدة المفضلة
        help_indicators = {
            "practical": [r"عملي", r"تطبيقي", ر"مثال", ر"تنفيذ"],
            "theoretical": [r"نظري", ر"مفهوم", ر"شرح", ر"فهم"]
        }
        
        for help_type, indicators in help_indicators.items():
            for indicator in indicators:
                if re.search(indicator, text.lower()):
                    preferences["preferred_help_type"] = help_type
                    break
        
        return preferences

    def _analyze_emotional_context(self, user_message: str, bot_response: str) -> Dict[str, Any]:
        """تحليل السياق العاطفي"""
        emotional_indicators = {
            "frustration": [r"لا أفهم", r"لماذا", ر"مشكلة", ر"صعب", ر"معقد"],
            "satisfaction": [r"شكراً", ر"ممتاز", ر"رائع", ر"جميل", ر"أحسنت"],
            "urgency": [r"بسرعة", ر"عاجل", ر"الآن", ر"فوري"],
            "confusion": [r"ماذا", ر"كيف", ر"أين", ر"متى", ر"لماذا"]
        }
        
        emotional_state = "neutral"
        confidence = 0.0
        
        for state, indicators in emotional_indicators.items():
            for indicator in indicators:
                if re.search(indicator, user_message.lower()):
                    emotional_state = state
                    confidence = 0.7
                    break
        
        if emotional_state != "neutral":
            return {
                "emotional_state": emotional_state,
                "confidence": confidence,
                "timestamp": time.time()
            }
        
        return {}

    def add_context_item(self, context_type: ContextType, content: Dict[str, Any], 
                        priority: PriorityLevel = PriorityLevel.MEDIUM,
                        ttl: Optional[int] = None) -> str:
        """إضافة عنصر سياق جديد"""
        context_id = f"{context_type.value}_{int(time.time() * 1000)}"
        
        expires_at = None
        if ttl is not None:
            expires_at = time.time() + ttl
        
        context_item = ContextItem(
            id=context_id,
            type=context_type,
            content=content,
            priority=priority,
            created_at=time.time(),
            expires_at=expires_at,
            source="context_manager"
        )
        
        self.context_store[context_id] = context_item
        self._cleanup_expired_context()
        
        logger.debug(f"➕ تم إضافة عنصر سياق: {context_type.value} (الأولوية: {priority.value})")
        return context_id

    def get_relevant_context(self, query: str, limit: int = 10) -> List[ContextItem]:
        """الحصول على السياق ذي الصلة بالاستعلام"""
        self._cleanup_expired_context()
        
        relevant_items = []
        
        for item in self.context_store.values():
            relevance_score = self._calculate_relevance(item, query)
            if relevance_score > 0.1:  # حد الأدنى للصلة
                relevant_items.append((item, relevance_score))
        
        # ترتيب حسب الصلة والأولوية
        relevant_items.sort(key=lambda x: (x[1], x[0].priority.value), reverse=True)
        
        return [item for item, score in relevant_items[:limit]]

    def _calculate_relevance(self, context_item: ContextItem, query: str) -> float:
        """حساب درجة صلة السياق بالاستعلام"""
        relevance_score = 0.0
        
        # البحث في محتوى السياق
        content_text = str(context_item.content).lower()
        query_lower = query.lower()
        
        # مطابقة الكلمات الرئيسية
        query_words = set(query_lower.split())
        content_words = set(content_text.split())
        
        common_words = query_words.intersection(content_words)
        if common_words:
            relevance_score += len(common_words) * 0.2
        
        # تعزيز بناءً على نوع السياق
        type_boost = {
            ContextType.CONVERSATION: 0.3,
            ContextType.USER_PREFERENCE: 0.4,
            ContextType.DOMAIN_KNOWLEDGE: 0.5,
            ContextType.TEMPORAL: 0.1,
            ContextType.TECHNICAL: 0.6
        }
        
        relevance_score += type_boost.get(context_item.type, 0.0)
        
        # تعزيز بناءً على الأولوية
        priority_boost = {
            PriorityLevel.CRITICAL: 0.5,
            PriorityLevel.HIGH: 0.3,
            PriorityLevel.MEDIUM: 0.1,
            PriorityLevel.LOW: 0.0
        }
        
        relevance_score += priority_boost.get(context_item.priority, 0.0)
        
        return min(relevance_score, 1.0)

    def get_conversation_context(self, lookback_turns: int = 5) -> Dict[str, Any]:
        """الحصول على سياق المحادثة الحديث"""
        recent_turns = self.conversation_history[-lookback_turns:] if self.conversation_history else []
        
        return {
            "recent_conversation": recent_turns,
            "total_turns": len(self.conversation_history),
            "current_topic": self._extract_current_topic(recent_turns),
            "conversation_flow": self._analyze_conversation_flow(recent_turns)
        }

    def _extract_current_topic(self, recent_turns: List[Dict]) -> str:
        """استخراج الموضوع الحالي من المحادثة"""
        if not recent_turns:
            return "عام"
        
        # تحليل آخر 3 أدوار للموضوع
        recent_text = " ".join([turn["user"] for turn in recent_turns[-3:]])
        
        topic_indicators = {
            "برمجة": [r"كود", r"برمجة", r"بايثون", r"جافا", r"html"],
            "تقنية": [r"تقنية", r"تكنولوجيا", r"ذكاء", r"آلة"],
            "تعلم": [r"تعلم", r"دراسة", ر"شرح", ر"فهم"],
            "بحث": [r"بحث", ر"معلومات", ر"ما هو", ر"شرح"],
            "مشروع": [r"مشروع", ر"تطبيق", ر"موقع", ر"برنامج"]
        }
        
        for topic, patterns in topic_indicators.items():
            for pattern in patterns:
                if re.search(pattern, recent_text.lower()):
                    return topic
        
        return "عام"

    def _analyze_conversation_flow(self, recent_turns: List[Dict]) -> str:
        """تحليل تدفق المحادثة"""
        if len(recent_turns) < 2:
            return "بداية المحادثة"
        
        last_user_turn = recent_turns[-1]["user"].lower() if recent_turns else ""
        
        if any(word in last_user_turn for word in ["شكر", "ممتاز", "رائع"]):
            return "نهاية محتملة"
        elif any(word in last_user_turn for word in ["لماذا", "كيف", "شرح"]):
            return "استفسار متعمق"
        elif any(word in last_user_turn for word in ["مثال", "عملي", "تطبيق"]):
            return "طلب أمثلة"
        else:
            return "استمرار المحادثة"

    def update_user_preference(self, key: str, value: Any, priority: PriorityLevel = PriorityLevel.MEDIUM):
        """تحديث تفضيلات المستخدم"""
        self.user_profile[key] = value
        
        # حفظ كسياق أيضاً
        self.add_context_item(
            ContextType.USER_PREFERENCE,
            {"preference_key": key, "preference_value": value},
            priority,
            ttl=86400  # انتهاء بعد يوم
        )
        
        logger.debug(f"🎯 تم تحديث تفضيل المستخدم: {key} = {value}")

    def update_domain_context(self, domain: str, context_data: Dict[str, Any]):
        """تحديث سياق المجال"""
        self.domain_context[domain] = {
            **self.domain_context.get(domain, {}),
            **context_data,
            "last_updated": time.time()
        }
        
        self.add_context_item(
            ContextType.DOMAIN_KNOWLEDGE,
            {"domain": domain, **context_data},
            PriorityLevel.HIGH,
            ttl=7200  # انتهاء بعد ساعتين
        )

    def get_comprehensive_context(self, query: str) -> Dict[str, Any]:
        """الحصول على سياق شامل للاستعلام"""
        
        relevant_context_items = self.get_relevant_context(query)
        conversation_context = self.get_conversation_context()
        
        comprehensive_context = {
            "query": query,
            "timestamp": time.time(),
            "session_id": self.session_id,
            
            # السياق التخاطبي
            "conversation": conversation_context,
            
            # السياق الشخصي
            "user_profile": self.user_profile,
            
            # سياق المجال
            "domain_context": self._get_relevant_domains(query),
            
            # العناصر السياقية ذات الصلة
            "context_items": [item.to_dict() for item in relevant_context_items],
            
            # التوصيات السياقية
            "suggestions": self._generate_context_suggestions(query, relevant_context_items),
            
            # تحليل النوايا
            "intent_analysis": self._analyze_intent_with_context(query, relevant_context_items)
        }
        
        return comprehensive_context

    def _get_relevant_domains(self, query: str) -> Dict[str, Any]:
        """الحصول على المجالات ذات الصلة بالاستعلام"""
        relevant_domains = {}
        detected_domains = self._detect_domains(query)
        
        for domain in detected_domains:
            if domain in self.domain_context:
                relevant_domains[domain] = self.domain_context[domain]
        
        return relevant_domains

    def _generate_context_suggestions(self, query: str, context_items: List[ContextItem]) -> List[str]:
        """توليد اقتراحات بناءً على السياق"""
        suggestions = []
        
        # اقتراحات بناءً على تاريخ المحادثة
        if len(self.conversation_history) > 3:
            recent_topics = set()
            for turn in self.conversation_history[-4:]:
                topic = self._extract_current_topic([turn])
                if topic != "عام":
                    recent_topics.add(topic)
            
            if len(recent_topics) == 1:
                suggestions.append(f"يبدو أنك مهتم بموضوع {list(recent_topics)[0]}")
        
        # اقتراحات بناءً على التفضيلات
        if "preferred_detail_level" in self.user_profile:
            detail_pref = self.user_profile["preferred_detail_level"]
            if detail_pref == "high_detail":
                suggestions.append("سأقدم إجابة مفصلة كما تفضل")
            elif detail_pref == "low_detail":
                suggestions.append("سأختصر الإجابة كما تفضل")
        
        return suggestions

    def _analyze_intent_with_context(self, query: str, context_items: List[ContextItem]) -> Dict[str, Any]:
        """تحليل النوايا مع مراعاة السياق"""
        intent_analysis = {
            "primary_intent": "information_request",
            "confidence": 0.7,
            "contextual_factors": [],
            "expected_response_type": "detailed_explanation"
        }
        
        # تحليل بناءً على السياق
        for item in context_items:
            if item.type == ContextType.CONVERSATION:
                intent_analysis["contextual_factors"].append("استمرار المحادثة الحالية")
            
            elif item.type == ContextType.USER_PREFERENCE:
                if "preferred_help_type" in item.content:
                    intent_analysis["expected_response_type"] = item.content["preferred_help_type"]
        
        # تحليل النص
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["كود", "برمجة", "اكتب", "انشئ"]):
            intent_analysis["primary_intent"] = "code_generation"
            intent_analysis["confidence"] = 0.9
        
        elif any(word in query_lower for word in ["شرح", "ما هو", "مفهوم"]):
            intent_analysis["primary_intent"] = "explanation"
            intent_analysis["confidence"] = 0.8
        
        elif any(word in query_lower for word in ["كيف", "طريقة", "خطوات"]):
            intent_analysis["primary_intent"] = "procedure"
            intent_analysis["expected_response_type"] = "step_by_step"
        
        return intent_analysis

    def _cleanup_expired_context(self):
        """تنظيف السياق المنتهي الصلاحية"""
        current_time = time.time()
        expired_ids = []
        
        for context_id, item in self.context_store.items():
            if item.is_expired():
                expired_ids.append(context_id)
        
        for context_id in expired_ids:
            del self.context_store[context_id]
        
        if expired_ids:
            logger.debug(f"🧹 تم تنظيف {len(expired_ids)} عنصر سياق منتهي")

    def clear_context(self, context_type: Optional[ContextType] = None):
        """مسح السياق (كلي أو حسب النوع)"""
        if context_type is None:
            # مسح كل السياق
            self.context_store.clear()
            self.conversation_history.clear()
            self.user_profile.clear()
            self.domain_context.clear()
            logger.info("🧹 تم مسح كل السياق")
        else:
            # مسح سياق نوع محدد
            ids_to_remove = [
                context_id for context_id, item in self.context_store.items()
                if item.type == context_type
            ]
            for context_id in ids_to_remove:
                del self.context_store[context_id]
            logger.info(f"🧹 تم مسح سياق النوع: {context_type.value}")

    def get_context_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات السياق"""
        self._cleanup_expired_context()
        
        type_counts = {}
        priority_counts = {}
        
        for item in self.context_store.values():
            type_counts[item.type.value] = type_counts.get(item.type.value, 0) + 1
            priority_counts[item.priority.value] = priority_counts.get(item.priority.value, 0) + 1
        
        return {
            "total_context_items": len(self.context_store),
            "conversation_turns": len(self.conversation_history),
            "user_preferences": len(self.user_profile),
            "active_domains": len(self.domain_context),
            "context_by_type": type_counts,
            "context_by_priority": priority_counts,
            "session_duration": time.time() - (self.conversation_history[0]["timestamp"] if self.conversation_history else time.time())
        }

    def export_context(self) -> Dict[str, Any]:
        """تصدير السياق الحالي"""
        return {
            "session_id": self.session_id,
            "exported_at": time.time(),
            "conversation_history": self.conversation_history,
            "user_profile": self.user_profile,
            "domain_context": self.domain_context,
            "context_items": [item.to_dict() for item in self.context_store.values()],
            "stats": self.get_context_stats()
        }

    def import_context(self, context_data: Dict[str, Any]):
        """استيراد السياق"""
        try:
            self.session_id = context_data.get("session_id", self.session_id)
            self.conversation_history = context_data.get("conversation_history", [])
            self.user_profile = context_data.get("user_profile", {})
            self.domain_context = context_data.get("domain_context", {})
            
            # إعادة بناء عناصر السياق
            self.context_store.clear()
            for item_data in context_data.get("context_items", []):
                try:
                    context_item = ContextItem(
                        id=item_data["id"],
                        type=ContextType(item_data["type"]),
                        content=item_data["content"],
                        priority=PriorityLevel(item_data["priority"]),
                        created_at=item_data["created_at"],
                        expires_at=item_data.get("expires_at"),
                        source=item_data.get("source", "imported"),
                        confidence=item_data.get("confidence", 1.0),
                        metadata=item_data.get("metadata", {})
                    )
                    self.context_store[item_data["id"]] = context_item
                except Exception as e:
                    logger.warning(f"⚠️ خطأ في استيراد عنصر السياق: {e}")
            
            logger.info(f"📥 تم استيراد السياق بنجاح ({len(self.context_store)} عنصر)")
        
        except Exception as e:
            logger.error(f"❌ خطأ في استيراد السياق: {e}")
            raise

# نسخة مبسطة للاستخدام السريع
def create_context_manager(session_id: str = "default") -> ContextManager:
    """دالة مساعدة لإنشاء مدير سياق"""
    return ContextManager(session_id)

# استخدام عالمي
_global_context_manager = None

def get_global_context_manager() -> ContextManager:
    """الحصول على مدير السياق العالمي"""
    global _global_context_manager
    if _global_context_manager is None:
        _global_context_manager = ContextManager("global")
    return _global_context_manager
