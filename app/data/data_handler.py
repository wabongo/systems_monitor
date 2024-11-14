# app/data/data_handler.py
import pandas as pd
from datetime import datetime, timedelta
import os
from ..utils.logger import logger

class DataHandler:
  def __init__(self):
      self.csv_path = 'server_data.csv'
      self._cache = None
      self._last_read = None
      self.cache_duration = timedelta(seconds=5)  # Refresh every 5 seconds

  def _should_refresh_cache(self) -> bool:
      """Check if the cache should be refreshed based on the time elapsed."""
      if self._cache is None or self._last_read is None:
          return True
      return datetime.now() - self._last_read > self.cache_duration

  def read_data(self) -> pd.DataFrame:
      """Read and cache the monitoring data."""
      try:
          if self._should_refresh_cache():
              if os.path.exists(self.csv_path):
                  df = pd.read_csv(self.csv_path)
                  df['timestamp'] = pd.to_datetime(df['timestamp'])
                  self._cache = df
                  self._last_read = datetime.now()
                  logger.info(f"Data read from {self.csv_path}")
              else:
                  logger.error(f"Data file not found: {self.csv_path}")
                  return pd.DataFrame()
          return self._cache
      except Exception as e:
          logger.error(f"Error reading data: {str(e)}")
          return pd.DataFrame()

  def get_latest_metrics(self, computer_name: str) -> dict:
      """Get the latest metrics for a specific computer."""
      df = self.read_data()
      if df.empty:
          return {}
      
      latest = df[df['computer_name'] == computer_name].iloc[-1]
      return {
          'cpu_usage': latest['cpu_usage'],
          'memory_usage': latest['memory_usage'],
          'disk_usage': latest['disk_usage'],
          'network_bytes_sent': latest['network_bytes_sent'],
          'network_bytes_recv': latest['network_bytes_recv'],
          'local_ip': latest['local_ip'],
          'public_ip': latest['public_ip'],
          'smartcare_status': latest['smartcare_status'],
          'sql_server_status': latest['sql_server_status'],
          'smartlink_status': latest['smartlink_status'],
          'etims_status': latest['etims_status'],
          'tims_status': latest['tims_status'],
          'timestamp': latest['timestamp']
      }

  def get_historical_data(self, computer_name: str, metrics: list, hours: int = 1) -> pd.DataFrame:
      """Get historical data for specific metrics."""
      df = self.read_data()
      if df.empty:
          return pd.DataFrame()

      cutoff_time = datetime.now() - timedelta(hours=hours)
      filtered_df = df[
          (df['computer_name'] == computer_name) & 
          (df['timestamp'] >= cutoff_time)
      ]
      
      # Ensure the requested metrics are in the DataFrame
      available_metrics = [metric for metric in metrics if metric in filtered_df.columns]
      
      return filtered_df[['timestamp'] + available_metrics]  # Return timestamp and requested metrics

  def get_service_status(self, computer_name: str) -> dict:
      """Get the status of services for a specific computer."""
      df = self.read_data()
      if df.empty:
          return {}
      
      latest = df[df['computer_name'] == computer_name].iloc[-1]
      return {
          'smartcare': latest['smartcare_status'],
          'sql_server': latest['sql_server_status'],
          'smartlink': latest['smartlink_status'],
          'etims': latest['etims_status'],
          'tims': latest['tims_status']
      }