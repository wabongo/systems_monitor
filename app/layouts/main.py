# app/layouts/main.py
import dash_bootstrap_components as dbc
from dash import html, dcc
from .header import create_header
from .metrics_dashboard import create_system_metrics, create_services_status, create_network_metrics

def create_layout():
  return html.Div([
      create_header(),
      dbc.Container([
          dbc.Row([
              dbc.Col([
                  dbc.Card([
                      dbc.CardHeader("Select Franchise"),
                      dbc.CardBody([
                          dcc.Dropdown(
                              id='computer-selector',
                              placeholder="Select a computer...",
                              className="mb-2"
                          ),
                          html.Div(id="last-update-time", className="text-muted small")
                      ])
                  ], className="mb-3"),
                  html.Div(id="alerts-container")  # Container for alerts
              ], width=12, lg=3),
              dbc.Col([
                  html.Div(id="main-metrics-container"),
                  dbc.Tabs([
                      dbc.Tab(
                          dbc.Row([
                              dbc.Col(create_system_metrics(""), width=12)
                          ]),
                          label="System Metrics",
                          tab_id="system-metrics-tab"
                      ),
                      dbc.Tab(
                          dbc.Row([
                              dbc.Col(create_services_status(), width=12)
                          ]),
                          label="Service Status",
                          tab_id="service-status-tab"
                      ),
                      dbc.Tab(
                          dbc.Row([
                              dbc.Col(create_network_metrics(), width=12)
                          ]),
                          label="Network Metrics",
                          tab_id="network-metrics-tab"
                      ),
                  ], id="metrics-tabs", active_tab="system-metrics-tab")
              ], width=12, lg=9)
          ])
      ], fluid=True),
      dcc.Interval(id='metrics-update-interval', interval=60000),  # 60 seconds
      dcc.Store(id='theme-store'),
      dcc.Download(id="download-data")
  ])