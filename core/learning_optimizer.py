# core/learning_optimizer.py — نظام تحسين التعلم الذاتي المتقدم
from __future__ import annotations
import logging
import json
import time
import sqlite3
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re
import numpy as np
from collections import defaultdict, deque

# إعداد التسجيل
logger = logging.getLogger(__name__)

class LearningStrategy(Enum):
    """استراتيجيات التعلم المختلفة"""
    ACTIVE_LEARNING = "active_learning"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    TRANSFER_LEARNING = "transfer_learning"
    META_LEARNING = "meta_learning"
    CONTEXT_AWARE_LEARNING = "context_aware_learning"

class KnowledgeDomain(Enum):
    """مجالات المعرفة المختلفة"""
    PROGRAMMING = "programming"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    BUSINESS = "business"
    HEALTH = "health"
    EDUCATION = "education"
    GENERAL = "general"

@dataclass
class LearningMetrics:
    """مقاييس أداء التعلم"""
    accuracy: float = 0.0
    relevance: float = 0.0
    completeness: float = 0.0
    response_time: float = 0.0
    user_satisfaction: float = 0.0
    knowledge_retention: float = 0.0
    
    def overall_score(self) -> float:
        """حساب النتيجة الإجمالية"""
        weights = {
            'accuracy': 0.25,
            'relevance': 0.20,
            'completeness': 0.15,
            'response_time': 0.15,
            'user_satisfaction': 0.15,
            'knowledge_retention': 0.10
        }
        
        return sum(
            getattr(self, metric) * weight 
            for metric, weight in weights.items()
        )

@dataclass
class LearningSession:
    """جلسة تعلم فردية"""
    session_id: str
    domain: KnowledgeDomain
    strategy: LearningStrategy
    start_time: float
    end_time: Optional[float] = None
    metrics: LearningMetrics = None
    topics_covered: List[str] = None
    knowledge_gained: int = 0
    confidence_boost: float = 0.0
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = LearningMetrics()
        if self.topics_covered is None:
            self.topics_covered = []
    
    def duration(self) -> float:
        """مدة الجلسة"""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "session_id": self.session_id,
            "domain": self.domain.value,
            "strategy": self.strategy.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metrics": {
                "accuracy": self.metrics.accuracy,
                "relevance": self.metrics.relevance,
                "completeness": self.metrics.completeness,
                "response_time": self.metrics.response_time,
                "user_satisfaction": self.metrics.user_satisfaction,
                "knowledge_retention": self.metrics.knowledge_retention,
                "overall_score": self.metrics.overall_score()
            },
            "topics_covered": self.topics_covered,
            "knowledge_gained": self.knowledge_gained,
            "confidence_boost": self.confidence_boost,
            "duration": self.duration()
        }

class LearningOptimizer:
    """محسن التعلم المتقدم - يحسن أداء النظام باستمرار"""
    
    def __init__(self, db_path: str = "learning_optimizer.db"):
        self.db_path = db_path
        self.learning_sessions: Dict[str, LearningSession] = {}
        self.performance_history: deque = deque(maxlen=1000)
        self.knowledge_domains: Dict[KnowledgeDomain, Dict] = {}
        self.learning_strategies: Dict[LearningStrategy, Dict] = {}
        
        # إحصائيات التعلم
        self.learning_stats = {
            "total_sessions": 0,
            "successful_learnings": 0,
            "failed_learnings": 0,
            "total_knowledge_gained": 0,
            "average_confidence": 0.0,
            "domains_covered": set()
        }
        
        # إعداد استراتيجيات التعلم
        self._initialize_strategies()
        self._initialize_domains()
        self._setup_database()
        
        logger.info("🧠 تم تهيئة محسن التعلم المتقدم")

    def _initialize_strategies(self):
        """تهيئة استراتيجيات التعلم"""
        self.learning_strategies = {
            LearningStrategy.ACTIVE_LEARNING: {
                "description": "تعلم نشط من التفاعلات المباشرة",
                "efficiency": 0.8,
                "speed": 0.7,
                "retention": 0.9,
                "applicable_domains": [KnowledgeDomain.PROGRAMMING, KnowledgeDomain.TECHNOLOGY]
            },
            LearningStrategy.REINFORCEMENT_LEARNING: {
                "description": "تعلم من المكافآت والعقوبات",
                "efficiency": 0.9,
                "speed": 0.6,
                "retention": 0.8,
                "applicable_domains": [KnowledgeDomain.GENERAL, KnowledgeDomain.BUSINESS]
            },
            LearningStrategy.TRANSFER_LEARNING: {
                "description": "نقل المعرفة بين المجالات",
                "efficiency": 0.7,
                "speed": 0.8,
                "retention": 0.7,
                "applicable_domains": [KnowledgeDomain.SCIENCE, KnowledgeDomain.EDUCATION]
            },
            LearningStrategy.META_LEARNING: {
                "description": "تعلم كيفية التعلم",
                "efficiency": 0.95,
                "speed": 0.5,
                "retention": 0.95,
                "applicable_domains": [KnowledgeDomain.GENERAL]
            },
            LearningStrategy.CONTEXT_AWARE_LEARNING: {
                "description": "تعلم مراعٍ للسياق",
                "efficiency": 0.85,
                "speed": 0.75,
                "retention": 0.85,
                "applicable_domains": [KnowledgeDomain.PROGRAMMING, KnowledgeDomain.TECHNOLOGY, KnowledgeDomain.GENERAL]
            }
        }

    def _initialize_domains(self):
        """تهيئة مجالات المعرفة"""
        self.knowledge_domains = {
            KnowledgeDomain.PROGRAMMING: {
                "description": "البرمجة وتطوير البرمجيات",
                "learning_difficulty": 0.7,
                "knowledge_density": 0.9,
                "update_frequency": 0.8,
                "priority": 0.9
            },
            KnowledgeDomain.TECHNOLOGY: {
                "description": "التقنيات الحديثة والذكاء الاصطناعي",
                "learning_difficulty": 0.6,
                "knowledge_density": 0.8,
                "update_frequency": 0.9,
                "priority": 0.8
            },
            KnowledgeDomain.SCIENCE: {
                "description": "العلوم والمعرفة العلمية",
                "learning_difficulty": 0.5,
                "knowledge_density": 0.7,
                "update_frequency": 0.4,
                "priority": 0.7
            },
            KnowledgeDomain.BUSINESS: {
                "description": "الأعمال والاقتصاد",
                "learning_difficulty": 0.4,
                "knowledge_density": 0.6,
                "update_frequency": 0.6,
                "priority": 0.6
            },
            KnowledgeDomain.HEALTH: {
                "description": "الصحة والطب",
                "learning_difficulty": 0.8,
                "knowledge_density": 0.8,
                "update_frequency": 0.7,
                "priority": 0.8
            },
            KnowledgeDomain.EDUCATION: {
                "description": "التعليم والتربية",
                "learning_difficulty": 0.3,
                "knowledge_density": 0.5,
                "update_frequency": 0.5,
                "priority": 0.5
            },
            KnowledgeDomain.GENERAL: {
                "description": "المعرفة العامة",
                "learning_difficulty": 0.2,
                "knowledge_density": 0.4,
                "update_frequency": 0.3,
                "priority": 0.4
            }
        }

    def _setup_database(self):
        """إعداد قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # جدول جلسات التعلم
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    session_id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    metrics_json TEXT NOT NULL,
                    topics_covered_json TEXT NOT NULL,
                    knowledge_gained INTEGER DEFAULT 0,
                    confidence_boost REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول أداء الاستراتيجيات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_performance (
                    strategy TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    efficiency REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    last_used REAL,
                    PRIMARY KEY (strategy, domain)
                )
            ''')
            
            # جدول تقدم التعلم
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_progress (
                    domain TEXT PRIMARY KEY,
                    knowledge_level REAL DEFAULT 0.0,
                    confidence_level REAL DEFAULT 0.0,
                    last_updated REAL,
                    sessions_count INTEGER DEFAULT 0,
                    total_knowledge_gained INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ تم إعداد قاعدة بيانات التعلم بنجاح")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إعداد قاعدة البيانات: {e}")

    def start_learning_session(self, domain: KnowledgeDomain, 
                             strategy: Optional[LearningStrategy] = None) -> str:
        """بدء جلسة تعلم جديدة"""
        if strategy is None:
            strategy = self._select_optimal_strategy(domain)
        
        session_id = f"session_{domain.value}_{int(time.time() * 1000)}"
        
        session = LearningSession(
            session_id=session_id,
            domain=domain,
            strategy=strategy,
            start_time=time.time()
        )
        
        self.learning_sessions[session_id] = session
        self.learning_stats["total_sessions"] += 1
        self.learning_stats["domains_covered"].add(domain)
        
        logger.info(f"🎯 بدء جلسة تعلم: {domain.value} باستراتيجية {strategy.value}")
        return session_id

    def _select_optimal_strategy(self, domain: KnowledgeDomain) -> LearningStrategy:
        """اختيار أفضل استراتيجية تعلم للمجال"""
        # تحليل أداء الاستراتيجيات السابقة
        strategy_scores = {}
        
        for strategy, config in self.learning_strategies.items():
            if domain in config["applicable_domains"]:
                # حساب النتيجة بناءً على الكفاءة والسرعة والاحتفاظ
                base_score = (
                    config["efficiency"] * 0.4 +
                    config["speed"] * 0.3 +
                    config["retention"] * 0.3
                )
                
                # تعديل بناءً على الأداء التاريخي
                historical_performance = self._get_strategy_performance(strategy, domain)
                adjusted_score = base_score * (1 + historical_performance * 0.2)
                
                strategy_scores[strategy] = adjusted_score
        
        if not strategy_scores:
            # استراتيجية افتراضية إذا لم توجد مناسبة
            return LearningStrategy.ACTIVE_LEARNING
        
        return max(strategy_scores.items(), key=lambda x: x[1])[0]

    def _get_strategy_performance(self, strategy: LearningStrategy, domain: KnowledgeDomain) -> float:
        """الحصول على الأداء التاريخي للاستراتيجية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT success_rate FROM strategy_performance WHERE strategy = ? AND domain = ?",
                (strategy.value, domain.value)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else 0.5  # قيمة افتراضية
            
        except Exception as e:
            logger.error(f"❌ خطأ في جلب أداء الاستراتيجية: {e}")
            return 0.5

    def update_learning_metrics(self, session_id: str, metrics: LearningMetrics):
        """تحديث مقاييس التعلم للجلسة"""
        if session_id not in self.learning_sessions:
            logger.warning(f"⚠️ جلسة التعلم غير موجودة: {session_id}")
            return
        
        session = self.learning_sessions[session_id]
        session.metrics = metrics
        
        # تحديث الإحصائيات
        overall_score = metrics.overall_score()
        if overall_score > 0.7:
            self.learning_stats["successful_learnings"] += 1
        else:
            self.learning_stats["failed_learnings"] += 1
        
        # تحديث متوسط الثقة
        total_sessions = self.learning_stats["successful_learnings"] + self.learning_stats["failed_learnings"]
        if total_sessions > 0:
            self.learning_stats["average_confidence"] = (
                (self.learning_stats["average_confidence"] * (total_sessions - 1) + metrics.user_satisfaction) 
                / total_sessions
            )
        
        logger.debug(f"📊 تم تحديث مقاييس التعلم للجلسة {session_id}: {overall_score:.2f}")

    def end_learning_session(self, session_id: str, knowledge_gained: int = 0, 
                           confidence_boost: float = 0.0):
        """إنهاء جلسة التعلم وحفظ النتائج"""
        if session_id not in self.learning_sessions:
            logger.warning(f"⚠️ جلسة التعلم غير موجودة: {session_id}")
            return
        
        session = self.learning_sessions[session_id]
        session.end_time = time.time()
        session.knowledge_gained = knowledge_gained
        session.confidence_boost = confidence_boost
        
        # تحديث الإحصائيات
        self.learning_stats["total_knowledge_gained"] += knowledge_gained
        
        # حفظ في قاعدة البيانات
        self._save_session_to_db(session)
        
        # تحديث أداء الاستراتيجية
        self._update_strategy_performance(session)
        
        # تحديث تقدم التعلم
        self._update_learning_progress(session)
        
        logger.info(f"✅ تم إنهاء جلسة التعلم: {session_id} (المعرفة المكتسبة: {knowledge_gained})")

    def _save_session_to_db(self, session: LearningSession):
        """حفظ جلسة التعلم في قاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_sessions 
                (session_id, domain, strategy, start_time, end_time, metrics_json, 
                 topics_covered_json, knowledge_gained, confidence_boost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                session.domain.value,
                session.strategy.value,
                session.start_time,
                session.end_time,
                json.dumps(session.metrics.to_dict() if hasattr(session.metrics, 'to_dict') else session.metrics.__dict__),
                json.dumps(session.topics_covered),
                session.knowledge_gained,
                session.confidence_boost
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ جلسة التعلم: {e}")

    def _update_strategy_performance(self, session: LearningSession):
        """تحديث أداء الاستراتيجية"""
        try:
            success_rate = session.metrics.overall_score()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO strategy_performance 
                (strategy, domain, success_rate, efficiency, usage_count, last_used)
                VALUES (?, ?, ?, ?, 1, ?)
                ON CONFLICT(strategy, domain) DO UPDATE SET
                success_rate = (success_rate + ?) / 2,
                efficiency = (efficiency + ?) / 2,
                usage_count = usage_count + 1,
                last_used = ?
            ''', (
                session.strategy.value,
                session.domain.value,
                success_rate,
                session.metrics.accuracy,
                session.end_time,
                success_rate,
                session.metrics.accuracy,
                session.end_time
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث أداء الاستراتيجية: {e}")

    def _update_learning_progress(self, session: LearningSession):
        """تحديث تقدم التعلم"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # حساب مستوى المعرفة الجديد
            knowledge_increase = session.knowledge_gained / 1000  # تطبيع
            confidence_increase = session.confidence_boost
            
            cursor.execute('''
                INSERT INTO learning_progress 
                (domain, knowledge_level, confidence_level, last_updated, sessions_count, total_knowledge_gained)
                VALUES (?, ?, ?, ?, 1, ?)
                ON CONFLICT(domain) DO UPDATE SET
                knowledge_level = knowledge_level + ?,
                confidence_level = (confidence_level + ?) / 2,
                last_updated = ?,
                sessions_count = sessions_count + 1,
                total_knowledge_gained = total_knowledge_gained + ?
            ''', (
                session.domain.value,
                knowledge_increase,
                confidence_increase,
                session.end_time,
                session.knowledge_gained,
                knowledge_increase,
                confidence_increase,
                session.end_time,
                session.knowledge_gained
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث تقدم التعلم: {e}")

    def analyze_learning_patterns(self) -> Dict[str, Any]:
        """تحليل أنماط التعلم والأداء"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # أداء الاستراتيجيات
            cursor.execute('''
                SELECT strategy, AVG(success_rate), COUNT(*) 
                FROM strategy_performance 
                GROUP BY strategy
            ''')
            strategy_performance = {
                row[0]: {"avg_success": row[1], "usage_count": row[2]}
                for row in cursor.fetchall()
            }
            
            # تقدم المجالات
            cursor.execute('''
                SELECT domain, knowledge_level, confidence_level, sessions_count
                FROM learning_progress
            ''')
            domain_progress = {
                row[0]: {
                    "knowledge_level": row[1],
                    "confidence_level": row[2],
                    "sessions_count": row[3]
                }
                for row in cursor.fetchall()
            }
            
            # جلسات التعلم الحديثة
            cursor.execute('''
                SELECT domain, strategy, knowledge_gained, confidence_boost
                FROM learning_sessions
                WHERE end_time > ?
                ORDER BY end_time DESC
                LIMIT 50
            ''', (time.time() - 86400,))  # آخر 24 ساعة
            
            recent_sessions = [
                {
                    "domain": row[0],
                    "strategy": row[1],
                    "knowledge_gained": row[2],
                    "confidence_boost": row[3]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            analysis = {
                "strategy_performance": strategy_performance,
                "domain_progress": domain_progress,
                "recent_sessions": recent_sessions,
                "overall_stats": self.learning_stats,
                "recommendations": self._generate_learning_recommendations(domain_progress, strategy_performance)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل أنماط التعلم: {e}")
            return {}

    def _generate_learning_recommendations(self, domain_progress: Dict, strategy_performance: Dict) -> List[str]:
        """توليد توصيات التعلم"""
        recommendations = []
        
        # البحث عن مجالات ضعيفة الأداء
        weak_domains = []
        for domain, progress in domain_progress.items():
            if progress["knowledge_level"] < 0.3 and progress["sessions_count"] > 0:
                weak_domains.append(domain)
        
        if weak_domains:
            recommendations.append(f"💡 التركيز على تحسين المجالات الضعيفة: {', '.join(weak_domains)}")
        
        # البحث عن استراتيجيات فعالة
        effective_strategies = []
        for strategy, performance in strategy_performance.items():
            if performance["avg_success"] > 0.8:
                effective_strategies.append(strategy)
        
        if effective_strategies:
            recommendations.append(f"🎯 زيادة استخدام الاستراتيجيات الفعالة: {', '.join(effective_strategies)}")
        
        # توصيات بناءً على الإحصائيات
        if self.learning_stats["successful_learnings"] / max(1, self.learning_stats["total_sessions"]) < 0.6:
            recommendations.append("📈 تحسين جودة جلسات التعلم لزيادة معدل النجاح")
        
        if len(self.learning_stats["domains_covered"]) < 4:
            recommendations.append("🌐 توسيع نطاق التعلم لتغطية مجالات معرفية أكثر")
        
        return recommendations

    def optimize_learning_parameters(self) -> Dict[str, Any]:
        """تحسين معاملات التعلم تلقائياً"""
        optimizations = {}
        
        # تحليل أداء الاستراتيجيات
        strategy_analysis = self.analyze_learning_patterns()
        
        for strategy, performance in strategy_analysis.get("strategy_performance", {}).items():
            if performance["avg_success"] < 0.6:
                # تقليل استخدام الاستراتيجيات ضعيفة الأداء
                strategy_enum = LearningStrategy(strategy)
                if strategy_enum in self.learning_strategies:
                    self.learning_strategies[strategy_enum]["efficiency"] *= 0.9
                    optimizations[f"reduce_{strategy}"] = "خفض كفاءة الاستراتيجية due to poor performance"
        
        # تحسين مجالات المعرفة
        for domain, progress in strategy_analysis.get("domain_progress", {}).items():
            if progress["knowledge_level"] < 0.2:
                # زيادة أولوية المجالات الضعيفة
                domain_enum = KnowledgeDomain(domain)
                if domain_enum in self.knowledge_domains:
                    self.knowledge_domains[domain_enum]["priority"] = min(
                        self.knowledge_domains[domain_enum]["priority"] * 1.2, 1.0
                    )
                    optimizations[f"boost_{domain}"] = "زيادة أولوية المجال due to low knowledge level"
        
        logger.info(f"🔧 تم إجراء {len(optimizations)} تحسين في معاملات التعلم")
        return optimizations

    def get_learning_plan(self, target_domains: List[KnowledgeDomain] = None) -> Dict[str, Any]:
        """إنشاء خطة تعلم مخصصة"""
        if target_domains is None:
            target_domains = list(KnowledgeDomain)
        
        learning_plan = {
            "created_at": time.time(),
            "target_domains": [domain.value for domain in target_domains],
            "sessions_plan": [],
            "expected_outcomes": {},
            "timeline": {}
        }
        
        for domain in target_domains:
            # اختيار أفضل استراتيجية للمجال
            strategy = self._select_optimal_strategy(domain)
            
            # تقدير الوقت المطلوب
            domain_config = self.knowledge_domains[domain]
            estimated_time = domain_config["learning_difficulty"] * 3600  # بالثواني
            
            session_plan = {
                "domain": domain.value,
                "strategy": strategy.value,
                "estimated_duration": estimated_time,
                "priority": domain_config["priority"],
                "topics_to_cover": self._generate_domain_topics(domain)
            }
            
            learning_plan["sessions_plan"].append(session_plan)
            
            # النتائج المتوقعة
            learning_plan["expected_outcomes"][domain.value] = {
                "knowledge_increase": domain_config["knowledge_density"] * 0.8,
                "confidence_boost": domain_config["priority"] * 0.7,
                "success_probability": self.learning_strategies[strategy]["efficiency"]
            }
        
        # ترتيب الجلسات حسب الأولوية
        learning_plan["sessions_plan"].sort(key=lambda x: x["priority"], reverse=True)
        
        # إنشاء جدول زمني
        current_time = time.time()
        for i, session in enumerate(learning_plan["sessions_plan"]):
            learning_plan["timeline"][session["domain"]] = {
                "scheduled_start": current_time + (i * 3600),  # كل ساعة جلسة
                "estimated_end": current_time + (i * 3600) + session["estimated_duration"]
            }
        
        return learning_plan

    def _generate_domain_topics(self, domain: KnowledgeDomain) -> List[str]:
        """توليد مواضيع للمجال المعرفي"""
        topic_templates = {
            KnowledgeDomain.PROGRAMMING: [
                "أساسيات البرمجة بلغة Python",
                "هياكل البيانات والخوارزميات",
                "تطوير تطبيقات الويب",
                "قواعد البيانات والإستعلامات",
                "مبادئ التصميم وأنماط البرمجة"
            ],
            KnowledgeDomain.TECHNOLOGY: [
                "مقدمة في الذكاء الاصطناعي",
                "تعلم الآلة والتطبيقات",
                "الحوسبة السحابية",
                "أمن المعلومات",
                "إنترنت الأشياء"
            ],
            KnowledgeDomain.SCIENCE: [
                "الفيزياء الحديثة",
                "الكيمياء العضوية",
                "الأحياء الجزيئية",
                "علوم الفضاء",
                "البيئة والمناخ"
            ],
            KnowledgeDomain.GENERAL: [
                "الثقافة العامة",
                "التاريخ والحضارات",
                "الجغرافيا والطقس",
                "الفنون والأدب",
                "الرياضيات الأساسية"
            ]
        }
        
        return topic_templates.get(domain, ["مواضيع عامة في المجال"])

    def get_learning_report(self) -> Dict[str, Any]:
        """إنشاء تقرير تعلم شامل"""
        analysis = self.analyze_learning_patterns()
        optimizations = self.optimize_learning_parameters()
        learning_plan = self.get_learning_plan()
        
        report = {
            "report_id": f"report_{int(time.time() * 1000)}",
            "generated_at": time.time(),
            "summary": {
                "total_learning_sessions": self.learning_stats["total_sessions"],
                "success_rate": self.learning_stats["successful_learnings"] / max(1, self.learning_stats["total_sessions"]),
                "total_knowledge_gained": self.learning_stats["total_knowledge_gained"],
                "domains_covered": len(self.learning_stats["domains_covered"]),
                "average_confidence": self.learning_stats["average_confidence"]
            },
            "performance_analysis": analysis,
            "optimizations_applied": optimizations,
            "future_learning_plan": learning_plan,
            "recommendations": analysis.get("recommendations", [])
        }
        
        return report

    def export_learning_data(self) -> Dict[str, Any]:
        """تصدير بيانات التعلم"""
        return {
            "exported_at": time.time(),
            "learning_stats": self.learning_stats,
            "knowledge_domains": {
                domain.value: config for domain, config in self.knowledge_domains.items()
            },
            "learning_strategies": {
                strategy.value: config for strategy, config in self.learning_strategies.items()
            },
            "active_sessions": {
                session_id: session.to_dict() 
                for session_id, session in self.learning_sessions.items()
            }
        }

# استخدام عالمي
_global_learning_optimizer = None

def get_global_learning_optimizer() -> LearningOptimizer:
    """الحصول على محسن التعلم العالمي"""
    global _global_learning_optimizer
    if _global_learning_optimizer is None:
        _global_learning_optimizer = LearningOptimizer()
    return _global_learning_optimizer

# دالة مساعدة للاستخدام السريع
def optimize_learning_response(user_query: str, bot_response: str, user_feedback: Optional[str] = None) -> Dict[str, Any]:
    """تحسين استجابة التعلم بناءً على التفاعل"""
    optimizer = get_global_learning_optimizer()
    
    # كشف مجال الاستعلام
    domain = detect_query_domain(user_query)
    
    # بدء جلسة تعلم
    session_id = optimizer.start_learning_session(domain)
    
    # حساب مقاييس الأداء
    metrics = calculate_response_metrics(user_query, bot_response, user_feedback)
    optimizer.update_learning_metrics(session_id, metrics)
    
    # إنهاء الجلسة مع نتائج التعلم
    knowledge_gained = estimate_knowledge_gain(bot_response)
    confidence_boost = metrics.user_satisfaction * 0.5
    
    optimizer.end_learning_session(session_id, knowledge_gained, confidence_boost)
    
    return {
        "session_id": session_id,
        "domain": domain.value,
        "metrics": metrics.overall_score(),
        "knowledge_gained": knowledge_gained
    }

def detect_query_domain(query: str) -> KnowledgeDomain:
    """كشف مجال الاستعلام"""
    query_lower = query.lower()
    
    domain_keywords = {
        KnowledgeDomain.PROGRAMMING: [r"كود", r"برمجة", r"بايثون", r"جافا", r"html", r"css"],
        KnowledgeDomain.TECHNOLOGY: [r"تقنية", r"تكنولوجيا", r"ذكاء", r"آلة", r"بيانات"],
        KnowledgeDomain.SCIENCE: [r"علم", r"بحث", r"نظرية", r"تجربة", r"فيزياء", r"كيمياء"],
        KnowledgeDomain.BUSINESS: [r"تجارة", r"شركة", r"سوق", r"ربح", r"استثمار"],
        KnowledgeDomain.HEALTH: [r"صحة", r"طب", r"علاج", r"دواء", r"مرض"],
        KnowledgeDomain.EDUCATION: [r"تعلم", r"دراسة", r"مدرسة", r"جامعة", r"تعليم"]
    }
    
    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if re.search(keyword, query_lower):
                return domain
    
    return KnowledgeDomain.GENERAL

def calculate_response_metrics(user_query: str, bot_response: str, user_feedback: Optional[str] = None) -> LearningMetrics:
    """حساب مقاييس جودة الاستجابة"""
    metrics = LearningMetrics()
    
    # حساب الدقة (بناءً على طول الاستجابة وجودة المحتوى)
    metrics.accuracy = min(len(bot_response) / 500, 1.0) * 0.8
    
    # حساب الصلة (بناءً على تطابق الكلمات الرئيسية)
    query_words = set(user_query.lower().split())
    response_words = set(bot_response.lower().split())
    common_words = query_words.intersection(response_words)
    metrics.relevance = min(len(common_words) / max(1, len(query_words)), 1.0)
    
    # حساب الاكتمال (بناءً على هيكل الاستجابة)
    completeness_indicators = ["\n", ". ", "، ", "• ", "- "]
    metrics.completeness = sum(1 for indicator in completeness_indicators if indicator in bot_response) / len(completeness_indicators)
    
    # وقت الاستجابة (قيمة افتراضية)
    metrics.response_time = 0.8
    
    # رضا المستخدم (بناءً على التغذية الراجعة)
    if user_feedback:
        positive_indicators = ["شكر", "ممتاز", "رائع", "جميل", "أحسنت"]
        metrics.user_satisfaction = 1.0 if any(indicator in user_feedback for indicator in positive_indicators) else 0.3
    else:
        metrics.user_satisfaction = 0.7  # قيمة افتراضية
    
    # احتفاظ المعرفة (بناءً على جودة المحتوى)
    metrics.knowledge_retention = (metrics.accuracy + metrics.completeness) / 2
    
    return metrics

def estimate_knowledge_gain(response: str) -> int:
    """تقدير كمية المعرفة المكتسبة"""
    # حساب بناءً على طول وجودة الاستجابة
    base_gain = len(response) // 10  # 10 حروف = 1 نقطة معرفة
    
    # تعزيز بناءً على مؤشرات الجودة
    quality_indicators = ["```", "def ", "function", "class ", "CREATE TABLE", "<html>"]
    quality_boost = sum(10 for indicator in quality_indicators if indicator in response)
    
    return base_gain + quality_boost
