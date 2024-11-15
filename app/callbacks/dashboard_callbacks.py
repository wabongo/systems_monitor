# app/callbacks/dashboard_callbacks.py
from datetime import datetime
from venv import logger
from dash import Input, Output, State, html, dcc, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from collector import get_network_speeds
from ..data.data_handler import DataHandler
from ..utils.alerts import AlertSystem
import pandas as pd

# Initialize data handler
data_handler = DataHandler()

def bytes_to_mbps(bytes, time_diff):
    return (bytes / time_diff) / (1024 * 1024)

@callback(
  Output("computer-selector", "options"),
  Input("metrics-update-interval", "n_intervals")
)
def update_computer_list(n):
  df = data_handler.read_data()
  
  # Debugging output
  print("DataFrame columns:", df.columns.tolist())  # Print the column names
  print("DataFrame head:\n", df.head())  # Print the first few rows of the DataFrame
  
  # Check if 'computer_name' exists in the DataFrame
  if 'computer_name' not in df.columns:
      print("Error: 'computer_name' column not found in DataFrame.")
      return []  # Return an empty list if the column is not found
  
  computers = df['computer_name'].unique()  # Use the correct column name
  return [{"label": comp, "value": comp} for comp in computers]

@callback(
  [Output("cpu-usage-value", "children"),
   Output("memory-usage-value", "children"),
   Output("disk-usage-value", "children"),
   Output("system-metrics-graph", "figure")],
  [Input("computer-selector", "value"),
   Input("metrics-update-interval", "n_intervals")]
)
def update_system_metrics(computer_name, n):
    if not computer_name:
        return "N/A", "N/A", "N/A", go.Figure()
    
    try:
        metrics = data_handler.get_latest_metrics(computer_name)
        if not metrics:
            return "N/A", "N/A", "N/A", go.Figure()
            
        historical = data_handler.get_historical_data(
            computer_name, 
            ['cpu_usage', 'memory_usage', 'disk_usage']
        )
        
        if historical.empty:
            return (
                f"{metrics.get('cpu_usage', 'N/A')}%",
                f"{metrics.get('memory_usage', 'N/A')}%",
                f"{metrics.get('disk_usage', 'N/A')}%",
                go.Figure()
            )
        
        # Create system metrics graph
        fig = go.Figure()
        colors = {'cpu_usage': '#FF6B6B', 'memory_usage': '#4ECDC4', 'disk_usage': '#45B7D1'}
        
        for metric in ['cpu_usage', 'memory_usage', 'disk_usage']:
            if metric in historical.columns:
                fig.add_trace(go.Scatter(
                    x=historical['timestamp'],
                    y=historical[metric],
                    name=metric.replace('_', ' ').title(),
                    mode='lines+markers',
                    line=dict(color=colors[metric])
                ))
        
        fig.update_layout(
            title="System Metrics History",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return (
            f"{metrics.get('cpu_usage', 'N/A')}%",
            f"{metrics.get('memory_usage', 'N/A')}%",
            f"{metrics.get('disk_usage', 'N/A')}%",
            fig
        )
        
    except Exception as e:
        logger.exception("Error updating system metrics")
        return "Error", "Error", "Error", go.Figure()

@callback(
  [Output("upload-speed-value", "children"),
   Output("download-speed-value", "children"),
   Output("network-metrics-graph", "figure")],
  [Input("computer-selector", "value"),
   Input("metrics-update-interval", "n_intervals")]
)
def update_network_metrics(computer_name, n):
    if not computer_name:
        return "N/A", "N/A", go.Figure()

    try:
        # Get historical network data
        historical = data_handler.get_historical_data(
            computer_name, 
            ['network_bytes_sent', 'network_bytes_recv']
        )
        
        if historical.empty:
            return "N/A", "N/A", go.Figure()

        # Calculate speeds from bytes
        time_diff = (historical['timestamp'].max() - historical['timestamp'].min()).total_seconds()
        if time_diff > 0:
            upload_speed = bytes_to_mbps(
                historical['network_bytes_sent'].diff().fillna(0).mean(), 
                time_diff / len(historical)
            )
            download_speed = bytes_to_mbps(
                historical['network_bytes_recv'].diff().fillna(0).mean(),
                time_diff / len(historical)
            )
        else:
            upload_speed = download_speed = 0

        # Create network metrics graph
        fig = go.Figure()

        # Add upload speed trace
        fig.add_trace(go.Scatter(
            x=historical['timestamp'],
            y=historical['network_bytes_sent'].diff().fillna(0).apply(
                lambda x: bytes_to_mbps(x, time_diff / len(historical))
            ),
            name='Upload Speed (Mbps)',
            mode='lines+markers',
            line=dict(color='#2ECC71')
        ))

        # Add download speed trace
        fig.add_trace(go.Scatter(
            x=historical['timestamp'],
            y=historical['network_bytes_recv'].diff().fillna(0).apply(
                lambda x: bytes_to_mbps(x, time_diff / len(historical))
            ),
            name='Download Speed (Mbps)',
            mode='lines+markers',
            line=dict(color='#3498DB')
        ))

        fig.update_layout(
            title="Network Speed History",
            xaxis_title="Time",
            yaxis_title="Speed (Mbps)",
            hovermode='x unified'
        )

        return f"{upload_speed:.1f} Mbps", f"{download_speed:.1f} Mbps", fig

    except Exception as e:
        logger.exception("Error updating network metrics")
        return "Error", "Error", go.Figure()

@callback(
  Output("services-status-container", "children"),
  [Input("computer-selector", "value"),
   Input("metrics-update-interval", "n_intervals")]
)
def update_services_status(computer_name, n):
  if not computer_name:
      return "No computer selected"
  
  services = data_handler.get_service_status(computer_name)
  
  status_indicators = []
  for service_name, status in services.items():
      status_class = "service-running" if status == "Running" else "service-stopped"
      status_indicators.append(
          dbc.Row([
              dbc.Col(html.Span(service_name), width=6),
              dbc.Col(
                  html.Span(
                      status,
                      className=f"service-status {status_class}"
                  ),
                  width=6,
                  className="text-end"
              )
          ], className="mb-2")
      )
  
  return html.Div(status_indicators)

@callback(
  Output("alerts-container", "children"),
  [Input("computer-selector", "value"),
   Input("metrics-update-interval", "n_intervals")]
)
def update_alerts(computer_name, n):
  if not computer_name:
      return []
  
  alert_system = AlertSystem()
  metrics = data_handler.get_latest_metrics(computer_name)
  services = data_handler.get_service_status(computer_name)
  
  # Collect all alerts
  alerts = alert_system.check_metrics(metrics) + alert_system.check_services(services)
  
  # Create alert components
  alert_components = []
  for alert in alerts:
      alert_components.append(
          dbc.Alert(
              alert['message'],
              color=alert['level'],
              dismissable=True,
              className="mb-2"
          )
      )
  
  return alert_components