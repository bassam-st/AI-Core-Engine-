# core/brain.py
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import importlib

from .analyzer import AdvancedAnalyzer
from .learner import AdaptiveLearner
from .coder import CodeGenerator
from .executor import SafeExecutor

class AICoreBrain:
    def __init__(self):
        self.analyzer = AdvancedAnalyzer()
        self.learner = AdaptiveLearner()
        self.coder = CodeGenerator()
        self.executor = SafeExecutor()
        self.setup_modules()
        
    def setup_modules(self):
        """تحميل الوحدات المتخصصة"""
        self.modules = {}
        modules_list = [
            'network_engineer',
            'system_engineer', 
            'code_developer',
            'security_analyst',
            'project_manager'
        ]
        
        for module_name in modules_list:
            try:
                module = importlib.import_module(f'modules.{module_name}')
                self.modules[module_name] = getattr(module, module_name.title().replace('_', ''))()
            except Exception as e:
                logging.warning(f"تعذر تحميل الوحدة {module_name}: {e}")
    
    def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """معالجة الرسالة الرئيسية"""
        # تحليل متقدم للرسالة
        analysis = self.analyzer.analyze(message, user_id)
        
        # التعلم من الرسالة
        self.learner.learn_from_message(message, analysis, user_id)
        
        # توجيه الرسالة للوحدة المناسبة
        response = self.route_to_module(message, analysis, user_id)
        
        return response
    
    def route_to_module(self, message: str, analysis: Dict, user_id: str) -> Dict[str, Any]:
        """توجيه الرسالة للوحدة المتخصصة المناسبة"""
        intent = analysis.get('intent', 'general')
        
        if intent == 'code_generation':
            return self.modules['code_developer'].handle_code_request(message, analysis)
        
        elif intent == 'network_management':
            return self.modules['network_engineer'].handle_network_request(message, analysis)
        
        elif intent == 'system_administration':
            return self.modules['system_engineer'].handle_system_request(message, analysis)
        
        elif intent == 'security_analysis':
            return self.modules['security_analyst'].handle_security_request(message, analysis)
        
        elif intent == 'project_management':
            return self.modules['project_manager'].handle_project_request(message, analysis)
        
        else:
            return self.generate_general_response(message, analysis)
    
    def generate_general_response(self, message: str, analysis: Dict) -> Dict[str, Any]:
        """توليد رد عام"""
        # هنا يمكنك إضافة منطق الرد الذكي العام
        response = {
            'message': f"أفهم أنك تطلب: {message}. دعني أساعدك في ذلك...",
            'type': 'general',
            'suggestions': [
                "هل تريد مساعدة في البرمجة؟",
                "هل تحتاج لتحليل شبكة؟", 
                "هل تريد مساعدة في إدارة النظام؟"
            ]
        }
        return response
    
    def generate_code(self, requirements: str, language: str = 'python') -> Dict[str, Any]:
        """توليد كود متقدم"""
        return self.coder.generate(requirements, language)
    
    def analyze_system(self, system_type: str) -> Dict[str, Any]:
        """تحليل النظام"""
        return self.modules['system_engineer'].analyze_system(system_type)
    
    def network_scan(self, target: str) -> Dict[str, Any]:
        """مسح الشبكة"""
        return self.modules['network_engineer'].scan_network(target)
    
    def create_project(self, project_name: str, project_type: str) -> Dict[str, Any]:
        """إنشاء مشروع"""
        return self.modules['project_manager'].create_project(project_name, project_type)
