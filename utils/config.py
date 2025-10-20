# utils/config.py - إعدادات التطبيق
import os
import json

class Config:
    def __init__(self):
        self.config_file = 'memory/config.json'
        self.default_config = {
            "app": {
                "name": "AI Core Engine",
                "version": "1.0.0",
                "description": "نواة ذكية متقدمة للبرمجة والشبكات والأنظمة"
            },
            "security": {
                "allowed_commands": ["python", "echo", "pwd", "ls", "whoami"],
                "max_execution_time": 30,
                "safe_directories": [".", "./projects", "./output"]
            },
            "learning": {
                "enabled": True,
                "max_memory_size": 1000,
                "auto_save_interval": 10
            },
            "ui": {
                "language": "ar",
                "theme": "dark",
                "auto_scroll": True
            }
        }
        self.load_config()
    
    def load_config(self):
        """تحميل الإعدادات"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config
                self.save_config()
        except:
            self.config = self.default_config
    
    def save_config(self):
        """حفظ الإعدادات"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get(self, key, default=None):
        """الحصول على قيمة إعداد"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
    
    def set(self, key, value):
        """تعيين قيمة إعداد"""
        keys = key.split('.')
        config_ref = self.config
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        config_ref[keys[-1]] = value
        self.save_config()
