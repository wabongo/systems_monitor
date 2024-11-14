# app/components/alerts.py
import dash_bootstrap_components as dbc
from dash import html

def create_alert(message, level='info'):
  """Create a single alert component."""
  return dbc.Alert(
      message,
      color=level,
      dismissable=True,
      className="mb-2"
  )

def create_alerts(alerts):
  """Create a list of alert components."""
  return [create_alert(alert['message'], alert['level']) for alert in alerts]