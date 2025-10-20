# core/coder.py - مولد الأكواد
import json
import os

class CodeGenerator:
    def __init__(self):
        self.templates = self.load_templates()
    
    def load_templates(self):
        """تحميل قوالب الأكواد"""
        templates = {
            "python": {
                "web_app": """from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', title='الصفحة الرئيسية')

@app.route('/about')
def about():
    return render_template('about.html', title='من نحن')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)""",

                "data_analysis": """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# تحميل البيانات
def load_data(file_path):
    return pd.read_csv(file_path)

# تحليل البيانات
def analyze_data(df):
    print("معلومات البيانات:")
    print(df.info())
    print("\\nالإحصائيات:")
    print(df.describe())
    return df

# تصور البيانات
def visualize_data(df):
    plt.figure(figsize=(10, 6))
    df.plot()
    plt.title('تحليل البيانات')
    plt.show()

if __name__ == '__main__':
    data = load_data('data.csv')
    analyzed_data = analyze_data(data)
    visualize_data(analyzed_data)""",

                "automation": """import os
import time
from datetime import datetime

class AutomationScript:
    def __init__(self):
        self.log_file = 'automation_log.txt'
    
    def log_action(self, action):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {action}\\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(log_entry.strip())
    
    def backup_files(self, source_dir, backup_dir):
        self.log_action(f'بدء نسخ احتياطي من {source_dir} إلى {backup_dir}')
        # كود النسخ الاحتياطي هنا
        self.log_action('اكتمل النسخ الاحتياطي')

if __name__ == '__main__':
    automator = AutomationScript()
    automator.backup_files('./data', './backup')"""
            },
            "html": {
                "basic_website": """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>موقعي الإلكتروني</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        header {
            background: #2c3e50;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
    </style>
</head>
<body>
    <header>
        <h1>مرحباً بك في موقعي</h1>
    </header>
    
    <div class="container">
        <h2>الصفحة الرئيسية</h2>
        <p>هذا موقع إلكتروني تم إنشاؤه باستخدام النواة الذكية</p>
    </div>
</body>
</html>"""
            },
            "bash": {
                "system_info": """#!/bin/bash

# سكريبت لجمع معلومات النظام
echo "=== معلومات النظام ==="
echo "اسم المستخدم: $(whoami)"
echo "اسم الجهاز: $(hostname)"
echo "نظام التشغيل: $(uname -s)"
echo "الإصدار: $(uname -r)"
echo "المعالج: $(uname -p)"

echo "=== استخدام الذاكرة ==="
free -h

echo "=== استخدام التخزين ==="
df -h

echo "=== معلومات الشبكة ==="
ifconfig | grep inet"""
            }
        }
        return templates
    
    def generate(self, requirements, language="python"):
        """توليد كود بناءً على المتطلبات"""
        requirements_lower = requirements.lower()
        
        # تحديد نوع الكود المطلوب
        code_type = self.detect_code_type(requirements_lower, language)
        
        # توليد الكود
        if language in self.templates and code_type in self.templates[language]:
            code = self.templates[language][code_type]
        else:
            code = self.generate_custom_code(requirements, language)
        
        explanation = self.generate_explanation(requirements, language, code_type)
        
        return {
            "code": code,
            "explanation": explanation,
            "language": language,
            "type": code_type
        }
    
    def detect_code_type(self, requirements, language):
        """اكتشاف نوع الكود المطلوب"""
        if language == "python":
            if any(word in requirements for word in ["ويب", "موقع", "فلاسك", "web"]):
                return "web_app"
            elif any(word in requirements for word in ["بيانات", "تحليل", "data"]):
                return "data_analysis"
            else:
                return "automation"
        
        elif language == "html":
            return "basic_website"
        
        elif language == "bash":
            return "system_info"
        
        return "basic"
    
    def generate_custom_code(self, requirements, language):
        """توليد كود مخصص"""
        if language == "python":
            return f'''# 🐍 كود Python مخصص
# المتطلبات: {requirements}

def main():
    """الدالة الرئيسية"""
    print("مرحباً! هذا كود Python مخصص")
    print("المتطلبات: {requirements}")
    
    # أضف منطقك هنا
    # TODO: تنفيذ المتطلبات المحددة

if __name__ == "__main__":
    main()'''
        
        else:
            return f"# كود {language} للمتطلبات: {requirements}"
    
    def generate_explanation(self, requirements, language, code_type):
        """توليد شرح للكود"""
        explanations = {
            "python": {
                "web_app": "هذا كود لتطبيق ويب باستخدام Flask مع صفحتين رئيسيتين",
                "data_analysis": "كود لتحليل البيانات باستخدام Pandas و Matplotlib",
                "automation": "سكريبت أتمتة مع نظام تسجيل المهام"
            },
            "html": "هيكل HTML أساسي لموقع ويب بتصميم متجاوب",
            "bash": "سكريبت Bash لجمع معلومات النظام"
        }
        
        return explanations.get(language, {}).get(code_type, 
               f"كود {language} للمتطلبات: {requirements}")
