# tools/file_manager.py - مدير الملفات
import os
import json
from datetime import datetime

class FileManager:
    def __init__(self):
        self.base_dirs = ['.', './projects', './knowledge', './memory']
        self.setup_directories()
    
    def setup_directories(self):
        """إنشاء المجلدات الأساسية"""
        for directory in self.base_dirs:
            os.makedirs(directory, exist_ok=True)
    
    def create_file(self, filepath, content, file_type="text"):
        """إنشاء ملف جديد"""
        try:
            # التحقق من المسار الآمن
            if not self.is_safe_path(filepath):
                return {
                    "success": False,
                    "message": "❌ المسار غير مسموح به لأسباب أمنية"
                }
            
            # التأكد من وجود المجلد
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # كتابة المحتوى
            with open(filepath, 'w', encoding='utf-8') as f:
                if file_type == "json":
                    json.dump(content, f, ensure_ascii=False, indent=2)
                else:
                    f.write(content)
            
            return {
                "success": True,
                "message": f"✅ تم إنشاء الملف: {filepath}",
                "filepath": filepath,
                "size": len(str(content))
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ خطأ في إنشاء الملف: {e}"
            }
    
    def read_file(self, filepath):
        """قراءة ملف"""
        try:
            if not os.path.exists(filepath):
                return {
                    "success": False,
                    "message": f"❌ الملف غير موجود: {filepath}"
                }
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "filepath": filepath,
                "size": len(content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ خطأ في قراءة الملف: {e}"
            }
    
    def list_directory(self, directory="."):
        """عرض محتويات المجلد"""
        try:
            if not self.is_safe_path(directory):
                return {
                    "success": False,
                    "message": "❌ المسار غير مسموح به"
                }
            
            items = os.listdir(directory)
            files = []
            folders = []
            
            for item in items:
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    folders.append({
                        "name": item,
                        "type": "directory",
                        "path": item_path
                    })
                else:
                    files.append({
                        "name": item,
                        "type": "file",
                        "path": item_path,
                        "size": os.path.getsize(item_path)
                    })
            
            return {
                "success": True,
                "directory": directory,
                "folders": folders,
                "files": files,
                "total_items": len(items)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ خطأ في عرض المجلد: {e}"
            }
    
    def create_project_structure(self, project_name, project_type="web"):
        """إنشاء هيكل مشروع"""
        structures = {
            "web": {
                f"{project_name}/app.py": "from flask import Flask\\napp = Flask(__name__)\\n\\n@app.route('/')\\ndef home():\\n    return 'مرحباً!'\\n\\nif __name__ == '__main__':\\n    app.run(debug=True)",
                f"{project_name}/templates/index.html": "<!DOCTYPE html>\\n<html>\\n<head>\\n    <title>مشروعي</title>\\n</head>\\n<body>\\n    <h1>مرحباً!</h1>\\n</body>\\n</html>",
                f"{project_name}/static/css/style.css": "body { font-family: Arial; }",
                f"{project_name}/requirements.txt": "flask==2.3.3"
            },
            "data": {
                f"{project_name}/main.py": "import pandas as pd\\nimport numpy as np\\n\\n# كود تحليل البيانات\\nprint('مشروع تحليل البيانات')",
                f"{project_name}/data/": "",
                f"{project_name}/notebooks/": "",
                f"{project_name}/requirements.txt": "pandas==1.5.3\\nnumpy==1.24.3"
            },
            "automation": {
                f"{project_name}/main.py": "import os\\nimport time\\n\\n# سكريبت الأتمتة\\nprint('مشروع الأتمتة')",
                f"{project_name}/config.json": "{}",
                f"{project_name}/utils.py": "# أدوات مساعدة",
                f"{project_name}/requirements.txt": "requests==2.31.0"
            }
        }
        
        structure = structures.get(project_type, {})
        results = []
        
        for filepath, content in structure.items():
            if filepath.endswith('/'):  # مجلد
                os.makedirs(filepath, exist_ok=True)
                results.append(f"📁 تم إنشاء مجلد: {filepath}")
            else:  # ملف
                result = self.create_file(filepath, content)
                if result["success"]:
                    results.append(f"📄 تم إنشاء ملف: {filepath}")
                else:
                    results.append(f"❌ فشل إنشاء: {filepath}")
        
        return {
            "success": True,
            "project_name": project_name,
            "project_type": project_type,
            "created_items": results
        }
    
    def is_safe_path(self, path):
        """التحقق من أمان المسار"""
        # منع المسارات الخطيرة
        dangerous_paths = ['/', '/etc', '/var', '/usr', '/sys', '/proc']
        for dangerous in dangerous_paths:
            if path.startswith(dangerous):
                return False
        
        # التأكد من أن المسار ضمن المجلدات المسموحة
        for base_dir in self.base_dirs:
            if path.startswith(base_dir):
                return True
        
        return path.startswith('.')  # السماح بالمسارات النسبية فقط
