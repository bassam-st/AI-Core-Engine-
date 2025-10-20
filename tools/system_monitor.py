# tools/system_monitor.py - مراقب النظام
import psutil
import platform
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.system_info = self.get_system_info()
    
    def get_system_info(self):
        """الحصول على معلومات النظام"""
        try:
            return {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor() or "غير معروف",
                "hostname": platform.node(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            }
        except:
            return {
                "platform": platform.system(),
                "platform_version": "غير معروف",
                "architecture": "غير معروف",
                "processor": "غير معروف",
                "hostname": "غير معروف",
                "boot_time": "غير معروف"
            }
    
    def get_cpu_info(self):
        """معلومات المعالج"""
        try:
            return {
                "physical_cores": psutil.cpu_count(logical=False),
                "total_cores": psutil.cpu_count(logical=True),
                "cpu_usage": psutil.cpu_percent(interval=1),
                "cpu_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "غير معروف"
            }
        except:
            return {
                "physical_cores": "غير معروف",
                "total_cores": "غير معروف",
                "cpu_usage": "غير معروف",
                "cpu_frequency": "غير معروف"
            }
    
    def get_memory_info(self):
        """معلومات الذاكرة"""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": self.bytes_to_gb(memory.total),
                "available": self.bytes_to_gb(memory.available),
                "used": self.bytes_to_gb(memory.used),
                "percentage": memory.percent
            }
        except:
            return {
                "total": "غير معروف",
                "available": "غير معروف",
                "used": "غير معروف",
                "percentage": "غير معروف"
            }
    
    def get_disk_info(self):
        """معلومات التخزين"""
        try:
            disk = psutil.disk_usage('/')
            return {
                "total": self.bytes_to_gb(disk.total),
                "used": self.bytes_to_gb(disk.used),
                "free": self.bytes_to_gb(disk.free),
                "percentage": disk.percent
            }
        except:
            return {
                "total": "غير معروف",
                "used": "غير معروف",
                "free": "غير معروف",
                "percentage": "غير معروف"
            }
    
    def get_network_info(self):
        """معلومات الشبكة"""
        try:
            network = psutil.net_io_counters()
            return {
                "bytes_sent": self.bytes_to_mb(network.bytes_sent),
                "bytes_recv": self.bytes_to_mb(network.bytes_recv),
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        except:
            return {
                "bytes_sent": "غير معروف",
                "bytes_recv": "غير معروف",
                "packets_sent": "غير معروف",
                "packets_recv": "غير معروف"
            }
    
    def get_running_processes(self, limit=10):
        """العمليات النشطة"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # ترتيب حسب استخدام CPU
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            return processes[:limit]
        except:
            return []
    
    def bytes_to_gb(self, bytes_value):
        """تحويل البايت إلى جيجابايت"""
        return round(bytes_value / (1024 ** 3), 2)
    
    def bytes_to_mb(self, bytes_value):
        """تحويل البايت إلى ميجابايت"""
        return round(bytes_value / (1024 ** 2), 2)
    
    def generate_system_report(self):
        """توليد تقرير نظام شامل"""
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        disk_info = self.get_disk_info()
        network_info = self.get_network_info()
        
        report = f"""
📊 تقرير مراقبة النظام - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🖥️ معلومات النظام:
• النظام: {self.system_info['platform']} {self.system_info['platform_version']}
• البنية: {self.system_info['architecture']}
• المعالج: {self.system_info['processor']}
• اسم الجهاز: {self.system_info['hostname']}
• وقت التشغيل: {self.system_info['boot_time']}

⚡ أداء النظام:
• استخدام المعالج: {cpu_info.get('cpu_usage', 'غير معروف')}%
• نوى فعلية: {cpu_info.get('physical_cores', 'غير معروف')}
• نوى كلية: {cpu_info.get('total_cores', 'غير معروف')}
• تردد المعالج: {cpu_info.get('cpu_frequency', 'غير معروف')} MHz

💾 الذاكرة:
• الإجمالي: {memory_info.get('total', 'غير معروف')} GB
• المستخدم: {memory_info.get('used', 'غير معروف')} GB
• المتاح: {memory_info.get('available', 'غير معروف')} GB
• النسبة: {memory_info.get('percentage', 'غير معروف')}%

💿 التخزين:
• المساحة الكلية: {disk_info.get('total', 'غير معروف')} GB
• المستخدم: {disk_info.get('used', 'غير معروف')} GB
• المتاح: {disk_info.get('free', 'غير معروف')} GB
• النسبة: {disk_info.get('percentage', 'غير معروف')}%

🌐 الشبكة:
• البيانات المرسلة: {network_info.get('bytes_sent', 'غير معروف')} MB
• البيانات المستقبلة: {network_info.get('bytes_recv', 'غير معروف')} MB
"""
        return report
