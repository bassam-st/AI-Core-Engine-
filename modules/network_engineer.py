# modules/network_engineer.py - مهندس الشبكات
import socket
import subprocess
import platform

class NetworkEngineer:
    def __init__(self):
        self.network_concepts = {
            'tcp': 'بروتوكول التحكم في الإرسال - اتصال موثوق يضمن وصول البيانات',
            'udp': 'بروتوكول بيانات المستخدم - اتصال سريع بدون تأكيد الاستلام',
            'ip': 'بروتوكول الإنترنت - عنوان فريد لكل جهاز على الشبكة',
            'dns': 'نظام اسم النطاق - يحول الأسماء إلى عناوين IP',
            'router': 'جهاز يوجه البيانات بين الشبكات المختلفة',
            'switch': 'جهاز يربط الأجهزة في نفس الشبكة المحلية'
        }
    
    def handle_network_request(self, message, analysis):
        """معالجة طلبات الشبكات"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['اشرح', 'ما هو', 'مفهوم']):
            return self.explain_concept(message)
        elif any(word in message_lower for word in ['مسح', 'فحص', 'scan']):
            return self.scan_network(message)
        elif any(word in message_lower for word in ['ping', 'اتصال', 'انترنت']):
            return self.test_connection(message)
        else:
            return self.general_network_help(message)
    
    def explain_concept(self, message):
        """شرح مفهوم شبكي"""
        for concept, explanation in self.network_concepts.items():
            if concept in message.lower():
                return {
                    'message': f"🌐 شرح {concept.upper()}:\n{explanation}",
                    'type': 'concept_explanation',
                    'concept': concept,
                    'suggestions': [f'مثال على {concept}', 'كيف يعمل', 'مشاكل شائعة']
                }
        
        # إذا لم يتم العثور على مفهوم محدد
        concepts_list = "\n".join([f"• {concept.upper()}" for concept in self.network_concepts.keys()])
        return {
            'message': f"📚 المفاهيم الشبكية المتاحة:\n{concepts_list}\n\nأي مفهوم تريد شرحه؟",
            'type': 'concepts_list',
            'suggestions': ['شرح TCP', 'شرح DNS', 'شرح IP']
        }
    
    def scan_network(self, message):
        """مسح الشبكة"""
        try:
            # الحصول على عنوان IP المحلي
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            network_info = {
                'hostname': hostname,
                'local_ip': local_ip,
                'platform': platform.system()
            }
            
            return {
                'message': f"🔍 معلومات الشبكة:\n• اسم الجهاز: {hostname}\n• IP محلي: {local_ip}\n• النظام: {platform.system()}",
                'type': 'network_scan',
                'network_info': network_info,
                'suggestions': ['فحص الاتصال بالإنترنت', 'معلومات الشبكة المتقدمة', 'فحص المنافذ']
            }
            
        except Exception as e:
            return {
                'message': f"❌ تعذر مسح الشبكة: {e}",
                'type': 'error',
                'suggestions': ['محاولة أخرى', 'فحص إعدادات الشبكة']
            }
    
    def test_connection(self, message):
        """اختبار الاتصال"""
        try:
            # اختبار الاتصال بالإنترنت
            target = "8.8.8.8"  # DNS Google
            if "جوجل" in message or "google" in message.lower():
                target = "google.com"
            
            # استخدام ping (يعتمد على النظام)
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "2", target]
            else:
                cmd = ["ping", "-c", "2", target]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                status = "✅ الاتصال نشط"
            else:
                status = "❌ مشكلة في الاتصال"
            
            return {
                'message': f"🌐 اختبار الاتصال:\nالهدف: {target}\nالحالة: {status}",
                'type': 'connection_test',
                'target': target,
                'status': status,
                'suggestions': ['اختبار مواقع أخرى', 'فحص DNS', 'تحليل الشبكة']
            }
            
        except Exception as e:
            return {
                'message': f"❌ تعذر اختبار الاتصال: {e}",
                'type': 'error',
                'suggestions': ['محاولة أخرى', 'فحص الإعدادات']
            }
    
    def general_network_help(self, message):
        """مساعدة شبكية عامة"""
        return {
            'message': "🛜 مساعدة شبكية! أستطيع:\n• شرح مفاهيم الشبكات\n• فحص اتصال الشبكة\n• تحليل مشاكل الاتصال\n• تقديم نصائح أمنية\n\nما الذي تحتاجه؟",
            'type': 'network_help',
            'suggestions': ['شرح TCP/IP', 'فحص اتصال الإنترنت', 'تحليل مشكلة شبكية']
        }
