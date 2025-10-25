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
        print(f"حدث خطأ: {{e}}")
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
                records.append({{
                    "id": row[0],
                    "name": row[1],
                    "value": row[2],
                    "created_at": row[3]
                }})
            
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

    def _python_gui_template(self, description: str, requirements: Dict) -> str:
        """قالب واجهة مستخدم بايثون"""
        code = f'''# واجهة مستخدم بايثون: {description}

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("❌ tkinter غير مثبت. جرب: sudo apt-get install python3-tk")

class App:
    """
    تطبيق واجهة مستخدم - {description}
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("{description}")
        self.root.geometry("600x400")
        self.root.configure(bg='#f0f0f0')
        
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # العنوان
        title_label = ttk.Label(
            main_frame, 
            text="🚀 {description}", 
            font=("Arial", 16, "bold"),
            foreground="#4CAF50"
        )
        title_label.pack(pady=10)
        
        # وصف التطبيق
        desc_label = ttk.Label(
            main_frame,
            text="هذا تطبيق واجهة مستخدم تم إنشاؤه تلقائياً",
            font=("Arial", 10)
        )
        desc_label.pack(pady=5)
        
        # حقل الإدخال
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(pady=20, fill=tk.X)
        
        ttk.Label(input_frame, text="أدخل النص:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(input_frame, width=40)
        self.entry.pack(side=tk.LEFT, padx=10)
        
        # أزرار التحكم
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame, 
            text="معالجة", 
            command=self.process_data
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="مسح", 
            command=self.clear_data
        ).pack(side=tk.LEFT, padx=5)
        
        # منطقة النتائج
        result_frame = ttk.LabelFrame(main_frame, text="النتائج", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.result_text = tk.Text(result_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def process_data(self):
        """معالجة البيانات"""
        input_text = self.entry.get().strip()
        
        if not input_text:
            messagebox.showwarning("تحذير", "الرجاء إدخال نص")
            return
        
        try:
            # منطق المعالجة
            result = f"تم معالجة النص: {{input_text}}\\n"
            result += f"طول النص: {{len(input_text)}} حرف\\n"
            result += f"الكلمات: {{len(input_text.split())}} كلمة\\n"
            result += f"الوقت: {{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في المعالجة: {{e}}")
    
    def clear_data(self):
        """مسح البيانات"""
        self.entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)

def main():
    """الدالة الرئيسية"""
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
        return code

    def _python_script_template(self, description: str, requirements: Dict) -> str:
        """قالب سكريبت بايثون"""
        code = f'''# سكريبت بايثون: {description}

import sys
import os
import argparse
from datetime import datetime

def main():
    """الدالة الرئيسية للسكريبت"""
    print("🚀 بدء تشغيل السكريبت...")
    print(f"الوصف: {description}")
    print(f"الوقت: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
    
    # معالجة وسائط命令行
    parser = argparse.ArgumentParser(description='{description}')
    parser.add_argument('--input', '-i', help='ملف الإدخال')
    parser.add_argument('--output', '-o', help='ملف الإخراج')
    parser.add_argument('--verbose', '-v', action='store_true', help='وضع التفصيل')
    
    args = parser.parse_args()
    
    if args.verbose:
        print("🔧 وضع التفصيل مفعل")
    
    try:
        # تنفيذ المهمة الرئيسية
        result = execute_task(args)
        
        if args.verbose:
            print(f"✅ النتيجة: {{result}}")
        
        print("🎉 تم تنفيذ السكريبت بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ: {{e}}", file=sys.stderr)
        sys.exit(1)

def execute_task(args):
    """تنفيذ المهمة المطلوبة"""
    # إضافة منطقك هنا
    if args.input:
        return f"تم معالجة الملف: {{args.input}}"
    else:
        return "تم تنفيذ المهمة بدون مدخلات"

if __name__ == "__main__":
    main()
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

    def _html_responsive_template(self, description: str, requirements: Dict) -> str:
        """قالب HTML متجاوب"""
        title = self._generate_title(description)
        
        code = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: #4CAF50;
            --secondary: #2196F3;
            --accent: #FF9800;
            --dark: #2c3e50;
            --light: #ecf0f1;
            --shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.7;
            color: var(--dark);
            background: var(--light);
        }}
        
        .navbar {{
            background: white;
            box-shadow: var(--shadow);
            padding: 1rem 2rem;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }}
        
        .nav-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .logo {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--primary);
        }}
        
        .nav-links {{
            display: flex;
            list-style: none;
            gap: 2rem;
        }}
        
        .nav-links a {{
            text-decoration: none;
            color: var(--dark);
            font-weight: 500;
            transition: color 0.3s;
        }}
        
        .nav-links a:hover {{
            color: var(--primary);
        }}
        
        .hero {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 8rem 2rem 4rem;
            text-align: center;
            margin-top: 60px;
        }}
        
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        .hero p {{
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto 2rem;
        }}
        
        .btn {{
            background: white;
            color: var(--primary);
            padding: 12px 30px;
            border: none;
            border-radius: 50px;
            font-weight: 600;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }}
        
        .features {{
            max-width: 1200px;
            margin: 4rem auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}
        
        .feature-card {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: var(--shadow);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .feature-card:hover {{
            transform: translateY(-10px);
        }}
        
        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        .feature-card h3 {{
            color: var(--primary);
            margin-bottom: 1rem;
        }}
        
        footer {{
            background: var(--dark);
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 4rem;
        }}
        
        /* التجاوب المتقدم */
        @media (max-width: 768px) {{
            .nav-links {{
                display: none;
            }}
            
            .hero h1 {{
                font-size: 2rem;
            }}
            
            .hero {{
                padding: 6rem 1rem 3rem;
            }}
            
            .features {{
                grid-template-columns: 1fr;
                padding: 0 1rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            .hero h1 {{
                font-size: 1.5rem;
            }}
            
            .hero p {{
                font-size: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-content">
            <div class="logo">🚀 {title}</div>
            <ul class="nav-links">
                <li><a href="#home">الرئيسية</a></li>
                <li><a href="#features">المميزات</a></li>
                <li><a href="#about">حول</a></li>
                <li><a href="#contact">اتصل بنا</a></li>
            </ul>
        </div>
    </nav>
    
    <section class="hero" id="home">
        <h1>مرحباً بك في {title}</h1>
        <p>{description}</p>
        <a href="#features" class="btn">اكتشف المزيد</a>
    </section>
    
    <section class="features" id="features">
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>سريع</h3>
            <p>أداء فائق السرعة وتحميل فوري</p>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">📱</div>
            <h3>متجاوب</h3>
            <p>يتكيف مع جميع الأجهزة والشاشات</p>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3>آمن</h3>
            <p>حماية متقدمة لبياناتك</p>
        </div>
    </section>
    
    <footer>
        <p>تم التطوير بواسطة نظام النواة الذكية © {datetime.now().strftime("%Y")}</p>
    </footer>

    <script>
        // تفاعلات JavaScript
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🎯 التطبيق المتجاوب جاهز!');
            
            // تأثير التمرير السلس
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        target.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'start'
                        }});
                    }}
                }});
            }});
            
            // تأثير الظهور عند التمرير
            const observerOptions = {{
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            }};
            
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }}
                }});
            }}, observerOptions);
            
            // تطبيق تأثير الظهور على العناصر
            document.querySelectorAll('.feature-card').forEach(card => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(card);
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

    def _javascript_class_template(self, description: str, requirements: Dict) -> str:
        """قالب كلاس JavaScript"""
        class_name = self._extract_class_name(description) or "TaskManager"
        
        code = f'''// كلاس JavaScript: {description}

/**
 * {description}
 */
class {class_name} {{
    constructor() {{
        this.data = [];
        this.status = 'ready';
        this.initialize();
    }}
    
    initialize() {{
        console.log('🚀 تهيئة {class_name}...');
        this.status = 'initialized';
    }}
    
    /**
     * تنفيذ المهمة الرئيسية
     * @param {{*}} input - البيانات المدخلة
     * @returns {{*}} - نتيجة التنفيذ
     */
    async execute(input) {{
        try {{
            this.status = 'processing';
            console.log('🔄 جاري المعالجة...');
            
            // منطق المعالجة
            const result = await this.processData(input);
            this.data.push(result);
            
            this.status = 'completed';
            console.log('✅ تم الانتهاء من المعالجة');
            
            return result;
            
        }} catch (error) {{
            this.status = 'error';
            console.error('❌ خطأ في التنفيذ:', error);
            throw error;
        }}
    }}
    
    /**
     * معالجة البيانات
     */
    async processData(input) {{
        // محاكاة عملية غير متزامنة
        return new Promise((resolve) => {{
            setTimeout(() => {{
                const result = {{
                    input,
                    processedAt: new Date().toISOString(),
                    id: Math.random().toString(36).substr(2, 9)
                }};
                resolve(result);
            }}, 100);
        }});
    }}
    
    /**
     * الحصول على الحالة
     */
    getStatus() {{
        return this.status;
    }}
    
    /**
     * الحصول على البيانات
     */
    getData() {{
        return this.data;
    }}
    
    /**
     * مسح البيانات
     */
    clearData() {{
        this.data = [];
        console.log('🧹 تم مسح البيانات');
    }}
}}

// دوال مساعدة
const Helper = {{
    formatDate: (date = new Date()) => {{
        return date.toLocaleDateString('ar-EG');
    }},
    
    generateId: () => {{
        return Math.random().toString(36).substr(2, 9);
    }},
    
    validateData: (data) => {{
        return data && typeof data === 'object';
    }}
}};

// مثال على الاستخدام
console.log('🔧 اختبار الكلاس:');
const manager = new {class_name}();
console.log('الحالة:', manager.getStatus());

// تنفيذ مثال
manager.execute('بيانات تجريبية')
    .then(result => {{
        console.log('النتيجة:', result);
        console.log('جميع البيانات:', manager.getData());
    }})
    .catch(error => {{
        console.error('خطأ:', error);
    }});

// التصدير
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ {class_name}, Helper }};
}} else {{
    window.{class_name} = {class_name};
    window.AppHelper = Helper;
}}
'''
        return code

    def _javascript_web_template(self, description: str, requirements: Dict) -> str:
        """قالب تطبيق ويب JavaScript"""
        code = f'''// تطبيق ويب JavaScript: {description}

class WebApp {{
    constructor() {{
        this.data = [];
        this.initializeApp();
    }}
    
    initializeApp() {{
        console.log('🚀 بدء تشغيل التطبيق...');
        this.bindEvents();
        this.loadInitialData();
    }}
    
    bindEvents() {{
        // ربط الأحداث هنا
        document.addEventListener('DOMContentLoaded', () => {{
            this.onDomReady();
        }});
    }}
    
    onDomReady() {{
        console.log('✅ DOM جاهز');
        this.renderUI();
    }}
    
    loadInitialData() {{
        // تحميل البيانات الأولية
        this.data = [
            {{ id: 1, name: 'عنصر 1', value: 'قيمة 1' }},
            {{ id: 2, name: 'عنصر 2', value: 'قيمة 2' }},
            {{ id: 3, name: 'عنصر 3', value: 'قيمة 3' }}
        ];
    }}
    
    renderUI() {{
        // عرض الواجهة
        const appElement = document.getElementById('app') || this.createAppElement();
        appElement.innerHTML = this.generateHTML();
    }}
    
    createAppElement() {{
        const appDiv = document.createElement('div');
        appDiv.id = 'app';
        appDiv.style.cssText = `
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
        `;
        document.body.appendChild(appDiv);
        return appDiv;
    }}
    
    generateHTML() {{
        return `
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #4CAF50;">🚀 تطبيق ويب</h1>
                <p>{description}</p>
            </div>
            
            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px;">
                <h3>📊 البيانات:</h3>
                <div id="data-container">
                    ${{this.data.map(item => `
                        <div style="padding: 10px; margin: 5px; background: white; border-radius: 5px;">
                            <strong>${{item.name}}</strong>: ${{item.value}}
                        </div>
                    `).join('')}}
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <button onclick="app.addNewItem()" style="
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                ">إضافة عنصر جديد</button>
            </div>
        `;
    }}
    
    addNewItem() {{
        const newItem = {{
            id: this.data.length + 1,
            name: `عنصر ${{this.data.length + 1}}`,
            value: `قيمة ${{this.data.length + 1}}`
        }};
        
        this.data.push(newItem);
        this.renderUI();
        console.log('✅ تم إضافة عنصر جديد:', newItem);
    }}
    
    // دوال مساعدة
    async fetchData(url) {{
        try {{
            const response = await fetch(url);
            return await response.json();
        }} catch (error) {{
            console.error('❌ خطأ في جلب البيانات:', error);
            return null;
        }}
    }}
    
    formatDate(date = new Date()) {{
        return date.toLocaleDateString('ar-EG');
    }}
}}

// تشغيل التطبيق
const app = new WebApp();

// التصدير للاستخدام في المشاريع
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = WebApp;
}} else {{
    window.WebApp = WebApp;
}}
'''
        return code

    # ──────────────────────────────────────────────────────────────────────
    # قوالب CSS
    # ──────────────────────────────────────────────────────────────────────
    
    def _css_basic_template(self, description: str, requirements: Dict) -> str:
        """قالب CSS أساسي"""
        code = f'''/* أنماط CSS: {description} */

/* إعدادات أساسية */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}}

/* الحاوية الرئيسية */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* رأس الصفحة */
.header {{
    background: linear-gradient(135deg, #4CAF50, #45a049);
    color: white;
    padding: 40px 0;
    text-align: center;
}}

.header h1 {{
    font-size: 2.5em;
    margin-bottom: 10px;
}}

.header p {{
    font-size: 1.2em;
    opacity: 0.9;
}}

/* شبكة المحتوى */
.content-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    margin: 40px 0;
}}

/* البطاقات */
.card {{
    background: white;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    padding: 30px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}}

.card h3 {{
    color: #4CAF50;
    margin-bottom: 15px;
    font-size: 1.4em;
}}

/* الأزرار */
.btn {{
    display: inline-block;
    background: #4CAF50;
    color: white;
    padding: 12px 25px;
    border: none;
    border-radius: 5px;
    text-decoration: none;
    font-size: 1em;
    cursor: pointer;
    transition: background 0.3s ease;
}}

.btn:hover {{
    background: #45a049;
}}

.btn-secondary {{
    background: #6c757d;
}}

.btn-secondary:hover {{
    background: #5a6268;
}}

/* التذييل */
.footer {{
    background: #343a40;
    color: white;
    text-align: center;
    padding: 30px 0;
    margin-top: 50px;
}}

/* التجاوب */
@media (max-width: 768px) {{
    .header h1 {{
        font-size: 2em;
    }}
    
    .content-grid {{
        grid-template-columns: 1fr;
        gap: 20px;
    }}
    
    .card {{
        padding: 20px;
    }}
}}

/* تأثيرات متقدمة */
.fade-in {{
    animation: fadeIn 0.8s ease-in;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.slide-in {{
    animation: slideIn 0.6s ease-out;
}}

@keyframes slideIn {{
    from {{ transform: translateX(-100px); opacity: 0; }}
    to {{ transform: translateX(0); opacity: 1; }}
}}
'''
        return code

    def _css_modern_template(self, description: str, requirements: Dict) -> str:
        """قالب CSS حديث"""
        code = f'''/* أنماط CSS حديثة: {description} */

:root {{
    --primary: #4CAF50;
    --primary-dark: #45a049;
    --secondary: #2196F3;
    --accent: #FF9800;
    --dark: #2c3e50;
    --light: #ecf0f1;
    --success: #28a745;
    --warning: #ffc107;
    --danger: #dc3545;
    --shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    --radius: 12px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* إعادة الضبط المتقدمة */
*, *::before, *::after {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    line-height: 1.7;
    color: var(--dark);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}}

/* تصميم الشريط الجانبي العصري */
.sidebar {{
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: var(--radius);
    padding: 2rem;
    box-shadow: var(--shadow);
    margin: 2rem;
}}

/* البطاقات الحديثة */
.card-modern {{
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: var(--radius);
    padding: 2rem;
    box-shadow: var(--shadow);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}}

.card-modern::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
}}

.card-modern:hover {{
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}}

/* الأزرار الحديثة */
.btn-modern {{
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    padding: 12px 28px;
    border: none;
    border-radius: 50px;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}}

.btn-modern::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}}

.btn-modern:hover::before {{
    left: 100%;
}}

.btn-modern:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(76, 175, 80, 0.3);
}}

/* شبكة متقدمة */
.grid-advanced {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    padding: 2rem;
}}

/* شريط التنقل العائم */
.nav-floating {{
    position: fixed;
    top: 2rem;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 50px;
    padding: 1rem 2rem;
    box-shadow: var(--shadow);
    z-index: 1000;
    display: flex;
    gap: 2rem;
}}

.nav-floating a {{
    color: var(--dark);
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition);
    position: relative;
}}

.nav-floating a::after {{
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 0;
    height: 2px;
    background: var(--primary);
    transition: width 0.3s;
}}

.nav-floating a:hover::after {{
    width: 100%;
}}

/* تأثيرات النص */
.text-gradient {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* تحميل متحرك */
.loading-spinner {{
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

/* تموجات الأزرار */
.ripple {{
    position: relative;
    overflow: hidden;
}}

.ripple::after {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}}

.ripple:active::after {{
    width: 300px;
    height: 300px;
}}

/* تنسيقات Forms حديثة */
.form-modern {{
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: var(--radius);
    padding: 2rem;
    box-shadow: var(--shadow);
}}

.form-group {{
    margin-bottom: 1.5rem;
}}

.form-label {{
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--dark);
}}

.form-input {{
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    font-size: 1rem;
    transition: var(--transition);
    background: white;
}}

.form-input:focus {{
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}}

/* التجاوب المتقدم */
@media (max-width: 1024px) {{
    .grid-advanced {{
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        padding: 1.5rem;
    }}
}}

@media (max-width: 768px) {{
    .nav-floating {{
        flex-direction: column;
        gap: 1rem;
        border-radius: 20px;
    }}
    
    .sidebar {{
        margin: 1rem;
        padding: 1.5rem;
    }}
}}

@media (max-width: 480px) {{
    .grid-advanced {{
        grid-template-columns: 1fr;
        gap: 1rem;
        padding: 1rem;
    }}
}}
'''
        return code

    def _css_responsive_template(self, description: str, requirements: Dict) -> str:
        """قالب CSS متجاوب"""
        return self._css_modern_template(description, requirements)

    # ──────────────────────────────────────────────────────────────────────
    # قوالب SQL
    # ──────────────────────────────────────────────────────────────────────
    
    def _sql_query_template(self, description: str, requirements: Dict) -> str:
        """قالب استعلام SQL"""
        code = f'''-- استعلامات SQL: {description}

-- إنشاء قاعدة البيانات
CREATE DATABASE IF NOT EXISTS app_db;
USE app_db;

-- جدول المستخدمين
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('admin', 'user', 'moderator') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- جدول المنتجات
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT,
    stock_quantity INT DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_name (name),
    INDEX idx_category (category_id),
    INDEX idx_price (price)
);

-- جدول الفئات
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id),
    INDEX idx_parent (parent_id)
);

-- جدول الطلبات
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- استعلامات أساسية

-- 1. جلب جميع المستخدمين النشطين
SELECT 
    id,
    username,
    email,
    full_name,
    role,
    created_at
FROM users 
WHERE is_active = TRUE 
ORDER BY created_at DESC;

-- 2. جلب المنتجات المتاحة مع معلومات الفئة
SELECT 
    p.id,
    p.name,
    p.description,
    p.price,
    p.stock_quantity,
    c.name as category_name,
    p.created_at
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.is_available = TRUE 
AND p.stock_quantity > 0
ORDER BY p.created_at DESC;

-- 3. إحصائيات المبيعات
SELECT 
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as average_order_value,
    MIN(created_at) as first_order_date,
    MAX(created_at) as last_order_date
FROM orders 
WHERE status != 'cancelled';

-- 4. أفضل العملاء
SELECT 
    u.id,
    u.username,
    u.full_name,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status != 'cancelled'
GROUP BY u.id, u.username, u.full_name
ORDER BY total_spent DESC
LIMIT 10;

-- 5. المنتجات الأكثر مبيعاً
SELECT 
    p.id,
    p.name,
    COUNT(oi.id) as times_ordered,
    SUM(oi.quantity) as total_quantity_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
WHERE o.status != 'cancelled'
GROUP BY p.id, p.name
ORDER BY total_quantity_sold DESC
LIMIT 10;

-- إجراءات مخزنة

-- إضافة مستخدم جديد
DELIMITER //
CREATE PROCEDURE AddUser(
    IN p_username VARCHAR(50),
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(255),
    IN p_full_name VARCHAR(100)
)
BEGIN
    INSERT INTO users (username, email, password_hash, full_name)
    VALUES (p_username, p_email, p_password, p_full_name);
END //
DELIMITER ;

-- تحديث كمية المخزون
DELIMITER //
CREATE PROCEDURE UpdateProductStock(
    IN p_product_id INT,
    IN p_quantity_change INT
)
BEGIN
    UPDATE products 
    SET stock_quantity = stock_quantity + p_quantity_change,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_product_id;
END //
DELIMITER ;

-- عرضات (Views)

-- عرض للمنتجات مع معلومات كاملة
CREATE VIEW product_details AS
SELECT 
    p.*,
    c.name as category_name,
    c.parent_id as category_parent_id,
    CASE 
        WHEN p.stock_quantity = 0 THEN 'out_of_stock'
        WHEN p.stock_quantity < 10 THEN 'low_stock'
        ELSE 'in_stock'
    END as stock_status
FROM products p
LEFT JOIN categories c ON p.category_id = c.id;

-- عرض لإحصائيات المستخدمين
CREATE VIEW user_statistics AS
SELECT 
    u.*,
    COUNT(o.id) as total_orders,
    COALESCE(SUM(o.total_amount), 0) as total_spent,
    MAX(o.created_at) as last_order_date
FROM users u
LEFT JOIN orders o ON u.id = o.user_id AND o.status != 'cancelled'
GROUP BY u.id;
'''
        return code

    def _sql_table_template(self, description: str, requirements: Dict) -> str:
        """قالب جداول SQL"""
        return self._sql_query_template(description, requirements)

    # ──────────────────────────────────────────────────────────────────────
    # دوال مساعدة
    # ──────────────────────────────────────────────────────────────────────
    
    def _extract_function_name(self, description: str) -> str:
        """استخراج اسم دالة من الوصف"""
        words = description.split()
        for i, word in enumerate(words):
            if word in ['دالة', 'function', 'برمج', 'اكتب'] and i + 1 < len(words):
                return self._to_camel_case(words[i + 1])
        return "executeTask"
    
    def _extract_class_name(self, description: str) -> str:
        """استخراج اسم كلاس من الوصف"""
        words = description.split()
        for i, word in enumerate(words):
            if word in ['كلاس', 'class', 'نظام', 'مدير'] and i + 1 < len(words):
                return self._to_pascal_case(words[i + 1])
        return "TaskManager"
    
    def _to_camel_case(self, text: str) -> str:
        """تحويل النص إلى camelCase"""
        words = text.split()
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _to_pascal_case(self, text: str) -> str:
        """تحويل النص إلى PascalCase"""
        return ''.join(word.capitalize() for word in text.split())
    
    def _generate_title(self, description: str) -> str:
        """توليد عنوان من الوصف"""
        if len(description) <= 50:
            return description
        return description[:47] + "..."
    
    def _generate_fallback_code(self, description: str, language: str) -> Dict:
        """توليد كود بديل عندما يفشل التحليل"""
        if language == 'python':
            code = f'''# كود بديل: {description}

def main():
    """الدالة الرئيسية"""
    print("🚀 تم تنفيذ الكود بنجاح!")
    print(f"الوصف: {description}")
    
    # إضافة منطقك هنا
    result = process_data()
    print(f"النتيجة: {{result}}")

def process_data():
    """معالجة البيانات"""
    return "تمت المعالجة بنجاح"

if __name__ == "__main__":
    main()
'''
        else:
            code = f'''// كود بديل: {description}

function main() {{
    console.log("🚀 تم تنفيذ الكود بنجاح!");
    console.log(`الوصف: {description}`);
    
    // إضافة منطقك هنا
    const result = processData();
    console.log(`النتيجة: ${{result}}`);
}}

function processData() {{
    return "تمت المعالجة بنجاح";
}}

// التشغيل
main();
'''
        
        return {
            "code": code,
            "lang": language,
            "title": "كود بديل",
            "requirements": {"language": language, "complexity": "simple"},
            "validated": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_error_response(self, description: str, error: str) -> Dict:
        """توليد رد خطأ"""
        return {
            "code": f"# خطأ في توليد الكود\\n# الوصف: {description}\\n# الخطأ: {error}",
            "lang": "text",
            "title": "خطأ في التوليد",
            "requirements": {},
            "validated": False,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

# واجهة التوافق مع الإصدار السابق
def generate_code(description: str) -> Dict:
    """واجهة متوافقة مع الإصدار السابق"""
    generator = CodeGenerator()
    return generator.generate_code(description)
