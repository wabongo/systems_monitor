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
    'smartcare': {'process_name': 'SmartCareProcessName', 'port': 8080},
    'sql_server': {'process_name': 'sqlservr', 'port': 1433},
    'smartlink': {'process_name': 'SmartLinkProcessName', 'port': 3307},
    'etims': {'process_name': 'ETIMSProcessName', 'port': 8000},
    'tims': {'process_name': 'TIMSProcessName', 'port': 8089},
}

# Store previous network counters
previous_net_io = None
previous_time = None

def bytes_to_mbps(bytes_count, seconds):
  """Convert bytes over time to Mbps and round to whole number."""
  if seconds > 0:  # Avoid division by zero
      mbps = (bytes_count * 8) / (1000000 * seconds)
      return round(mbps)  # Round to nearest whole number like Fast.com
  return 0  # Return 0 if no time has passed  # Round to nearest whole number like Fast.com

def format_speed(speed):
    """Format speed to match Fast.com style."""
    return f"{speed} Mbps"

def get_network_speeds():
  """Calculate current network speeds in Mbps."""
  global previous_net_io, previous_time
  current_net_io = psutil.net_io_counters()
  current_time = time.time()

  if previous_net_io is None or previous_time is None:
      upload_speed = 0
      download_speed = 0
  else:
      time_elapsed = current_time - previous_time
      bytes_sent = current_net_io.bytes_sent - previous_net_io.bytes_sent
      bytes_recv = current_net_io.bytes_recv - previous_net_io.bytes_recv

      upload_speed = bytes_to_mbps(bytes_sent, time_elapsed)
      download_speed = bytes_to_mbps(bytes_recv, time_elapsed)

  previous_net_io = current_net_io
  previous_time = current_time

  logger.debug(f"Upload Speed: {upload_speed} Mbps, Download Speed: {download_speed} Mbps")
  return upload_speed, download_speed




def get_ip_addresses():
    """Get the computer's static and public IP addresses."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
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
                'upload_speed_mbps': upload_speed,    # Now whole numbers like Fast.com
                'download_speed_mbps': download_speed # Now whole numbers like Fast.com
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