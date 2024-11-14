# app/data/models.py
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class NetworkData(BaseModel):
    upload_speed_mbps: str
    download_speed_mbps: str

class IPAddresses(BaseModel):
    internal_ip: str
    external_ip: str
    static_ips: List[str]

class GeneralInfo(BaseModel):
    computer_name: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_data: NetworkData
    ip_addresses: IPAddresses

class ApplicationStatus(BaseModel):
    status: bool
    process_name: str

class ApplicationInfo(BaseModel):
    smartcare: ApplicationStatus
    sql_server: ApplicationStatus
    smartlink: ApplicationStatus
    etims: ApplicationStatus
    tims: ApplicationStatus

class SystemInfo(BaseModel):
    general_info: GeneralInfo
    application_info: ApplicationInfo
    timestamp: float

class MonitoringData(BaseModel):
    system_info: SystemInfo
    notifications: List[str]