# app/utils/alerts.py
from typing import List, Dict
from ..utils.config import config

class AlertSystem:
    def __init__(self):
        self.cpu_threshold = config.get('monitoring.thresholds.cpu', 90)
        self.memory_threshold = config.get('monitoring.thresholds.memory', 85)
        self.disk_threshold = config.get('monitoring.thresholds.disk', 85)
    
    def check_metrics(self, metrics: Dict) -> List[Dict]:
        alerts = []
        
        # Check CPU Usage
        if metrics['cpu_usage'] > self.cpu_threshold:
            alerts.append({
                'level': 'danger',
                'message': f"CPU usage is critical: {metrics['cpu_usage']}%"
            })
        elif metrics['cpu_usage'] > self.cpu_threshold * 0.8:
            alerts.append({
                'level': 'warning',
                'message': f"CPU usage is high: {metrics['cpu_usage']}%"
            })
        
        # Check Memory Usage
        if metrics['memory_usage'] > self.memory_threshold:
            alerts.append({
                'level': 'danger',
                'message': f"Memory usage is critical: {metrics['memory_usage']}%"
            })
        elif metrics['memory_usage'] > self.memory_threshold * 0.8:
            alerts.append({
                'level': 'warning',
                'message': f"Memory usage is high: {metrics['memory_usage']}%"
            })
        
        # Check Disk Usage
        if metrics['disk_usage'] > self.disk_threshold:
            alerts.append({
                'level': 'danger',
                'message': f"Disk usage is critical: {metrics['disk_usage']}%"
            })
        elif metrics['disk_usage'] > self.disk_threshold * 0.8:
            alerts.append({
                'level': 'warning',
                'message': f"Disk usage is high: {metrics['disk_usage']}%"
            })
        
        return alerts
    
    def check_services(self, services: Dict) -> List[Dict]:
        alerts = []
        
        for service_name, status in services.items():
            if status != "Running":
                alerts.append({
                    'level': 'danger',
                    'message': f"{service_name} is not running"
                })
        
        return alerts


