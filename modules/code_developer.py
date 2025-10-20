# modules/code_developer.py - مطور الأكواد
import os
from datetime import datetime

class CodeDeveloper:
    def __init__(self):
        self.supported_languages = ['python', 'html', 'javascript', 'bash']
    
    def handle_code_request(self, message, analysis):
        """معالجة طلبات البرمجة"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['أنشئ', 'اكتب', 'اصنع', 'مشروع']):
            return self.create_project(message)
        elif any(word in message_lower for word in ['سكريبت', 'برنامج', 'كود']):
            return self.generate_script(message)
        elif any(word in message_lower for word in ['خطأ', 'مشكلة', 'إصلاح']):
            return self.debug_code(message)
        else:
            return self.general_programming_help(message)
    
    def create_project(self, message):
        """إنشاء مشروع جديد"""
        project_types = {
            'ويب': 'web',
            'موقع': 'web', 
            'تحليل': 'data',
            'بيانات': 'data',
            'أتمتة': 'automation'
        }
        
        project_type = 'web'
        for key, value in project_types.items():
            if key in message:
                project_type = value
                break
        
        project_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # إنشاء هيكل المشروع
        project_structure = self.generate_project_structure(project_name, project_type)
        
        return {
            'message': f"🚀 تم إنشاء مشروع {project_type} جديد!\nاسم المشروع: {project_name}",
            'type': 'project_creation',
            'project_name': project_name,
            'project_type': project_type,
            'structure': project_structure,
            'suggestions': ['عرض الملفات', 'تشغيل المشروع', 'تعديل الكود']
        }
    
    def generate_project_structure(self, project_name, project_type):
        """توليد هيكل المشروع"""
        if project_type == 'web':
            return {
                'files': {
                    f'{project_name}/app.py': '# تطبيق ويب باستخدام Flask',
                    f'{project_name}/templates/index.html': '# الصفحة الرئيسية',
                    f'{project_name}/static/css/style.css': '# التصاميم',
                    f'{project_name}/requirements.txt': 'flask==2.3.3'
                }
            }
        elif project_type == 'data':
            return {
                'files': {
                    f'{project_name}/analysis.py': '# تحليل البيانات',
                    f'{project_name}/data.csv': '# بيانات المثال',
                    f'{project_name}/visualization.py': '# تصور البيانات'
                }
            }
        else:
            return {
                'files': {
                    f'{project_name}/main.py': '# السكريبت الرئيسي',
                    f'{project_name}/config.json': '# الإعدادات',
                    f'{project_name}/utils.py': '# الأدوات المساعدة'
                }
            }
    
    def generate_script(self, message):
        """توليد سكريبت"""
        language = 'python'
        if 'html' in message:
            language = 'html'
        elif 'bash' in message:
            language = 'bash'
        
        script_purpose = "أتمتة المهام"
        if 'ويب' in message:
            script_purpose = "تطبيق ويب"
        elif 'بيانات' in message:
            script_purpose = "تحليل البيانات"
        
        return {
            'message': f"📝 تم إنشاء سكريبت {language} لـ {script_purpose}",
            'type': 'script_generation',
            'language': language,
            'purpose': script_purpose,
            'suggestions': ['تعديل الكود', 'تشغيل السكريبت', 'حفظ الملف']
        }
    
    def debug_code(self, message):
        """مساعدة في تصحيح الأخطاء"""
        return {
            'message': "🔧 سأساعدك في تصحيح الأخطاء! أرسل لي الكود الذي يواجه مشكلة وسأحللها.",
            'type': 'debugging_help',
            'suggestions': ['تحليل خطأ Python', 'فحص كود HTML', 'مراجعة السكريبت']
        }
    
    def general_programming_help(self, message):
        """مساعدة برمجية عامة"""
        return {
            'message': "💻 مساعدة برمجية! أستطيع:\n• إنشاء مشاريع جديدة\n• كتابة سكريبتات\n• تصحيح الأخطاء\n• شرح المفاهيم\n\nما الذي تحتاجه؟",
            'type': 'programming_help',
            'suggestions': ['إنشاء مشروع ويب', 'سكريبت تحليل بيانات', 'تصحيح كود Python']
        }
