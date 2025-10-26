# core/intent_analyzer.py — نظام تحليل النوايا المتقدم والذكي
from __future__ import annotations
import logging
import re
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from collections import defaultdict

# إعداد التسجيل
logger = logging.getLogger(__name__)

class IntentType(Enum):
    """أنواع النوايا المختلفة"""
    INFORMATION_REQUEST = "information_request"
    CODE_GENERATION = "code_generation"
    PROJECT_CREATION = "project_creation"
    ANALYSIS_REQUEST = "analysis_request"
    LEARNING_REQUEST = "learning_request"
    CALCULATION = "calculation"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    RECOMMENDATION = "recommendation"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE_TASK = "creative_task"
    SMALL_TALK = "small_talk"
    ERROR_HANDLING = "error_handling"
    UNKNOWN = "unknown"

class ComplexityLevel(Enum):
    """مستويات التعقيد"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    ADVANCED = "advanced"

class UrgencyLevel(Enum):
    """مستويات الاستعجال"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class IntentAnalysis:
    """نتيجة تحليل النوايا"""
    primary_intent: IntentType
    confidence: float
    secondary_intents: List[Tuple[IntentType, float]]
    complexity: ComplexityLevel
    urgency: UrgencyLevel
    entities: Dict[str, Any]
    context_clues: List[str]
    suggested_actions: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "primary_intent": self.primary_intent.value,
            "confidence": self.confidence,
            "secondary_intents": [(intent.value, conf) for intent, conf in self.secondary_intents],
            "complexity": self.complexity.value,
            "urgency": self.urgency.value,
            "entities": self.entities,
            "context_clues": self.context_clues,
            "suggested_actions": self.suggested_actions,
            "metadata": self.metadata
        }

class AdvancedIntentAnalyzer:
    """محلل النوايا المتقدم - يفهم النوايا العميقة للمستخدم"""
    
    def __init__(self):
        self.pattern_library = self._build_pattern_library()
        self.entity_extractors = self._build_entity_extractors()
        self.context_analyzer = self._build_context_analyzer()
        self.confidence_calculator = self._build_confidence_calculator()
        
        # إحصائيات التحليل
        self.analysis_stats = {
            "total_analyses": 0,
            "high_confidence_analyses": 0,
            "average_confidence": 0.0,
            "intent_distribution": defaultdict(int)
        }
        
        logger.info("🎯 تم تهيئة محلل النوايا المتقدم")

    def _build_pattern_library(self) -> Dict[IntentType, Dict[str, Any]]:
        """بناء مكتبة أنماط النوايا"""
        return {
            IntentType.INFORMATION_REQUEST: {
                "patterns": [
                    r"ما هو", r"ماهو", r"ما هي", r"ماهي", r"كيف", r"لماذا", r"أين", r"متى",
                    r"شرح", r"تعريف", r"مفهوم", r"ما معنى", r"ما رأيك في", r"ما تقول في",
                    r"أخبرني عن", r"أريد معرفة", r"ابحث عن", r"هل تعرف"
                ],
                "weight": 1.0,
                "complexity_indicators": [r"بالتفصيل", r"شرح مفصل", r"كامل", r"شامل"]
            },
            
            IntentType.CODE_GENERATION: {
                "patterns": [
                    r"اكتب كود", r"انشئ كود", r"برمج", r"اصنع كود", r"دالة", r"function",
                    r"سكريبت", r"برنامج", r"كود ل", r"مثال على كود", r"كود جاهز",
                    r"كود (?:بايثون|python|جافا|java|html|css|جافاسكريبت|javascript)",
                    r"برمجة", r"تطوير", r"انشاء برنامج"
                ],
                "weight": 1.2,
                "complexity_indicators": [r"كامل", r"مشروع", r"نظام", r"متكامل", r"معقد"]
            },
            
            IntentType.PROJECT_CREATION: {
                "patterns": [
                    r"ابني مشروع", r"انشئ مشروع", r"اصنع مشروع", r"مشروع ل",
                    r"تطبيق", r"موقع", r"نظام", r"منصة", r"برنامج متكامل",
                    r"ابني لي", r"انشئ لي", r"صمم لي", r"عمل نظام"
                ],
                "weight": 1.3,
                "complexity_indicators": [r"كبير", r"متكامل", r"شامل", r"احترافي"]
            },
            
            IntentType.ANALYSIS_REQUEST: {
                "patterns": [
                    r"حلل", r"حلل لي", r"قيم", r"راجع", r"ما تقييمك", r"ما رأيك في",
                    r"كيف ترى", r"ما تحليلك", r"دراسة", r"تقييم", r"فحص", r"تحليل"
                ],
                "weight": 1.1,
                "complexity_indicators": [r"مفصل", r"شامل", ر"عميق", ر"دقيق"]
            },
            
            IntentType.LEARNING_REQUEST: {
                "patterns": [
                    r"تعلم", r"تعلم من", r"احفظ", r"تذكر", r"أضف إلى ذاكرتك",
                    r"تعلم هذا", r"احفظ المعلومة", r"تعلم وتذكر", r"كن ذكياً"
                ],
                "weight": 0.9,
                "complexity_indicators": [r"دائم", ر"مستمر", ر"دوري"]
            },
            
            IntentType.CALCULATION: {
                "patterns": [
                    r"احسب", r"ما مجموع", r"كم", r"حل", r"معادلة", r"عملية حسابية",
                    r"ناتج", r"حساب", r"ما ناتج", r"ما نتيجة", r"كم يساوي"
                ],
                "weight": 1.0,
                "complexity_indicators": [r"معقد", ر"صعب", ر"متقدم", ر"كبير"]
            },
            
            IntentType.EXPLANATION: {
                "patterns": [
                    r"اشرح", r"وضح", r"فصل", ر"بين", ر"ما الفرق", ر"ما الفروقات",
                    r"كيف يعمل", ر"ما آلية", ر"ما طريقة", ر"ما خطوات"
                ],
                "weight": 1.0,
                "complexity_indicators": [r"مفصل", ر"وافي", ر"شامل", ر"دقيق"]
            },
            
            IntentType.COMPARISON: {
                "patterns": [
                    r"قارن", r"ما الفرق بين", r"ما الفروقات", r"أيهما أفضل",
                    r"مقارنة بين", ر"ما الاختلاف", ر"ما أوجه الشبه"
                ],
                "weight": 1.1,
                "complexity_indicators": [r"شامل", ر"مفصل", ر"دقيق", ر"وافي"]
            },
            
            IntentType.RECOMMENDATION: {
                "patterns": [
                    r"ماذا تنصح", r"ما توصيك", r"ما رأيك في", r"أفضل",
                    r"أنصحني", ر"ما ترشيحك", ر"ما اقتراحك", ر"ما تفضيلك"
                ],
                "weight": 1.0,
                "complexity_indicators": [r"مفصل", ر"شامل", ر"مدروس"]
            },
            
            IntentType.PROBLEM_SOLVING: {
                "patterns": [
                    r"حل المشكلة", r"كيف أحل", r"ما الحل", r"واجهت مشكلة",
                    r"عندي issue", ر"ما troubleshooting", ر"إصلاح", ر"علاج"
                ],
                "weight": 1.2,
                "complexity_indicators": [r"صعب", ر"معقد", ر"مستعصي", ر"كبير"]
            },
            
            IntentType.CREATIVE_TASK: {
                "patterns": [
                    r"اصنع", r"ابتكر", r"أنشئ", ر"صمم", ر"اكتشف", ر"اخترع",
                    r"فكرة", ر"مبتكر", ر"إبداعي", ر"جديد", ر"مختلف"
                ],
                "weight": 1.3,
                "complexity_indicators": [r"كبير", ر"معقد", ر"مبتكر", ر"فريد"]
            },
            
            IntentType.SMALL_TALK: {
                "patterns": [
                    r"مرحبا", r"اهلا", r"كيف حالك", r"من انت", r"شكرا", r"مساء الخير",
                    r"صباح الخير", ر"السلام عليكم", ر"وعليكم السلام", ر"حياك الله"
                ],
                "weight": 0.5,
                "complexity_indicators": []
            },
            
            IntentType.ERROR_HANDLING: {
                "patterns": [
                    r"خطأ", r"error", r"مشكلة", r"لا يعمل", ر"لماذا لا", ر"ما الخلل",
                    r"تصحيح", ر"إصلاح", ر"debug", ر"fix", ر"solve"
                ],
                "weight": 1.2,
                "complexity_indicators": [r"صعب", ر"معقد", ر"مستعصي"]
            }
        }

    def _build_entity_extractors(self) -> Dict[str, Any]:
        """بناء مستخرجي الكيانات"""
        return {
            "programming_languages": {
                "patterns": [
                    r"بايثون", r"python", r"جافا", r"java", r"جافاسكريبت", r"javascript",
                    r"html", r"css", r"sql", r"بي إتش بي", r"php", r"روبي", r"ruby",
                    r"سويفت", r"swift", r"كوتلن", r"kotlin", r"سي بلس بلس", r"c\+\+",
                    r"سي شارب", r"c#", r"غو", r"go", r"روست", r"rust"
                ],
                "type": "technology"
            },
            
            "technologies": {
                "patterns": [
                    r"react", r"vue", r"angular", r"node", r"django", r"flask",
                    r"spring", r"laravel", r"express", r"fastapi", r"sqlite",
                    r"mysql", r"postgresql", r"mongodb", r"redis", r"docker"
                ],
                "type": "technology"
            },
            
            "domains": {
                "patterns": [
                    r"ويب", r"web", r"موبايل", r"mobile", r"سطح مكتب", r"desktop",
                    r"ذكاء اصطناعي", r"ai", r"تعلم آلة", r"machine learning",
                    r"بيانات", r"data", r"أمن", r"security", r"سحابي", r"cloud"
                ],
                "type": "domain"
            },
            
            "complexity_indicators": {
                "patterns": [
                    r"بسيط", r"سهل", r"مبدئي", r"أولي", r"مبتدئ",
                    r"متوسط", r"عادي", r"معتاد", r"معتدل",
                    r"معقد", r"صعب", r"متقدم", r"محترف", r"خبير",
                    r"شامل", r"كامل", r"مفصل", r"وافي", r"دقيق"
                ],
                "type": "complexity"
            },
            
            "urgency_indicators": {
                "patterns": [
                    r"عاجل", r"فوري", r"الآن", r"بسرعة", r"مستعجل",
                    r"عادي", r"وقت", r"لاحق", r"مستقبل",
                    r"مهم", r"ضروري", r"حيوي", ر"حاسم"
                ],
                "type": "urgency"
            }
        }

    def _build_context_analyzer(self) -> Dict[str, Any]:
        """بناء محلل السياق"""
        return {
            "context_clues": {
                "detail_level": [r"بالتفصيل", r"باختصار", r"ملخص", r"مفصل", r"سريع"],
                "preference": [r"أفضل", r"مفضل", r"أحب", r"أريد", r"أتمنى"],
                "constraint": [r"شرط", r"بشرط", r"شريطة", r"باستثناء", r"بدون"],
                "example_request": [r"مثال", r"مثلاً", r"على سبيل المثال", r"توضيح"]
            },
            "sentiment_indicators": {
                "positive": [r"شكراً", r"ممتاز", ر"رائع", ر"جميل", ر"أحسنت"],
                "negative": [r"خطأ", ر"غلط", ر"سيء", ر"لا يعمل", ر"مشكلة"],
                "confused": [r"لم أفهم", ر"ماذا", ر"كيف", ر"لماذا", ر"أين"]
            }
        }

    def _build_confidence_calculator(self) -> Dict[str, Any]:
        """بناء حاسبة الثقة"""
        return {
            "factors": {
                "pattern_match_strength": 0.3,
                "entity_presence": 0.2,
                "context_support": 0.15,
                "complexity_alignment": 0.15,
                "historical_patterns": 0.1,
                "query_structure": 0.1
            },
            "thresholds": {
                "high_confidence": 0.8,
                "medium_confidence": 0.6,
                "low_confidence": 0.4
            }
        }

    def analyze_intent(self, text: str, context: Dict[str, Any] = None) -> IntentAnalysis:
        """تحليل النوايا الرئيسي"""
        if context is None:
            context = {}
        
        # تنظيف النص
        cleaned_text = self._clean_text(text)
        
        # استخراج الكيانات
        entities = self._extract_entities(cleaned_text)
        
        # تحليل الأنماط
        intent_scores = self._calculate_intent_scores(cleaned_text, entities, context)
        
        # تحديد النوايا الأساسية والثانوية
        primary_intent, confidence = self._select_primary_intent(intent_scores)
        secondary_intents = self._select_secondary_intents(intent_scores, primary_intent)
        
        # تحليل التعقيد والاستعجال
        complexity = self._analyze_complexity(cleaned_text, entities, primary_intent)
        urgency = self._analyze_urgency(cleaned_text, entities)
        
        # استخراج أدلة السياق
        context_clues = self._extract_context_clues(cleaned_text)
        
        # توليد الإجراءات المقترحة
        suggested_actions = self._generate_suggested_actions(primary_intent, entities, complexity)
        
        # تحديث الإحصائيات
        self._update_analysis_stats(primary_intent, confidence)
        
        # إنشاء نتيجة التحليل
        analysis = IntentAnalysis(
            primary_intent=primary_intent,
            confidence=confidence,
            secondary_intents=secondary_intents,
            complexity=complexity,
            urgency=urgency,
            entities=entities,
            context_clues=context_clues,
            suggested_actions=suggested_actions,
            metadata={
                "text_length": len(text),
                "word_count": len(text.split()),
                "analysis_timestamp": time.time(),
                "cleaned_text": cleaned_text
            }
        )
        
        logger.info(f"🎯 تحليل النوايا: {primary_intent.value} (ثقة: {confidence:.2f})")
        return analysis

    def _clean_text(self, text: str) -> str:
        """تنظيف النص المدخل"""
        if not text:
            return ""
        
        # تحويل إلى lowercase
        text = text.lower()
        
        # إزالة علامات الترقيم الزائدة
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # إزالة المسافات الزائدة
        text = ' '.join(text.split())
        
        # استبدال الحروف المتباينة
        replacements = {
            "أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """استخراج الكيانات من النص"""
        entities = {
            "programming_languages": [],
            "technologies": [],
            "domains": [],
            "complexity_levels": [],
            "urgency_levels": [],
            "other_entities": []
        }
        
        for entity_type, config in self.entity_extractors.items():
            patterns = config["patterns"]
            entity_list = entities.get(entity_type, [])
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                entity_list.extend(matches)
            
            # إزالة التكرارات
            entities[entity_type] = list(set(entity_list))
        
        return entities

    def _calculate_intent_scores(self, text: str, entities: Dict[str, Any], context: Dict[str, Any]) -> Dict[IntentType, float]:
        """حساب درجات النوايا"""
        intent_scores = {}
        
        for intent_type, config in self.pattern_library.items():
            base_score = 0.0
            
            # مطابقة الأنماط
            pattern_score = self._calculate_pattern_score(text, config["patterns"])
            base_score += pattern_score * config["weight"]
            
            # دعم الكيانات
            entity_score = self._calculate_entity_score(intent_type, entities)
            base_score += entity_score * 0.2
            
            # دعم السياق
            context_score = self._calculate_context_score(intent_type, context)
            base_score += context_score * 0.15
            
            # محاذاة التعقيد
            complexity_score = self._calculate_complexity_alignment(text, intent_type)
            base_score += complexity_score * 0.15
            
            intent_scores[intent_type] = min(base_score, 1.0)
        
        return intent_scores

    def _calculate_pattern_score(self, text: str, patterns: List[str]) -> float:
        """حساب درجة مطابقة الأنماط"""
        if not text:
            return 0.0
        
        total_matches = 0
        for pattern in patterns:
            if re.search(pattern, text):
                total_matches += 1
        
        # تطبيع الدرجة
        max_possible_matches = len(patterns)
        if max_possible_matches == 0:
            return 0.0
        
        return min(total_matches / max_possible_matches, 1.0)

    def _calculate_entity_score(self, intent_type: IntentType, entities: Dict[str, Any]) -> float:
        """حساب درجة دعم الكيانات"""
        entity_support_map = {
            IntentType.CODE_GENERATION: ["programming_languages", "technologies"],
            IntentType.PROJECT_CREATION: ["programming_languages", "technologies", "domains"],
            IntentType.TECHNICAL_QUESTION: ["programming_languages", "technologies"],
            IntentType.ANALYSIS_REQUEST: ["domains"]
        }
        
        supported_entities = entity_support_map.get(intent_type, [])
        if not supported_entities:
            return 0.5  # درجة محايدة
        
        total_entities = 0
        matching_entities = 0
        
        for entity_type in supported_entities:
            entity_list = entities.get(entity_type, [])
            total_entities += len(entity_list)
            if entity_list:
                matching_entities += 1
        
        if total_entities == 0:
            return 0.3  # درجة منخفضة عند عدم وجود كيانات
        
        return matching_entities / len(supported_entities)

    def _calculate_context_score(self, intent_type: IntentType, context: Dict[str, Any]) -> float:
        """حساب درجة دعم السياق"""
        if not context:
            return 0.5
        
        # تحليل تاريخ المحادثة
        conversation_history = context.get("conversation_history", [])
        if not conversation_history:
            return 0.5
        
        # البحث عن نوايا سابقة مشابهة
        recent_intents = []
        for turn in conversation_history[-3:]:  # آخر 3 أدوار
            user_msg = turn.get("user", "")
            if user_msg:
                # تحليل سريع للنوايا السابقة
                quick_analysis = self._quick_analyze(user_msg)
                recent_intents.append(quick_analysis)
        
        # حساب التوافق مع النوايا السابقة
        if recent_intents:
            similarity_count = sum(1 for intent in recent_intents if intent == intent_type)
            return similarity_count / len(recent_intents)
        
        return 0.5

    def _calculate_complexity_alignment(self, text: str, intent_type: IntentType) -> float:
        """حساب محاذاة التعقيد"""
        complexity_words = [
            "بسيط", "سهل", "مبدئي", "مبتدئ",
            "متوسط", "عادي", "معتدل", 
            "معقد", "صعب", "متقدم", "محترف"
        ]
        
        text_lower = text.lower()
        complexity_matches = sum(1 for word in complexity_words if word in text_lower)
        
        # بعض النوايا تتطلب تعقيداً أعلى بشكل طبيعي
        high_complexity_intents = [
            IntentType.PROJECT_CREATION,
            IntentType.CODE_GENERATION,
            IntentType.PROBLEM_SOLVING
        ]
        
        if intent_type in high_complexity_intents:
            return min(complexity_matches * 0.3, 1.0)
        else:
            return 0.5  # درجة محايدة

    def _quick_analyze(self, text: str) -> IntentType:
        """تحليل سريع للنوايا (للاستخدام في السياق)"""
        cleaned_text = self._clean_text(text)
        
        for intent_type, config in self.pattern_library.items():
            for pattern in config["patterns"]:
                if re.search(pattern, cleaned_text):
                    return intent_type
        
        return IntentType.UNKNOWN

    def _select_primary_intent(self, intent_scores: Dict[IntentType, float]) -> Tuple[IntentType, float]:
        """اختيار النية الأساسية"""
        if not intent_scores:
            return IntentType.UNKNOWN, 0.0
        
        primary_intent, max_score = max(intent_scores.items(), key=lambda x: x[1])
        
        # إذا كانت الدرجة منخفضة جداً، نعتبرها unknown
        if max_score < 0.3:
            return IntentType.UNKNOWN, max_score
        
        return primary_intent, max_score

    def _select_secondary_intents(self, intent_scores: Dict[IntentType, float], primary_intent: IntentType) -> List[Tuple[IntentType, float]]:
        """اختيار النوايا الثانوية"""
        secondary_intents = []
        
        for intent_type, score in intent_scores.items():
            if intent_type != primary_intent and score > 0.3:
                secondary_intents.append((intent_type, score))
        
        # ترتيب حسب الدرجة
        secondary_intents.sort(key=lambda x: x[1], reverse=True)
        
        return secondary_intents[:3]  # أعلى 3 نوايا ثانوية

    def _analyze_complexity(self, text: str, entities: Dict[str, Any], primary_intent: IntentType) -> ComplexityLevel:
        """تحليل مستوى التعقيد"""
        complexity_indicators = {
            ComplexityLevel.SIMPLE: [r"بسيط", r"سهل", r"مبدئي", r"أولي", r"مبتدئ"],
            ComplexityLevel.MEDIUM: [r"متوسط", r"عادي", r"معتاد", r"معتدل"],
            ComplexityLevel.COMPLEX: [r"معقد", r"صعب", r"متقدم", r"محترف"],
            ComplexityLevel.ADVANCED: [r"شامل", r"كامل", r"مفصل", r"وافي", r"دقيق"]
        }
        
        text_lower = text.lower()
        complexity_scores = {}
        
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if re.search(indicator, text_lower))
            complexity_scores[level] = score
        
        # بعض النوايا تعتبر معقدة بشكل افتراضي
        inherently_complex_intents = [
            IntentType.PROJECT_CREATION,
            IntentType.PROBLEM_SOLVING,
            IntentType.CREATIVE_TASK
        ]
        
        if primary_intent in inherently_complex_intents:
            complexity_scores[ComplexityLevel.COMPLEX] += 2
        
        # اختيار مستوى التعقيد
        max_level = max(complexity_scores.items(), key=lambda x: x[1])
        
        if max_level[1] == 0:
            # إذا لم توجد مؤشرات، نستخدم المستوى المتوسط
            return ComplexityLevel.MEDIUM
        
        return max_level[0]

    def _analyze_urgency(self, text: str, entities: Dict[str, Any]) -> UrgencyLevel:
        """تحليل مستوى الاستعجال"""
        urgency_indicators = {
            UrgencyLevel.LOW: [r"لاحق", r"مستقبل", r"ليس عاجل", r"في وقت"],
            UrgencyLevel.NORMAL: [],  # الحالة الافتراضية
            UrgencyLevel.HIGH: [r"مهم", r"ضروري", r"حيوي", r"حاسم"],
            UrgencyLevel.URGENT: [r"عاجل", r"فوري", r"الآن", r"بسرعة", r"مستعجل"]
        }
        
        text_lower = text.lower()
        
        for level, indicators in urgency_indicators.items():
            for indicator in indicators:
                if re.search(indicator, text_lower):
                    return level
        
        return UrgencyLevel.NORMAL

    def _extract_context_clues(self, text: str) -> List[str]:
        """استخراج أدلة السياق"""
        context_clues = []
        
        for clue_type, patterns in self.context_analyzer["context_clues"].items():
            for pattern in patterns:
                if re.search(pattern, text):
                    context_clues.append(f"{clue_type}: {pattern}")
                    break
        
        for sentiment, patterns in self.context_analyzer["sentiment_indicators"].items():
            for pattern in patterns:
                if re.search(pattern, text):
                    context_clues.append(f"sentiment: {sentiment}")
                    break
        
        return context_clues

    def _generate_suggested_actions(self, primary_intent: IntentType, entities: Dict[str, Any], complexity: ComplexityLevel) -> List[str]:
        """توليد الإجراءات المقترحة"""
        actions = []
        
        action_templates = {
            IntentType.INFORMATION_REQUEST: [
                "البحث في قاعدة المعرفة",
                "الاستعلام من مصادر الويب",
                "التحقق من الذاكرة الداخلية",
                "توفير إجابة شاملة"
            ],
            IntentType.CODE_GENERATION: [
                "توليد الكود المطلوب",
                "توفير شرح للكود",
                "إضافة تعليقات توضيحية",
                "اختبار الكود generated"
            ],
            IntentType.PROJECT_CREATION: [
                "تحليل المتطلبات",
                "تصميم هيكل المشروع",
                "إنشاء ملفات المشروع",
                "توفير إرشادات التنفيذ"
            ],
            IntentType.ANALYSIS_REQUEST: [
                "تحليل متعمق للموضوع",
                "توفير إحصائيات وبيانات",
                "عرض النتائج بطريقة منظمة",
                "تقديم توصيات عملية"
            ]
        }
        
        # إجراءات عامة
        general_actions = [
            "التحقق من صحة المعلومات",
            "توفير أمثلة عملية",
            "مراعاة مستوى التعقيد المطلوب",
            "الاستعداد للأسئلة المتابعة"
        ]
        
        # إضافة إجراءات محددة للنية
        actions.extend(action_templates.get(primary_intent, []))
        
        # إضافة إجراءات عامة
        actions.extend(general_actions)
        
        # تعديل الإجراءات بناءً على التعقيد
        if complexity == ComplexityLevel.COMPLEX:
            actions.append("توفير تحليل متعمق وشامل")
        elif complexity == ComplexityLevel.SIMPLE:
            actions.append("التركيز على الإيجاز والوضوح")
        
        return actions

    def _update_analysis_stats(self, primary_intent: IntentType, confidence: float):
        """تحديث إحصائيات التحليل"""
        self.analysis_stats["total_analyses"] += 1
        self.analysis_stats["intent_distribution"][primary_intent.value] += 1
        
        if confidence >= self.confidence_calculator["thresholds"]["high_confidence"]:
            self.analysis_stats["high_confidence_analyses"] += 1
        
        # تحديث متوسط الثقة
        total = self.analysis_stats["total_analyses"]
        current_avg = self.analysis_stats["average_confidence"]
        self.analysis_stats["average_confidence"] = (
            (current_avg * (total - 1) + confidence) / total
        )

    def get_analysis_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات التحليل"""
        return {
            **self.analysis_stats,
            "confidence_thresholds": self.confidence_calculator["thresholds"],
            "total_intent_types": len(IntentType)
        }

    def optimize_patterns(self, feedback_data: List[Tuple[str, IntentType, bool]]):
        """تحسين الأنماط بناءً على التغذية الراجعة"""
        successful_matches = 0
        total_feedback = len(feedback_data)
        
        for text, expected_intent, was_correct in feedback_data:
            if was_correct:
                successful_matches += 1
        
        accuracy = successful_matches / total_feedback if total_feedback > 0 else 0.0
        
        logger.info(f"📊 دقة تحليل النوايا: {accuracy:.2f} ({successful_matches}/{total_feedback})")
        
        # إذا كانت الدقة منخفضة، يمكن إضافة تحسينات إضافية هنا
        if accuracy < 0.7:
            logger.warning("⚠️ دقة تحليل النوايا منخفضة - يوصى بمراجعة الأنماط")

# استخدام عالمي
_global_intent_analyzer = None

def get_global_intent_analyzer() -> AdvancedIntentAnalyzer:
    """الحصول على محلل النوايا العالمي"""
    global _global_intent_analyzer
    if _global_intent_analyzer is None:
        _global_intent_analyzer = AdvancedIntentAnalyzer()
    return _global_intent_analyzer

# دالة مساعدة للاستخدام السريع
def quick_intent_analysis(text: str) -> Dict[str, Any]:
    """تحليل سريع للنوايا"""
    analyzer = get_global_intent_analyzer()
    analysis = analyzer.analyze_intent(text)
    return analysis.to_dict()
