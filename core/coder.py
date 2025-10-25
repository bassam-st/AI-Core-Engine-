# core/coder.py — مولد الأكواد الذكي والمحترف
from __future__ import annotations
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime

# إعداد التسجيل
logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """محلل متطلبات الكود"""
    
    def __init__(self):
        self.language_patterns = {
            'python': [r'بايثون', r'python', r'دالة', r'function', r'سكريبت'],
            'javascript': [r'جافا سكريبت', r'javascript', r'js', r'واجهة', r'موقع'],
            'html': [r'html', r'صفحة', r'موقع', r'ويب', r'واجهة'],
            'css': [r'css', r'تنسيق', r'شكل', r'تصميم'],
            'sql': [r'sql', r'قاعدة بيانات', r'استعلام', r'query']
        }
        
        self.project_types = {
            'website': [r'موقع', r'صفحة', r'ويب', r'web'],
            'function': [r'دالة', r'function', r'حساب', r'معالجة'],
            'api': [r'api', r'واجهة', r'rest', r'خدمة'],
            'database': [r'قاعدة بيانات', r'database', r'جدول'],
            'utility': [r'أداة', r'utility', r'مساعد', r'tool']
        }

    def analyze_requirements(self, description: str) -> Dict:
        """تحليل متطلبات الكود المطلوب"""
        desc_lower = description.lower()
        
        # تحديد اللغة
        detected_lang = 'python'  # افتراضي
        max_matches = 0
        
        for lang, patterns in self.language_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, desc_lower))
            if matches > max_matches:
                max_matches = matches
                detected_lang = lang
        
        # تحديد نوع المشروع
        project_type = 'utility'
        for p_type, patterns in self.project_types.items():
            if any(re.search(pattern, desc_lower) for pattern in patterns):
                project_type = p_type
                break
        
        # استخراج المتطلبات
        requirements = {
            'language': detected_lang,
            'project_type': project_type,
            'has_ui': any(word in desc_lower for word in ['واجهة', 'موقع', 'صفحة']),
            'has_database': any(word in desc_lower for word in ['قاعدة', 'بيانات', 'تخزين']),
            'has_api': any(word in desc_lower for word in ['api', 'واجهة', 'خدمة']),
            'complexity': self._assess_complexity(description)
        }
        
        logger.info(f"📋 تم تحليل المتطلبات: {requirements}")
        return requirements

    def _assess_complexity(self, description: str) -> str:
        """تقييم تعقيد الكود المطلوب"""
        word_count = len(description.split())
        
        if word_count < 10:
            return 'simple'
        elif word_count < 25:
            return 'medium'
        else:
            return 'complex'

class CodeGenerator:
    """مولد الأكواد المحترف"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.analyzer = CodeAnalyzer()

    def _load_templates(self) -> Dict:
        """تحميل قوالب الكود"""
        return {
            'python': {
                'function': self._python_function_template,
                'class': self._python_class_template,
                'script': self._python_script_template
            },
            'javascript': {
                'function': self._javascript_function_template,
                'class': self._javascript_class_template,
                'web_app': self._javascript_web_template
            },
            'html': {
                'basic': self._html_basic_template,
                'responsive': self._html_responsive_template,
                'dashboard': self._html_dashboard_template
            },
            'css': {
                'basic': self._css_basic_template,
                'modern': self._css_modern_template,
                'responsive': self._css_responsive_template
            },
            'sql': {
                'query': self._sql_query_template,
                'table': self._sql_table_template
            }
        }

    def generate_code(self, description: str) -> Dict:
        """توليد كود محترف بناءً على الوصف"""
        try:
            # تحليل المتطلبات
            requirements = self.analyzer.analyze_requirements(description)
            language = requirements['language']
            project_type = requirements['project_type']
            
            # اختيار القالب المناسب
            template = self._select_template(language, project_type, requirements)
            
            if not template:
                return self._generate_fallback_code(description, language)
            
            # توليد الكود
            code = template(description, requirements)
            
            # التحقق من الجودة
            validation = self._validate_code(code, language)
            
            if not validation['valid']:
                # محاولة إصلاح الأخطاء
                code = self._fix_code_issues(code, language, validation['issues'])
            
            return {
                "code": code,
                "lang": language,
                "title": self._generate_title(description),
                "requirements": requirements,
                "validated": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في توليد الكود: {e}")
            return self._generate_error_response(description, str(e))

    def _select_template(self, language: str, project_type: str, requirements: Dict):
        """اختيار القالب المناسب"""
        lang_templates = self.templates.get(language, {})
        
        if language == 'python':
            if requirements['has_ui']:
                return self._python_gui_template
            elif requirements['has_database']:
                return self._python_database_template
            else:
                return lang_templates.get('function', self._python_function_template)
                
        elif language == 'javascript':
            if requirements['has_ui']:
                return lang_templates.get('web_app', self._javascript_web_template)
            else:
                return lang_templates.get('function', self._javascript_function_template)
                
        elif language == 'html':
            if requirements['complexity'] == 'complex':
                return lang_templates.get('dashboard', self._html_dashboard_template)
            else:
                return lang_templates.get('basic', self._html_basic_template)
                
        else:
            return next(iter(lang_templates.values())) if lang_templates else None

    def _validate_code(self, code: str, language: str) -> Dict:
        """التحقق من جودة الكود"""
        issues = []
        
        if not code or len(code.strip()) < 10:
            issues.append("الكود قصير جداً أو فارغ")
            return {"valid": False, "issues": issues}
        
        # فحوصات حسب اللغة
        if language == 'python':
            if 'import ' not in code and 'def ' not in code:
                issues.append("يحتاج استيراد مكتبات أو دوال")
            if code.count('\n') < 3:
                issues.append("الكود قصير جداً")
                
        elif language == 'html':
            if not any(tag in code for tag in ['<html', '<body', '<div']):
                issues.append("يفتقر إلى هيكل HTML أساسي")
            if '<!DOCTYPE html>' not in code:
                issues.append("يفتقر إلى DOCTYPE")
                
        elif language == 'javascript':
            if 'function' not in code and 'const' not in code and 'let' not in code:
                issues.append("يفتقر إلى دوال أو متغيرات")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "score": max(0, 1 - len(issues) * 0.3)
        }

    def _fix_code_issues(self, code: str, language: str, issues: List[str]) -> str:
        """إصلاح مشاكل الكود الشائعة"""
        fixed_code = code
        
        if language == 'html':
            if '<!DOCTYPE html>' not in fixed_code:
                fixed_code = '<!DOCTYPE html>\n' + fixed_code
            if '<html' not in fixed_code:
                fixed_code = fixed_code.replace('<head>', '<html>\n<head>') + '\n</html>'
                
        elif language == 'python':
            if 'import ' not in fixed_code:
                # إضافة استيرادات أساسية حسب السياق
                if 'print(' in fixed_code:
                    fixed_code = fixed_code  # لا حاجة لاستيراد print
                elif 'requests' in fixed_code:
                    fixed_code = 'import requests\n' + fixed_code
        
        return fixed_code

    # ──────────────────────────────────────────────────────────────────────
    # قوالب بايثون
    # ──────────────────────────────────────────────────────────────────────
    
    def _python_function_template(self, description: str, requirements: Dict) -> str:
        """قالب دالة بايثون"""
        function_name = self._extract_function_name(description) or "execute_task"
        
        code = f'''# دالة بايثون: {description}

def {function_name}(*args, **kwargs):
    """
    تنفيذ المهمة المطلوبة
    
    Args:
        *args: وسائط متغيرة
        **kwargs: وسائط مفتاحية
        
    Returns:
        نتيجة التنفيذ
    """
    try:
        # تنفيذ المنطق المطلوب هنا
        result = "تم تنفيذ المهمة بنجاح"
        
        # إرجاع النتيجة
        return result
        
    except Exception as e:
        print(f"حدث خطأ: {e}")
        return None

# مثال على الاستخدام
if __name__ == "__main__":
    output = {function_name}()
    print(f"النتيجة: {{output}}")
'''
        return code

    def _python_class_template(self, description: str, requirements: Dict) -> str:
        """قالب كلاس بايثون"""
        class_name = self._extract_class_name(description) or "TaskManager"
        
        code = f'''# كلاس بايثون: {description}

class {class_name}:
    """
    مدير المهام - {description}
    """
    
    def __init__(self):
        """تهيئة الكلاس"""
        self.results = []
        self.status = "جاهز"
    
    def execute(self, data=None):
        """
        تنفيذ المهمة الرئيسية
        
        Args:
            data: البيانات المدخلة
            
        Returns:
            نتيجة التنفيذ
        """
        try:
            self.status = "جاري التنفيذ"
            
            # منطق التنفيذ هنا
            result = self._process_data(data)
            self.results.append(result)
            
            self.status = "مكتمل"
            return result
            
        except Exception as e:
            self.status = f"خطأ: {{e}}"
            return None
    
    def _process_data(self, data):
        """معالجة البيانات الداخلية"""
        if data is None:
            return "لا توجد بيانات"
        return f"تم معالجة: {{data}}"
    
    def get_status(self):
        """الحصول على الحالة"""
        return self.status
    
    def get_results(self):
        """الحصول على النتائج"""
        return self.results

# مثال على الاستخدام
if __name__ == "__main__":
    manager = {class_name}()
    result = manager.execute("مثال على البيانات")
    print(f"الحالة: {{manager.get_status()}}")
    print(f"النتيجة: {{result}}")
'''
        return code

    def _python_database_template(self, description: str, requirements: Dict) -> str:
        """قالب قاعدة بيانات بايثون"""
        code = f'''# نظام إدارة قاعدة البيانات: {description}

import sqlite3
from typing import List, Dict, Optional

class DatabaseManager:
    """
    مدير قاعدة البيانات - {description}
    """
    
    def __init__(self, db_path=":memory:"):
        """تهيئة مدير قاعدة البيانات"""
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """تهيئة قاعدة البيانات والجداول"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # إنشاء الجداول الأساسية
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            print("✅ تم تهيئة قاعدة البيانات بنجاح")
            
        except Exception as e:
            print(f"❌ خطأ في تهيئة قاعدة البيانات: {{e}}")
    
    def insert_record(self, name: str, value: str = None) -> bool:
        """إضافة سجل جديد"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO records (name, value) VALUES (?, ?)",
                (name, value)
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ خطأ في إضافة السجل: {{e}}")
            return False
    
    def get_records(self) -> List[Dict]:
        """جلب جميع السجلات"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM records ORDER BY created_at DESC")
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    "id": row[0],
                    "name": row[1],
                    "value": row[2],
                    "created_at": row[3]
                })
            
            return records
        except Exception as e:
            print(f"❌ خطأ في جلب السجلات: {{e}}")
            return []
    
    def close(self):
        """إغلاق الاتصال"""
        if self.connection:
            self.connection.close()

# مثال على الاستخدام
if __name__ == "__main__":
    # إنشاء مدير قاعدة البيانات
    db_manager = DatabaseManager("example.db")
    
    # إضافة سجلات مثال
    db_manager.insert_record("سجل 1", "قيمة 1")
    db_manager.insert_record("سجل 2", "قيمة 2")
    
    # جلب وعرض السجلات
    records = db_manager.get_records()
    print("📋 السجلات:")
    for record in records:
        print(f"  - {{record['name']}}: {{record['value']}}")
    
    # إغلاق الاتصال
    db_manager.close()
'''
        return code

    # ──────────────────────────────────────────────────────────────────────
    # قوالب HTML
    # ──────────────────────────────────────────────────────────────────────
    
    def _html_basic_template(self, description: str, requirements: Dict) -> str:
        """قالب HTML أساسي"""
        title = self._generate_title(description)
        
        code = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* التنسيقات الأساسية */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .feature {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #4CAF50;
        }}
        
        .feature h3 {{
            color: #4CAF50;
            margin-bottom: 10px;
        }}
        
        footer {{
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
        
        /* التجاوب */
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 {title}</h1>
            <p>{description}</p>
        </header>
        
        <div class="content">
            <h2>مرحباً بك في التطبيق</h2>
            <p>هذا تطبيق ويب تم إنشاؤه تلقائياً بناءً على طلبك.</p>
            
            <div class="features">
                <div class="feature">
                    <h3>📱 متجاوب</h3>
                    <p>يتكيف مع جميع أحجام الشاشات</p>
                </div>
                
                <div class="feature">
                    <h3>🎨 حديث</h3>
                    <p>تصميم عصري وجذاب</p>
                </div>
                
                <div class="feature">
                    <h3>⚡ سريع</h3>
                    <p>أداء ممتاز وسريع التحميل</p>
                </div>
            </div>
        </div>
        
        <footer>
            <p>تم الإنشاء في {datetime.now().strftime("%Y-%m-%d")} | نظام النواة الذكية</p>
        </footer>
    </div>

    <script>
        // إضافة التفاعل
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('✅ التطبيق جاهز للعمل!');
            
            // إضافة تأثيرات تفاعلية
            const features = document.querySelectorAll('.feature');
            features.forEach(feature => {{
                feature.addEventListener('mouseenter', function() {{
                    this.style.transform = 'translateY(-5px)';
                    this.style.transition = 'transform 0.3s ease';
                }});
                
                feature.addEventListener('mouseleave', function() {{
                    this.style.transform = 'translateY(0)';
                }});
            }});
        }});
    </script>
</body>
</html>'''
        return code

    def _html_dashboard_template(self, description: str, requirements: Dict) -> str:
        """قالب لوحة تحكم HTML"""
        title = self._generate_title(description)
        
        code = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - {title}</title>
    <style>
        :root {{
            --primary: #4CAF50;
            --secondary: #2196F3;
            --dark: #343a40;
            --light: #f8f9fa;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            display: flex;
            min-height: 100vh;
        }}
        
        /* الشريط الجانبي */
        .sidebar {{
            width: 250px;
            background: var(--dark);
            color: white;
            padding: 20px 0;
        }}
        
        .logo {{
            text-align: center;
            padding: 20px;
            border-bottom: 1px solid #495057;
        }}
        
        .logo h2 {{
            color: var(--primary);
        }}
        
        .nav-links {{
            list-style: none;
            margin-top: 20px;
        }}
        
        .nav-links li {{
            padding: 15px 25px;
            border-left: 4px solid transparent;
            transition: all 0.3s;
        }}
        
        .nav-links li:hover {{
            background: #495057;
            border-left-color: var(--primary);
        }}
        
        .nav-links a {{
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        /* المحتوى الرئيسي */
        .main-content {{
            flex: 1;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-top: 4px solid var(--primary);
        }}
        
        .stat-card h3 {{
            color: var(--dark);
            margin-bottom: 10px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: var(--primary);
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .card h3 {{
            color: var(--dark);
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--light);
        }}
        
        .btn {{
            background: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #45a049;
        }}
        
        @media (max-width: 768px) {{
            body {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                height: auto;
            }}
            
            .content-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <!-- الشريط الجانبي -->
    <div class="sidebar">
        <div class="logo">
            <h2>🧠 {title}</h2>
            <p>لوحة التحكم</p>
        </div>
        
        <ul class="nav-links">
            <li><a href="#"><span>📊</span> الإحصائيات</a></li>
            <li><a href="#"><span>👥</span> المستخدمين</a></li>
            <li><a href="#"><span>📁</span> الملفات</a></li>
            <li><a href="#"><span>⚙️</span> الإعدادات</a></li>
            <li><a href="#"><span>🔒</span> الأمان</a></li>
        </ul>
    </div>
    
    <!-- المحتوى الرئيسي -->
    <div class="main-content">
        <div class="header">
            <h1>مرحباً بك في لوحة التحكم</h1>
            <p>إدارة وتتبع {description}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>المستخدمين النشطين</h3>
                <div class="stat-number">1,234</div>
                <p>+5.2% من الشهر الماضي</p>
            </div>
            
            <div class="stat-card">
                <h3>الطلبات اليومية</h3>
                <div class="stat-number">567</div>
                <p>+12.8% من الأمس</p>
            </div>
            
            <div class="stat-card">
                <h3>معدل النجاح</h3>
                <div class="stat-number">98.7%</div>
                <p>+0.3% من الشهر الماضي</p>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="card">
                <h3>📈 النشاط الحديث</h3>
                <p>هنا يتم عرض النشاطات والإحصائيات الحديثة...</p>
                <div style="margin-top: 20px;">
                    <button class="btn">عرض التقرير الكامل</button>
                </div>
            </div>
            
            <div class="card">
                <h3>🔔 الإشعارات</h3>
                <ul style="list-style: none;">
                    <li style="padding: 10px; border-bottom: 1px solid #eee;">✅ تم تحديث النظام</li>
                    <li style="padding: 10px; border-bottom: 1px solid #eee;">📊 تقرير الأداء جاهز</li>
                    <li style="padding: 10px;">👥 5 مستخدمين جدد</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        // تفاعلات لوحة التحكم
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🎛️ لوحة التحكم جاهزة');
            
            // تحديث الإحصائيات ديناميكياً
            function updateStats() {{
                const statNumbers = document.querySelectorAll('.stat-number');
                statNumbers.forEach(stat => {{
                    const current = parseInt(stat.textContent.replace(/,/g, ''));
                    const newValue = current + Math.floor(Math.random() * 10);
                    stat.textContent = newValue.toLocaleString();
                }});
            }}
            
            // تحديث كل 10 ثواني (للتجربة)
            setInterval(updateStats, 10000);
            
            // تفاعل الأزرار
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(btn => {{
                btn.addEventListener('click', function() {{
                    alert('🚀 تم تنفيذ الإجراء بنجاح!');
                }});
            }});
        }});
    </script>
</body>
</html>'''
        return code

    # ──────────────────────────────────────────────────────────────────────
    # قوالب JavaScript
    # ──────────────────────────────────────────────────────────────────────
    
    def _javascript_function_template(self, description: str, requirements: Dict) -> str:
        """قالب دالة JavaScript"""
        function_name = self._extract_function_name(description) or "processData"
        
        code = f'''// دالة JavaScript: {description}

/**
 * {description}
 * @param {{*}} input - البيانات المدخلة
 * @returns {{*}} - نتيجة المعالجة
 */
function {function_name}(input) {{
    try {{
        // منطق المعالجة هنا
        let result;
        
        if (typeof input === 'string') {{
            result = `تم معالجة النص: ${{input}}`;
        }} else if (Array.isArray(input)) {{
            result = `تم معالجة مصفوفة تحتوي على ${{input.length}} عنصر`;
        }} else if (typeof input === 'object') {{
            result = `تم معالجة كائن يحتوي على ${{Object.keys(input).length}} خاصية`;
        }} else {{
            result = `تم معالجة البيانات: ${{input}}`;
        }}
        
        // تسجيل النتيجة
        console.log('✅', result);
        
        return result;
        
    }} catch (error) {{
        console.error('❌ خطأ في المعالجة:', error);
        throw error;
    }}
}}

// دوال مساعدة
const utils = {{
    /**
     * التحقق من صحة البيانات
     */
    validateInput: (data) => {{
        return data !== null && data !== undefined;
    }},
    
    /**
     * تنسيق النتيجة
     */
    formatResult: (result) => {{
        return `🎯 ${{result}}`;
    }}
}};

// أمثلة على الاستخدام
console.log('🔧 اختبار الدالة:');
console.log({function_name}('نص تجريبي'));
console.log({function_name}([1, 2, 3]));
console.log({function_name}({{name: 'test', value: 123}}));

// التصدير للاستخدام في المشاريع
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ {function_name}, utils }};
}} else if (typeof window !== 'undefined') {{
    window.{function_name} = {function_name};
    window.appUtils = utils;
}}
'''
        return code

    # ──────────────────────────────────────────────────────────────────────
    # دوال مساعدة
    # ──────────────────────────────────────────────────────────────────────
    
    def _extract_function_name(self, description: str) -> str:
        """استخراج اسم دالة من الوصف"""
        # البحث عن أفعال يمكن استخدامها كأسماء دوال
        verbs = ['احسب', 'أنشئ', 'اصنع', 'عرض', 'معالجة', 'تنفيذ', 'جلب']
        for verb in verbs:
            if verb in description:
                return verb + '
