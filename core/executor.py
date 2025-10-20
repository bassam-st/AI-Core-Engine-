# core/executor.py - منفذ الأوامر الآمن
import subprocess
import os
import tempfile

class SafeExecutor:
    def __init__(self):
        self.allowed_commands = [
            'python', 'python3', 'echo', 'ls', 'pwd', 
            'whoami', 'date', 'uname', 'hostname'
        ]
    
    def execute_python_code(self, code, timeout=30):
        """تنفيذ كود Python بأمان"""
        try:
            # إنشاء ملف مؤقت
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # تنفيذ الكود
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            
            # تنظيف الملف المؤقت
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "انتهت المهلة - الكود استغرق وقتاً طويلاً",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"خطأ في التنفيذ: {e}",
                "return_code": -1
            }
    
    def execute_system_command(self, command):
        """تنفيذ أوامر النظام بأمان"""
        try:
            # التحقق من الأمان
            if not self.is_command_safe(command):
                return {
                    "success": False,
                    "output": "",
                    "error": "هذا الأمر غير مسموح به لأسباب أمنية",
                    "return_code": -1
                }
            
            # تنفيذ الأمر
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8'
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "انتهت المهلة - الأمر استغرق وقتاً طويلاً",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"خطأ في التنفيذ: {e}",
                "return_code": -1
            }
    
    def is_command_safe(self, command):
        """التحقق من أمان الأمر"""
        command_lower = command.lower()
        
        # قائمة الأوامر الخطيرة الممنوعة
        dangerous_commands = [
            'rm ', 'del ', 'format', 'mkfs', 'dd ', 'shutdown',
            'reboot', 'init', 'kill', 'chmod 777', 'passwd'
        ]
        
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return False
        
        # التحقق من الأوامر المسموحة
        for allowed in self.allowed_commands:
            if command_lower.startswith(allowed):
                return True
        
        return False
    
    def create_file(self, filename, content):
        """إنشاء ملف بأمان"""
        try:
            # التحقق من المسار الآمن
            safe_dirs = ['.', './projects', './output']
            file_dir = os.path.dirname(filename)
            
            if file_dir not in safe_dirs:
                return {
                    "success": False,
                    "message": "المسار غير مسموح به"
                }
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"تم إنشاء الملف: {filename}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"خطأ في إنشاء الملف: {e}"
            }
