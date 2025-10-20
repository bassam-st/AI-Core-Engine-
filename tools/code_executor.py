# tools/code_executor.py - منفذ الأكواد الآمن
import subprocess
import tempfile
import os
import sys

class CodeExecutor:
    def __init__(self):
        self.allowed_modules = [
            'os', 'sys', 'math', 'datetime', 'json', 
            'random', 'time', 're', 'collections'
        ]
    
    def execute_python_code(self, code, timeout=30):
        """تنفيذ كود Python بأمان"""
        try:
            # فحص الكود بحث عن عمليات خطيرة
            safety_check = self.check_code_safety(code)
            if not safety_check["safe"]:
                return {
                    "success": False,
                    "output": "",
                    "error": f"❌ الكود يحتوي على عمليات غير مسموحة: {safety_check['reason']}",
                    "execution_time": 0
                }
            
            # إنشاء ملف مؤقت
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write("#!/usr/bin/env python3\n")
                f.write("# -*- coding: utf-8 -*-\n\n")
                f.write(code)
                temp_file = f.name
            
            # تنفيذ الكود
            start_time = os.times().elapsed
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            execution_time = os.times().elapsed - start_time
            
            # تنظيف الملف المؤقت
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": round(execution_time, 2),
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "⏰ انتهت المهلة - الكود استغرق وقتاً طويلاً في التنفيذ",
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"❌ خطأ في التنفيذ: {e}",
                "execution_time": 0
            }
    
    def check_code_safety(self, code):
        """فحص أمان الكود"""
        dangerous_patterns = [
            (r'__import__\s*\(', 'استيراد ديناميكي'),
            (r'eval\s*\(', 'دالة eval'),
            (r'exec\s*\(', 'دالة exec'),
            (r'open\s*\([^)]*w[^)]*\)', 'فتح ملف للكتابة'),
            (r'os\.system\s*\(', 'أوامر النظام'),
            (r'subprocess\s*\.', 'عمليات فرعية'),
            (r'import\s+os\s*$', 'استيراد os'),
            (r'import\s+sys\s*$', 'استيراد sys'),
        ]
        
        code_lines = code.split('\n')
        
        for pattern, reason in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return {"safe": False, "reason": reason}
        
        # فحص الاستيرادات
        for line in code_lines:
            if line.strip().startswith('import '):
                module = line.split()[1].split('.')[0]
                if module not in self.allowed_modules:
                    return {"safe": False, "reason": f"استيراد {module}"}
            
            elif line.strip().startswith('from '):
                module = line.split()[1]
                if module not in self.allowed_modules:
                    return {"safe": False, "reason": f"استيراد {module}"}
        
        return {"safe": True, "reason": "الكود آمن"}
    
    def execute_system_command(self, command, timeout=10):
        """تنفيذ أوامر النظام بأمان"""
        try:
            # قائمة الأوامر المسموحة
            allowed_commands = [
                'python', 'python3', 'echo', 'pwd', 'ls', 
                'whoami', 'date', 'uname', 'hostname'
            ]
            
            # التحقق من الأمر
            command_base = command.split()[0]
            if command_base not in allowed_commands:
                return {
                    "success": False,
                    "output": "",
                    "error": f"❌ الأمر غير مسموح به: {command_base}",
                    "execution_time": 0
                }
            
            # تنفيذ الأمر
            start_time = os.times().elapsed
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            execution_time = os.times().elapsed - start_time
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": round(execution_time, 2),
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "⏰ انتهت المهلة - الأمر استغرق وقتاً طويلاً",
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"❌ خطأ في التنفيذ: {e}",
                "execution_time": 0
            }

# إضافة استيراد re المفقود
import re
