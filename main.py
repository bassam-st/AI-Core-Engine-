#!/usr/bin/env python3
# النواة الذكية المتقدمة - AI Core Engine
# نظام متكامل للذكاء الاصطناعي، البرمجة، الشبكات، والأنظمة

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template

# إضافة المسارات للمشروع
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from core.brain import AICoreBrain
from utils.logger import setup_logging

app = Flask(__name__)
ai_core = AICoreBrain()

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """واجهة المحادثة مع النواة الذكية"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'لا يوجد رسالة'}), 400
        
        # معالجة الرسالة عبر النواة الذكية
        response = ai_core.process_message(user_message, user_id)
        
        return jsonify({
            'response': response['message'],
            'type': response['type'],
            'suggestions': response.get('suggestions', []),
            'code': response.get('code', ''),
            'execution_result': response.get('execution_result', '')
        })
        
    except Exception as e:
        logging.error(f"خطأ في معالجة الرسالة: {e}")
        return jsonify({'error': 'حدث خطأ في المعالجة'}), 500

@app.route('/api/code/generate', methods=['POST'])
def generate_code():
    """توليد كود بناءً على الطلب"""
    try:
        data = request.get_json()
        requirements = data.get('requirements', '')
        language = data.get('language', 'python')
        
        code = ai_core.generate_code(requirements, language)
        
        return jsonify({
            'code': code['code'],
            'explanation': code['explanation'],
            'language': code['language']
        })
        
    except Exception as e:
        logging.error(f"خطأ في توليد الكود: {e}")
        return jsonify({'error': 'حدث خطأ في توليد الكود'}), 500

@app.route('/api/system/analyze', methods=['POST'])
def analyze_system():
    """تحليل النظام"""
    try:
        data = request.get_json()
        system_type = data.get('system_type', 'general')
        
        analysis = ai_core.analyze_system(system_type)
        
        return jsonify(analysis)
        
    except Exception as e:
        logging.error(f"خطأ في تحليل النظام: {e}")
        return jsonify({'error': 'حدث خطأ في تحليل النظام'}), 500

@app.route('/api/network/scan', methods=['POST'])
def network_scan():
    """مسح الشبكة"""
    try:
        data = request.get_json()
        target = data.get('target', 'localhost')
        
        scan_result = ai_core.network_scan(target)
        
        return jsonify(scan_result)
        
    except Exception as e:
        logging.error(f"خطأ في مسح الشبكة: {e}")
        return jsonify({'error': 'حدث خطأ في مسح الشبكة'}), 500

@app.route('/api/project/create', methods=['POST'])
def create_project():
    """إنشاء مشروع جديد"""
    try:
        data = request.get_json()
        project_name = data.get('project_name', '')
        project_type = data.get('project_type', 'web')
        
        project = ai_core.create_project(project_name, project_type)
        
        return jsonify(project)
        
    except Exception as e:
        logging.error(f"خطأ في إنشاء المشروع: {e}")
        return jsonify({'error': 'حدث خطأ في إنشاء المشروع'}), 500

if __name__ == '__main__':
    setup_logging()
    logging.info("🚀 تشغيل النواة الذكية المتقدمة...")
    app.run(host='0.0.0.0', port=5000, debug=False)
