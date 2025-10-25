# core/memory.py — نظام الذاكرة الذكية مع تحسينات الأداء
from __future__ import annotations
import os
import sqlite3
import time
import re
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from rank_bm25 import BM25Okapi
import hashlib

# إعداد التسجيل
logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("BASSAM_DB", "bassam_v2.db")

# كلمات التوقف العربية المحسنة
_AR_STOP = set("""
و في على من مع عن الى إلى أو أم ثم بل قد لقد كان كانت كانوا كن كنت كنتن يكون تكون تكونون تكونن
هذا هذه ذلك تلك هناك هنا حيث كذلك كما كيف لماذا لما إن أن إنما أنما ألا إلا ما لا لم لن هل
جدا جداً فقط أيضا أيضًا أي أيًّا أيها التي الذي الذين اللذان اللتان اللواتي اللائي أولئك هؤلاء
حين عندما بينما أثناء بسبب لدى ضمن دون غير بين قبل بعد منذ حتى خلال فوق تحت أمام وراء
لذلك لهذا لذا لأن كي لكي إذ إذا إلا إنّ أنّ ألا لكن اللي الي عند عنا عنه عليها عليه
بعض كل اي اى بعد قبل حين دون غير سوى الا إلا بلا فلان انا انت انتم انتن نحن
""".split())

# ذاكرة التخزين المؤقت المحسنة
_memory_cache: List[Dict] = []
_bm25: Optional[BM25Okapi] = None
_last_rebuild: float = 0
_cache_ttl: int = 300  # 5 دقائق

class MemoryManager:
    """مدير الذاكرة المتقدم"""
    
    def __init__(self):
        self.connection_pool = []
        self.max_connections = 5
        
    def get_connection(self) -> sqlite3.Connection:
        """الحصول على اتصال من المجمع"""
        if self.connection_pool:
            return self.connection_pool.pop()
        else:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
            
    def return_connection(self, conn: sqlite3.Connection):
        """إعادة الاتصال إلى المجمع"""
        if len(self.connection_pool) < self.max_connections:
            self.connection_pool.append(conn)
        else:
            conn.close()

# مدير الذاكرة العالمي
memory_manager = MemoryManager()

def _connect() -> sqlite3.Connection:
    """الحصول على اتصال قاعدة بيانات"""
    return memory_manager.get_connection()

def _close_connection(conn: sqlite3.Connection):
    """إغلاق الاتصال"""
    memory_manager.return_connection(conn)

def init_db():
    """تهيئة قاعدة البيانات مع الجداول المحسنة"""
    conn = _connect()
    cur = conn.cursor()
    
    try:
        # جدول الحقائق المحسن
        cur.execute("""
            CREATE TABLE IF NOT EXISTS facts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                normalized_text TEXT,
                source TEXT,
                category TEXT,
                quality_score REAL DEFAULT 1.0,
                usage_count INTEGER DEFAULT 0,
                last_used INTEGER DEFAULT 0,
                added_at INTEGER,
                hash TEXT UNIQUE
            )
        """)
        
        # جدول المحادثات المحسن
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_msg TEXT NOT NULL,
                bot_msg TEXT NOT NULL,
                intent_type TEXT,
                confidence REAL,
                sources_json TEXT,
                session_id TEXT,
                ts INTEGER
            )
        """)
        
        # جدول الفئات
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT
            )
        """)
        
        # جدول الإحصائيات
        cur.execute("""
            CREATE TABLE IF NOT EXISTS statistics(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value INTEGER,
                updated_at INTEGER
            )
        """)
        
        # إنشاء الفئات الأساسية
        default_categories = [
            ("برمجة", "مواضيع البرمجة والتطوير"),
            ("تقنية", "التقنيات والذكاء الاصطناعي"),
            ("علم", "المعلومات العلمية"),
            ("صحة", "المواضيع الصحية"),
            ("عام", "المعلومات العامة")
        ]
        
        for name, desc in default_categories:
            cur.execute(
                "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                (name, desc)
            )
        
        # إنشاء الفهرس للمساعدة في البحث
        cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_text ON facts(normalized_text)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_facts_quality ON facts(quality_score)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_conv_ts ON conversations(ts)")
        
        conn.commit()
        logger.info("✅ قاعدة البيانات مهيأة بنجاح")
        
    except Exception as e:
        logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
        conn.rollback()
    finally:
        _close_connection(conn)
    
    _rebuild_index()

def _enhanced_normalize(s: str) -> str:
    """تنقية محسّنة للنص العربي مع معالجة متقدمة"""
    if not s:
        return ""
        
    s = str(s).strip().lower()
    
    # استبدال الحروف المتباينة
    repl = {
        "أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي", "ـ": "",
        "َ": "", "ُ": "", "ِ": "", "ّ": "", "ْ": "", "ً": "", "ٌ": "", "ٍ": ""
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    
    # إزالة علامات الترقيم والرموز
    s = re.sub(r'[^\w\s]', ' ', s)
    
    # إزالة الأرقام المنفردة
    s = re.sub(r'\b\d+\b', ' ', s)
    
    # إزالة المسافات الزائدة والكلمات القصيرة
    words = [w for w in s.split() if w not in _AR_STOP and len(w) > 1]
    
    return " ".join(words)

def _calculate_text_hash(text: str) -> str:
    """حساب بصمة النص لمنع التكرار"""
    normalized = _enhanced_normalize(text)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def _rebuild_index(force: bool = False):
    """إعادة بناء الفهرس مع التخزين المؤقت"""
    global _memory_cache, _bm25, _last_rebuild
    
    current_time = time.time()
    if not force and current_time - _last_rebuild < _cache_ttl:
        return
        
    try:
        conn = _connect()
        cur = conn.cursor()
        
        # جلب الحقائق مع التصفية بالجودة
        cur.execute("""
            SELECT id, text, source, category, quality_score 
            FROM facts 
            WHERE quality_score >= 0.3 
            ORDER BY quality_score DESC, usage_count DESC 
            LIMIT 10000
        """)
        
        rows = cur.fetchall()
        _memory_cache = [
            {
                "id": r[0],
                "text": r[1],
                "source": r[2] or "",
                "category": r[3] or "عام",
                "quality": r[4]
            }
            for r in rows
        ]
        
        _close_connection(conn)
        
        # بناء الفهرس BM25
        if _memory_cache:
            corpus = [_enhanced_normalize(item["text"]) for item in _memory_cache]
            tokenized_corpus = [doc.split() for doc in corpus if doc.strip()]
            if tokenized_corpus:
                _bm25 = BM25Okapi(tokenized_corpus)
            else:
                _bm25 = None
        else:
            _bm25 = None
            
        _last_rebuild = current_time
        logger.info(f"🔄 تم إعادة بناء الفهرس ({len(_memory_cache)} عنصر)")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إعادة بناء الفهرس: {e}")

def add_fact(text: str, source: str | None = None, category: str = "عام"):
    """إضافة حقيقة جديدة مع التحقق من الجودة والتكرار"""
    if not text or len(text.strip()) < 10:
        return False
        
    # التحقق من الجودة
    quality = _calculate_fact_quality(text)
    if quality < 0.2:
        return False
        
    # التحقق من التكرار
    text_hash = _calculate_text_hash(text)
    
    conn = _connect()
    cur = conn.cursor()
    
    try:
        # التحقق من وجود النص مسبقاً
        cur.execute("SELECT id FROM facts WHERE hash = ?", (text_hash,))
        existing = cur.fetchone()
        
        if existing:
            # تحديث الاستخدام إذا كان موجوداً
            cur.execute(
                "UPDATE facts SET usage_count = usage_count + 1, last_used = ? WHERE id = ?",
                (int(time.time()), existing[0])
            )
            conn.commit()
            _close_connection(conn)
            return True
        
        # إضافة حقيقة جديدة
        normalized = _enhanced_normalize(text)
        cur.execute("""
            INSERT INTO facts 
            (text, normalized_text, source, category, quality_score, added_at, hash) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (text.strip(), normalized, source, category, quality, int(time.time()), text_hash))
        
        conn.commit()
        _close_connection(conn)
        
        # إعادة بناء الفهرس
        _rebuild_index(force=True)
        
        logger.info(f"✅ تم إضافة حقيقة جديدة: {text[:50]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطأ في إضافة الحقيقة: {e}")
        conn.rollback()
        _close_connection(conn)
        return False

def _calculate_fact_quality(text: str) -> float:
    """حساب جودة الحقيقة من 0 إلى 1"""
    if not text or len(text) < 20:
        return 0.0
        
    # عوامل خفض الجودة
    penalty_phrases = [
        "انقر هنا", "اشترك الآن", "لمزيد من المعلومات", "تسجيل الدخول",
        "إعلان", "رابط خارجي", "شاهد أيضاً", "تابعنا على"
    ]
    
    score = 0.5  # درجة أساسية
    
    # عوامل رفع الجودة
    if len(text) > 50: score += 0.1
    if len(text.split()) > 8: score += 0.1
    if any(char.isdigit() for char in text): score += 0.1
    if "." in text: score += 0.1
    if ":" in text: score += 0.05
    
    # عوامل خفض الجودة
    for phrase in penalty_phrases:
        if phrase in text.lower():
            score -= 0.3
            break
            
    if text.count("!") > 2: score -= 0.2
    if text.count("http") > 0: score -= 0.2
    
    return max(0.1, min(1.0, score))

def save_conv(user_msg: str, bot_msg: str, intent_type: str = None, 
              confidence: float = None, sources: List[dict] = None, session_id: str = "default"):
    """حفظ محادثة مع بيانات إضافية"""
    conn = _connect()
    cur = conn.cursor()
    
    try:
        sources_json = json.dumps(sources or [])
        
        cur.execute("""
            INSERT INTO conversations 
            (user_msg, bot_msg, intent_type, confidence, sources_json, session_id, ts) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_msg, bot_msg, intent_type, confidence, sources_json, session_id, int(time.time())))
        
        conn.commit()
        
        # تحديث إحصائيات الاستخدام
        _update_statistics("total_conversations")
        
    except Exception as e:
        logger.error(f"❌ خطأ في حفظ المحادثة: {e}")
        conn.rollback()
    finally:
        _close_connection(conn)

def search_memory(q: str, limit: int = 5, min_score: float = 0.1, 
                 category: str = None) -> List[Dict]:
    """بحث محسن في الذاكرة مع تصفية متقدمة"""
    if not _bm25 or not _memory_cache or not q.strip():
        return []
    
    # تطبيع query
    norm_q = _enhanced_normalize(q)
    if not norm_q:
        return []
    
    try:
        # البحث باستخدام BM25
        tokenized_query = norm_q.split()
        scores = _bm25.get_scores(tokenized_query)
        
        # جمع النتائج مع التصفية
        results = []
        for i, (item, score) in enumerate(zip(_memory_cache, scores)):
            if score >= min_score:
                # تطبيق تصفية الفئة إذا كانت محددة
                if category and item.get("category") != category:
                    continue
                    
                results.append({
                    "id": item["id"],
                    "text": item["text"],
                    "source": item["source"],
                    "category": item.get("category", "عام"),
                    "quality": item.get("quality", 1.0),
                    "score": float(score),
                    "rank": i + 1
                })
        
        # ترتيب النتائج
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # تحديث عدد الاستخدامات للنتائج الأولى
        if results:
            _update_usage_counts([r["id"] for r in results[:3]])
        
        return results[:limit]
        
    except Exception as e:
        logger.error(f"❌ خطأ في البحث: {e}")
        return []

def _update_usage_counts(fact_ids: List[int]):
    """تحديث عدد مرات استخدام الحقائق"""
    if not fact_ids:
        return
        
    conn = _connect()
    cur = conn.cursor()
    
    try:
        placeholders = ','.join('?' * len(fact_ids))
        cur.execute(f"""
            UPDATE facts 
            SET usage_count = usage_count + 1, last_used = ? 
            WHERE id IN ({placeholders})
        """, [int(time.time())] + fact_ids)
        
        conn.commit()
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث الاستخدام: {e}")
    finally:
        _close_connection(conn)

def _update_statistics(stat_key: str):
    """تحديث الإحصائيات"""
    conn = _connect()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO statistics (key, value, updated_at) 
            VALUES (?, 1, ?)
            ON CONFLICT(key) DO UPDATE SET 
            value = value + 1, updated_at = ?
        """, (stat_key, int(time.time()), int(time.time())))
        
        conn.commit()
    except Exception as e:
        logger.error(f"❌ خطأ في تحديث الإحصائيات: {e}")
    finally:
        _close_connection(conn)

def manage_memory_size(max_facts: int = 8000, max_conversations: int = 5000):
    """إدارة حجم الذاكرة مع الاحتفاظ بالأهم"""
    conn = _connect()
    cur = conn.cursor()
    
    try:
        # إدارة الحقائق - الاحتفاظ بالأعلى جودة واستخداماً
        cur.execute("SELECT COUNT(*) FROM facts")
        fact_count = cur.fetchone()[0]
        
        if fact_count > max_facts:
            delete_count = fact_count - max_facts
            cur.execute("""
                DELETE FROM facts 
                WHERE id IN (
                    SELECT id FROM facts 
                    ORDER BY quality_score ASC, usage_count ASC, last_used ASC 
                    LIMIT ?
                )
            """, (delete_count,))
            logger.info(f"🧹 تم حذف {delete_count} حقيقة قديمة")
        
        # إدارة المحادثات - الاحتفاظ بالأحدث
        cur.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cur.fetchone()[0]
        
        if conv_count > max_conversations:
            delete_count = conv_count - max_conversations
            cur.execute("""
                DELETE FROM conversations 
                WHERE id IN (
                    SELECT id FROM conversations 
                    ORDER BY ts ASC 
                    LIMIT ?
                )
            """, (delete_count,))
            logger.info(f"🧹 تم حذف {delete_count} محادثة قديمة")
        
        conn.commit()
        
        # إعادة بناء الفهرس
        _rebuild_index(force=True)
        
    except Exception as e:
        logger.error(f"❌ خطأ في إدارة الذاكرة: {e}")
        conn.rollback()
    finally:
        _close_connection(conn)

def get_memory_stats() -> Dict:
    """الحصول على إحصائيات الذاكرة"""
    conn = _connect()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM facts")
        total_facts = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cur.fetchone()[0]
        
        cur.execute("SELECT AVG(quality_score) FROM facts")
        avg_quality = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM facts WHERE quality_score >= 0.7")
        high_quality_facts = cur.fetchone()[0]
        
        return {
            "total_facts": total_facts,
            "total_conversations": total_conversations,
            "average_quality": round(avg_quality, 2),
            "high_quality_facts": high_quality_facts,
            "cached_items": len(_memory_cache),
            "index_status": "active" if _bm25 else "inactive"
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في جلب الإحصائيات: {e}")
        return {}
    finally:
        _close_connection(conn)

def get_recent_conversations(limit: int = 10, session_id: str = "default") -> List[Dict]:
    """الحصول على المحادثات الحديثة"""
    conn = _connect()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT user_msg, bot_msg, intent_type, ts 
            FROM conversations 
            WHERE session_id = ? 
            ORDER BY ts DESC 
            LIMIT ?
        """, (session_id, limit))
        
        results = cur.fetchall()
        return [
            {
                "user": r[0],
                "bot": r[1],
                "intent": r[2],
                "timestamp": r[3]
            }
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"❌ خطأ في جلب المحادثات: {e}")
        return []
    finally:
        _close_connection(conn)

def get_context(user_msg: str, limit: int = 3) -> List[Dict]:
    """الحصول على سياق ذكي للمحادثة"""
    recent_conv = get_recent_conversations(limit=5)
    memory_context = search_memory(user_msg, limit=limit)
    
    return {
        "conversation_history": recent_conv[:2],
        "relevant_memory": memory_context,
        "timestamp": int(time.time())
    }
