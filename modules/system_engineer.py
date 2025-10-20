# modules/system_engineer.py - مهندس الأنظمة
import platform
import os
import psutil

class SystemEngineer:
    def __init__(self):
        self.system_info = self.get_system_info()
    
    def get_system_info(self):
        """جمع معلومات النظام"""
        try:
            return {
                'system': platform.system(),
                'version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'memory': psutil.virtual_memory().total // (1024**3),  # GB
                'disk_usage': psutil.disk_usage('/').percent
            }
        except:
            return {
                'system': platform.system(),
                'version': platform.version(),
                'architecture': 'غير معروف',
                'processor': 'غير معروف',
                'memory': 'غير معروف',
                'disk_usage': 'غير معروف'
            }
    
    def handle_system_request(self, message, analysis):
        """معالجة طلبات الأنظمة"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['معلومات', 'مواصفات', 'نظام']):
            return self.show_system_info(message)
        elif any(word in message_lower for word in ['أداء', 'استخدام', 'ذاكرة']):
            return self.show_performance(message)
        elif any(word in message_lower for word in ['إدارة', 'ملفات', 'مجلدات']):
            return self.file_management(message)
        else:
            return self.general_system_help(message)
    
    def show_system_info(self, message):
        """عرض معلومات النظام"""
        info = self.system_info
        
        info_text = f"""
🖥️ معلومات النظام:
• نظام التشغيل: {info['system']}
• الإصدار: {info['version']}
• البنية: {info['architecture']}
• المعالج: {info['processor']}
• الذاكرة: {info['memory']} GB
• استخدام التخزين: {info['disk_usage']}%
"""
        return {
            'message': info_text,
            'type': 'system_info',
            'system_info': info,
            'suggestions': ['مراقبة الأداء', 'إدارة الملفات', 'تحسين الأداء']
        }
    
    def show_performance(self, message):
        """عرض أداء النظام"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            performance_text = f"""
📊 أداء النظام الحالي:
• استخدام المعالج: {cpu_percent}%
• استخدام الذاكرة: {memory.percent}%
• الذاكرة المتاحة: {memory.available // (1024**3)} GB
• استخدام التخزين: {disk.percent}%
• المساحة الحرة: {disk.free // (1024**9)} GB
"""
            return {
                'message': performance_text,
                'type': 'performance_info',
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'suggestions': ['تحسين الأداء', 'تنظيف الذاكرة', 'إدارة العمليات']
            }
            
        except Exception as e:
            return {
                'message': f"❌ تعذر الحصول على معلومات الأداء: {e}",
                'type': 'error',
                'suggestions': ['محاولة أخرى', 'التحقق من صلاحيات النظام']
            }
    
    def file_management(self, message):
        """إدارة الملفات"""
        current_dir = os.getcwd()
        files = os.listdir('.')
        
        # عرض الملفات والمجلدات فقط
        items = []
        for item in files[:10]:  # أول 10 عناصر فقط
            if os.path.isdir(item):
                items.append(f"📁 {item}/")
            else:
                items.append(f"📄 {item}")
        
        files_list = "\n".join(items)
        
        return {
            'message': f"📂 إدارة الملفات:\nالمسار الحالي: {current_dir}\n\nالمحتويات:\n{files_list}",
            'type': 'file_management',
            'current_directory': current_dir,
            'file_count': len(files),
            'suggestions': ['عرض المزيد', 'إنشاء مجلد', 'إنشاء ملف']
        }
    
    def general_system_help(self, message):
        """مساعدة نظامية عامة"""
        return {
            'message': "⚙️ مساعدة نظامية! أستطيع:\n• عرض معلومات النظام\n• مراقبة الأداء\n• إدارة الملفات\n• تقديم نصائح الصيانة\n\nما الذي تحتاجه؟",
            'type': 'system_help',
            'suggestions': ['عرض مواصفات النظام', 'مراقبة الأداء', 'إدارة الملفات']
        }
