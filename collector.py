import psutil
import time
import logging
import os
import socket
import json
from datetime import datetime
import csv
from pathlib import Path
import requests

# Configuration
INTERVAL = 10  # 10 seconds interval
DEBUG_MODE = True
CSV_FILE_PATH = 'server_data.csv'

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Applications to monitor
APPLICATIONS = {
    'smartcare': {'process_name': 'SmartCareProcessName', 'port': 8080},  # Replace with actual process name
    'sql_server': {'process_name': 'sqlservr', 'port': 1433},
    'smartlink': {'process_name': 'SmartLinkProcessName', 'port': 3307},  # Replace with actual process name
    'etims': {'process_name': 'ETIMSProcessName', 'port': 8000},          # Replace with actual process name
    'tims': {'process_name': 'TIMSProcessName', 'port': 8089},            # Replace with actual process name
}

def get_ip_addresses():
    """Get the computer's static and public IP addresses."""
    try:
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Get public IP address
        public_ip = requests.get('https://api.ipify.org').text

        return local_ip, public_ip
    except Exception as e:
        logger.exception('Error getting IP addresses')
        return None, None

def check_application_status(application):
    """Check if the specified application is running."""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == application['process_name']:
            return 'Running'
    return 'Stopped'

def collect_system_info():
    """Collect system information."""
    try:
        # Get basic system stats
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get network stats
        net_io = psutil.net_io_counters()
        
        # Get process information
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 0:  # Only include active processes
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': pinfo['cpu_percent'],
                        'memory_percent': pinfo['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Get IP addresses
        local_ip, public_ip = get_ip_addresses()

        # Check application status
        application_status = {app: check_application_status(APPLICATIONS[app]) for app in APPLICATIONS}

        system_info = {
            'timestamp': datetime.now().isoformat(),
            'computer_name': socket.gethostname(),
            'cpu': {
                'usage_percent': cpu_usage,
                'cores': psutil.cpu_count(),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            },
            'top_processes': sorted(processes, 
                                  key=lambda x: x['cpu_percent'], 
                                  reverse=True)[:5],
            'local_ip': local_ip,
            'public_ip': public_ip,
            'application_status': application_status
        }
        
        write_to_csv(system_info)
        return system_info

    except Exception as e:
        logger.exception('Error collecting system information')
        return None

def write_to_csv(data):
    """Write data to CSV file."""
    try:
        fieldnames = [
            "timestamp", "computer_name", "cpu_usage", "memory_usage",
            "disk_usage", "network_bytes_sent", "network_bytes_recv",
            "local_ip", "public_ip", "smartcare_status", "sql_server_status",
            "smartlink_status", "etims_status", "tims_status"
        ]
        
        file_exists = Path(CSV_FILE_PATH).exists()
        
        with open(CSV_FILE_PATH, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                "timestamp": data['timestamp'],
                "computer_name": data['computer_name'],
                "cpu_usage": data['cpu']['usage_percent'],
                "memory_usage": data['memory']['percent'],
                "disk_usage": data['disk']['percent'],
                "network_bytes_sent": data['network']['bytes_sent'],
                "network_bytes_recv": data['network']['bytes_recv'],
                "local_ip": data['local_ip'],
                "public_ip": data['public_ip'],
                "smartcare_status": data['application_status'].get('smartcare', 'Unknown'),
                "sql_server_status": data['application_status'].get('sql_server', 'Unknown'),
                "smartlink_status": data['application_status'].get('smartlink', 'Unknown'),
                "etims_status": data['application_status'].get('etims', 'Unknown'),
                "tims_status": data['application_status'].get('tims', 'Unknown')
            })
            
        logger.debug(f"Data written to CSV: {data['timestamp']}")
        
    except Exception as e:
        logger.exception('Error writing to CSV')

def main():
    logger.info("Starting system monitor...")
    
    while True:
        try:
            system_info = collect_system_info()
            if system_info:
                logger.debug(f"Collected data: {json.dumps(system_info, indent=2)}")
            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Stopping system monitor...")
            break
        except Exception as e:
            logger.exception("Unexpected error in main loop")
            time.sleep(INTERVAL)

if __name__ == '__main__':
    main()