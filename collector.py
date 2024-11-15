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
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server_data.csv')

def load_config():
    """Load configuration from config.json file."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None

config = load_config()
if not config:
    logger.error("Failed to load configuration. Using defaults.")
    INTERVAL = 10
    DEBUG_MODE = True
    APPLICATIONS = {
        'smartcare': {'process_name': 'SmartCareProcessName', 'port': 8080},
        'sql_server': {'process_name': 'sqlservr', 'port': 1433},
        'smartlink': {'process_name': 'SmartLinkProcessName', 'port': 3307},
        'etims': {'process_name': 'ETIMSProcessName', 'port': 8000},
        'tims': {'process_name': 'TIMSProcessName', 'port': 8089}
    }
    THRESHOLDS = {
        'cpu_percent': 80,
        'memory_percent': 90,
        'disk_percent': 85
    }
else:
    INTERVAL = config.get('interval', 10)
    DEBUG_MODE = config.get('debug_mode', True)
    APPLICATIONS = config.get('applications', {})
    THRESHOLDS = config.get('thresholds', {
        'cpu_percent': 80,
        'memory_percent': 90,
        'disk_percent': 85
    })

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Store previous network counters and IP
previous_net_io = None
previous_time = None
previous_public_ip = None

def bytes_to_mbps(bytes_count, seconds):
    """Convert bytes over time to Megabits per second (Mbps)."""
    if seconds <= 0:  # Avoid division by zero
        return 0
    
    # Convert bytes to bits and then to megabits
    bits = bytes_count * 8
    megabits = bits / 1_000_000  # Using decimal (1 million) for Mbps calculation
    
    # Calculate megabits per second
    mbps = megabits / seconds
    
    return round(mbps, 2)  # Round to 2 decimal places

def format_speed(speed):
    """Format speed to match Fast.com style."""
    return f"{speed} Mbps"

def get_network_speeds():
    """Calculate current network speeds in Mbps."""
    global previous_net_io, previous_time
    
    current_net_io = psutil.net_io_counters()
    current_time = time.time()
    
    # Initialize speeds to 0
    upload_speed = download_speed = 0
    
    if previous_net_io and previous_time:
        time_elapsed = current_time - previous_time
        
        # Only calculate if at least 1 second has passed
        if time_elapsed >= 1:
            # Calculate bytes transferred during the interval
            bytes_sent = current_net_io.bytes_sent - previous_net_io.bytes_sent
            bytes_recv = current_net_io.bytes_recv - previous_net_io.bytes_recv
            
            # Convert to Mbps
            upload_speed = bytes_to_mbps(bytes_sent, time_elapsed)
            download_speed = bytes_to_mbps(bytes_recv, time_elapsed)
            
            logger.debug(f"Raw bytes sent: {bytes_sent}, received: {bytes_recv} in {time_elapsed} seconds")
    
    # Update previous values
    previous_net_io = current_net_io
    previous_time = current_time
    
    logger.debug(f"Network Speeds - Upload: {upload_speed} Mbps, Download: {download_speed} Mbps")
    return upload_speed, download_speed

def check_port(port):
    """Check if a port is in use."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def check_application_status(application):
    """Check if the specified application is running and its port is active."""
    process_running = False
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == application['process_name']:
            process_running = True
            break
    
    port_active = check_port(application['port'])
    
    if process_running and port_active:
        return 'Running'
    elif process_running:
        return 'Process Running (Port Closed)'
    elif port_active:
        return 'Port Active (Process Stopped)'
    return 'Stopped'

def check_ip_change(current_public_ip):
    """Monitor for changes in public IP address."""
    global previous_public_ip
    
    if previous_public_ip is None:
        previous_public_ip = current_public_ip
        return False, None
    
    if current_public_ip != previous_public_ip:
        old_ip = previous_public_ip
        previous_public_ip = current_public_ip
        return True, old_ip
    
    return False, None

def get_ip_addresses():
    """Get the computer's static and public IP addresses."""
    global previous_public_ip
    
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Get public IP
        public_ip = requests.get('https://api.ipify.org').text
        
        # Check for IP change
        ip_changed, old_ip = check_ip_change(public_ip)
        if ip_changed:
            logger.warning(f"PUBLIC IP CHANGED - Old: {old_ip}, New: {public_ip}")
            logger.warning("Remote access may be affected! Update whitelist configurations.")
        
        return local_ip, public_ip
    except Exception as e:
        logger.exception('Error getting IP addresses')
        return None, None

def check_thresholds(system_info):
    """Check if any metrics exceed defined thresholds."""
    alerts = []
    
    cpu_usage = system_info['cpu']['usage_percent']
    if cpu_usage > THRESHOLDS['cpu_percent']:
        alerts.append(f"HIGH CPU USAGE: {cpu_usage}% exceeds threshold of {THRESHOLDS['cpu_percent']}%")
    
    memory_usage = system_info['memory']['percent']
    if memory_usage > THRESHOLDS['memory_percent']:
        alerts.append(f"HIGH MEMORY USAGE: {memory_usage}% exceeds threshold of {THRESHOLDS['memory_percent']}%")
    
    disk_usage = system_info['disk']['percent']
    if disk_usage > THRESHOLDS['disk_percent']:
        alerts.append(f"HIGH DISK USAGE: {disk_usage}% exceeds threshold of {THRESHOLDS['disk_percent']}%")
    
    return alerts

def collect_system_info():
    """Collect system information."""
    try:
        # Get basic system stats
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get network stats and speeds
        net_io = psutil.net_io_counters()
        upload_speed, download_speed = get_network_speeds()
        
        # Get process information
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 0:
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': pinfo['cpu_percent'],
                        'memory_percent': pinfo['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        local_ip, public_ip = get_ip_addresses()
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
                'packets_recv': net_io.packets_recv,
                'upload_speed_mbps': upload_speed,
                'download_speed_mbps': download_speed
            },
            'top_processes': sorted(processes, 
                                  key=lambda x: x['cpu_percent'], 
                                  reverse=True)[:5],
            'local_ip': local_ip,
            'public_ip': public_ip,
            'application_status': application_status
        }
        
        # Check for threshold alerts
        alerts = check_thresholds(system_info)
        for alert in alerts:
            logger.warning(alert)
        
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
          "upload_speed_mbps", "download_speed_mbps",
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
              "upload_speed_mbps": data['network']['upload_speed_mbps'],
              "download_speed_mbps": data['network']['download_speed_mbps'],
              "local_ip": data['local_ip'],
              "public_ip": data['public_ip'],
              "smartcare_status": data['application_status'].get('smartcare', 'Unknown'),
              "sql_server_status": data['application_status'].get('sql_server', 'Unknown'),
              "smartlink_status": data['application_status'].get('smartlink', 'Unknown'),
              "etims_status": data['application_status'].get('etims', 'Unknown'),
              "tims_status": data['application_status'].get('tims', 'Unknown')
          })

          logger.debug(f"Data written to CSV: {data['timestamp']}")
          # Log network speeds in Fast.com style
          logger.info(f"Download Speed: {format_speed(data['network']['download_speed_mbps'])}")
          logger.info(f"Upload Speed: {format_speed(data['network']['upload_speed_mbps'])}")

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