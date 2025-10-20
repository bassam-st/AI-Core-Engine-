# modules/network_engineer.py
import socket
import subprocess
import logging
from typing import Dict, List, Any

class NetworkEngineer:
    def __init__(self):
        self.knowledge_base = self.load_network_knowledge()
    
    def load_network_knowledge(self) -> Dict:
        """تحميل معرفة الشبكات"""
        return {
            "protocols": ["TCP", "UDP", "HTTP", "HTTPS", "FTP", "SSH"],
            "tools": ["ping", "traceroute", "nmap", "wireshark", "iptables"],
            "concepts": ["IP Addressing", "Subnetting", "Routing", "Switching", "DNS"]
        }
    
    def handle_network_request(self, message: str, analysis: Dict) -> Dict[str, Any]:
        """معالجة طلبات الشبكات"""
        if "مسح" in message or "scan" in message.lower():
            return self.handle_network_scan(message)
        elif "ping" in message.lower():
            return self.handle_ping_test(message)
        elif "شبكة" in message or "network" in message.lower():
            return self.explain_network_concept(message)
        else:
            return self.general_network_help(message)
    
    def handle_network_scan(self, message: str) -> Dict[str, Any]:
        """معالجة مسح الشبكة"""
        try:
            # استخراج الهدف من الرسالة
            target = "localhost"
            if "localhost" not in message and "127.0.0.1" not in message:
                # محاولة استخراج عنوان IP أو نطاق
                words = message.split()
                for word in words:
                    if '.' in word and any(c.isdigit() for c in word):
                        target = word
                        break
            
            result = subprocess.run(['nmap', '-sP', target], 
                                  capture_output=True, text=True, timeout=30)
            
            return {
                'message': f"نتيجة مسح الشبكة لـ {target}:",
                'type': 'network_scan',
                'scan_result': result.stdout,
                'suggestions': ["مسح مفصل", "فحص المنافذ", "تحليل الأمان"]
            }
            
        except Exception as e:
            logging.error(f"خطأ في مسح الشبكة: {e}")
            return {
                'message': f"تعذر مسح الشبكة: {e}",
                'type': 'error'
            }
    
    def handle_ping_test(self, message: str) -> Dict[str, Any]:
        """اختبار ping"""
        try:
            target = "google.com"
            words = message.split()
            for word in words:
                if '.' in word:
                    target = word
                    break
            
            result = subprocess.run(['ping', '-c', '4', target], 
                                  capture_output=True, text=True, timeout=10)
            
            return {
                'message': f"نتيجة ping لـ {target}:",
                'type': 'ping_test',
                'ping_result': result.stdout,
                'suggestions': ["مسح الشبكة", "فحص الاتصال", "تحليل الأداء"]
            }
            
        except Exception as e:
            logging.error(f"خطأ في اختبار ping: {e}")
            return {
                'message': f"تعذر إجراء اختبار ping: {e}",
                'type': 'error'
            }
    
    def explain_network_concept(self, message: str) -> Dict[str, Any]:
        """شرح مفهوم شبكي"""
        concepts = {
            "tcp": "بروتوكول التحكم في الإرسال - يوصل اتصال موثوق بين التطبيقات",
            "udp": "بروتوكول بيانات المستخدم - غير موثوق لكن سريع للمكالمات الصوتية والفيديو",
            "dns": "نظام اسم النطاق - يحول أسماء النطاقات إلى عناوين IP",
            "ip": "بروتوكول الإنترنت - عنوان فريد لكل جهاز على الشبكة",
            "subnet": "تقسيم الشبكة إلى أجزاء أصغر لإدارة أفضل"
        }
        
        for concept, explanation in concepts.items():
            if concept in message.lower():
                return {
                    'message': f"شرح {concept.upper()}: {explanation}",
                    'type': 'concept_explanation',
                    'suggestions': [f"مثال عملي لـ {concept}", "أدوات مرتبطة", "مشاكل شائعة"]
                }
        
        return {
            'message': "أستطيع شرح مفاهيم الشبكات مثل TCP, UDP, DNS, IP, Subnet. أي مفهوم تريد شرحه؟",
            'type': 'general_help',
            'suggestions': ["شرح TCP", "شرح DNS", "شرح Subnet"]
        }
    
    def general_network_help(self, message: str) -> Dict[str, Any]:
        """مساعدة عامة في الشبكات"""
        return {
            'message': "أنا هنا لمساعدتك في مواضيع الشبكات. يمكنني:\n- مسح الشبكات\n- اختبار الاتصال\n- شرح المفاهيم\n- تحليل مشاكل الشبكة",
            'type': 'general_help',
            'suggestions': ["مسح شبكة محلية", "اختبار ping", "شرح TCP/IP", "تحليل أداء الشبكة"]
        }
