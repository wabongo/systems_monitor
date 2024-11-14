# app/utils/config.py
import yaml
import os
from typing import Dict, Any

class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '../../config.yaml')
        with open(config_path, 'r') as file:
            self._config = yaml.safe_load(file)
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

config = ConfigManager()