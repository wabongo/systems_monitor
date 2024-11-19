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
        # Get historical network data including speed test results
        historical = data_handler.get_historical_data(
            computer_name, 
            ['internet_upload_speed', 'internet_download_speed']
        )
        
        if historical.empty:
            return "N/A", "N/A", go.Figure()

        # Get the latest speed test results
        latest = historical.iloc[-1]
        upload_speed = latest.get('internet_upload_speed', 0)
        download_speed = latest.get('internet_download_speed', 0)

        # Create network metrics graph
        fig = go.Figure()

        # Add upload speed trace
        fig.add_trace(go.Scatter(
            x=historical['timestamp'],
            y=historical['internet_upload_speed'],
            name='Upload Speed (Mbps)',
            mode='lines+markers',
            line=dict(color='#2ECC71')
        ))

        # Add download speed trace
        fig.add_trace(go.Scatter(
            x=historical['timestamp'],
            y=historical['internet_download_speed'],
            name='Download Speed (Mbps)',
            mode='lines+markers',
            line=dict(color='#3498DB')
        ))

        fig.update_layout(
            title="Internet Speed History",
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

@callback(
    [
        Output('network-graph', 'figure'),
        Output('internet-speed-graph', 'figure')
    ],
    [Input('interval-component', 'n_intervals')]
)
def update_network_graphs(n):
    try:
        df = data_handler.get_historical_data()
        if df.empty:
            raise ValueError("No data available")

        # Network Usage Graph
        network_fig = go.Figure()
        network_fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['upload_speed_mbps'],
            name='Upload (Usage)',
            line=dict(color='blue')
        ))
        network_fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['download_speed_mbps'],
            name='Download (Usage)',
            line=dict(color='green')
        ))
        
        network_fig.update_layout(
            title='Network Usage Over Time',
            xaxis_title='Time',
            yaxis_title='Speed (Mbps)',
            template='plotly_dark'
        )

        # Internet Speed Test Graph
        speed_fig = go.Figure()
        speed_fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['internet_upload_speed'],
            name='Upload (Speed Test)',
            line=dict(color='orange')
        ))
        speed_fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['internet_download_speed'],
            name='Download (Speed Test)',
            line=dict(color='red')
        ))
        
        speed_fig.update_layout(
            title='Internet Speed Test Results',
            xaxis_title='Time',
            yaxis_title='Speed (Mbps)',
            template='plotly_dark'
        )

        return network_fig, speed_fig
    except Exception as e:
        logger.error(f"Error updating network graphs: {e}")
        return {}, {}

@callback(
    [Output("local-ip-display", "children"),
     Output("public-ip-display", "children"),
     Output("ip-change-alert", "is_open"),
     Output("ip-change-alert", "children")],
    [Input("computer-selector", "value"),
     Input("metrics-update-interval", "n_intervals")]
)
def update_ip_addresses(computer_name, n):
    """Update IP address displays and check for IP changes."""
    if not computer_name:
        return "N/A", "N/A", False, ""
    
    try:
        metrics = data_handler.get_latest_metrics(computer_name)
        if not metrics:
            return "N/A", "N/A", False, ""
        
        local_ip = metrics.get('local_ip', 'N/A')
        public_ip = metrics.get('public_ip', 'N/A')
        
        # Don't show "Unknown" in the UI
        if local_ip == "Unknown":
            local_ip = "Not Available"
        if public_ip == "Unknown":
            public_ip = "Not Available"
        
        # Check for IP change only if we have valid IPs
        if public_ip not in ["N/A", "Not Available"]:
            previous_metrics = data_handler.get_previous_metrics(computer_name)
            prev_ip = previous_metrics.get('public_ip') if previous_metrics else None
            if prev_ip and prev_ip not in ["N/A", "Unknown", "Not Available"] and prev_ip != public_ip:
                alert_msg = html.Div([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Public IP changed from {prev_ip} to {public_ip}"
                ])
                return local_ip, public_ip, True, alert_msg
        
        return local_ip, public_ip, False, ""
        
    except Exception as e:
        logger.error(f"Error updating IP addresses: {str(e)}")
        return "Error", "Error", False, ""  # Return error state on exception