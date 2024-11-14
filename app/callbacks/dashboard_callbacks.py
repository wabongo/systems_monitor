# app/callbacks/dashboard_callbacks.py
from dash import Input, Output, State, html, dcc, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from ..data.data_handler import DataHandler
from ..utils.alerts import AlertSystem
import pandas as pd

# Initialize data handler
data_handler = DataHandler()

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
  
  metrics = data_handler.get_latest_metrics(computer_name)
  historical = data_handler.get_historical_data(computer_name, ['cpu_usage', 'memory_usage', 'disk_usage'])
  
  # Create system metrics graph
  fig = go.Figure()
  for metric in ['cpu_usage', 'memory_usage', 'disk_usage']:
      fig.add_trace(go.Scatter(
          x=historical['timestamp'],
          y=historical[metric],
          name=metric.replace('_', ' ').title(),  # Format metric name for display
          mode='lines+markers'
      ))
  
  fig.update_layout(
      title="System Metrics History",
      xaxis_title="Time",
      yaxis_title="Usage (%)",
      hovermode='x unified'
  )
  
  return (
      f"{metrics['cpu_usage']}%",
      f"{metrics['memory_usage']}%",
      f"{metrics['disk_usage']}%",
      fig
  )

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
  
  df = data_handler.read_data()
  current = df[df['computer_name'] == computer_name].iloc[-1]
  historical = data_handler.get_historical_data(
      computer_name, 
      ['network_bytes_sent', 'network_bytes_recv'], 
      hours=24
  )
  
  # Clean the speed values (remove 'Mbps' and convert to float)
  historical['network_bytes_sent'] = historical['network_bytes_sent'].astype(float)
  historical['network_bytes_recv'] = historical['network_bytes_recv'].astype(float)
  
  # Create network metrics graph
  fig = go.Figure()
  
  # Add upload trace
  fig.add_trace(go.Scatter(
      x=historical['timestamp'],
      y=historical['network_bytes_sent'],
      name='Upload Speed',
      line=dict(color='#2ECC71'),
      fill='tozeroy'
  ))
  
  # Add download trace
  fig.add_trace(go.Scatter(
      x=historical['timestamp'],
      y=historical['network_bytes_recv'],
      name='Download Speed',
      line=dict(color='#3498DB'),
      fill='tozeroy'
  ))
  
  fig.update_layout(
      title="Network Speed History",
      xaxis_title="Time",
      yaxis_title="Speed (Bytes)",
      hovermode='x unified',
      showlegend=True
  )
  
  return current['network_bytes_sent'], current['network_bytes_recv'], fig

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