# app/layouts/metrics_dashboard.py
import dash_bootstrap_components as dbc
from dash import html, dcc
from app.components.cards import create_metric_card

def create_system_metrics(computer_name):
    return dbc.Card([
        dbc.CardHeader([
            html.H4("System Metrics", className="mb-0"),
            html.Small(computer_name, className="text-muted")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    create_metric_card(
                        "CPU Usage",
                        html.Div(id="cpu-usage-value"),
                        "fas fa-microchip"
                    )
                ], width=4),
                dbc.Col([
                    create_metric_card(
                        "Memory Usage",
                        html.Div(id="memory-usage-value"),
                        "fas fa-memory"
                    )
                ], width=4),
                dbc.Col([
                    create_metric_card(
                        "Disk Usage",
                        html.Div(id="disk-usage-value"),
                        "fas fa-hdd"
                    )
                ], width=4),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="system-metrics-graph")
                ])
            ])
        ])
    ], className="mb-4")

def create_metric_card(title, value, icon):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"{icon} fa-2x mb-2"),
                html.H5(title, className="mb-2"),
                html.Div(value, className="metric-value")
            ], className="text-center")
        ])
    ], className="status-card")

def create_services_status():
    return dbc.Card([
        dbc.CardHeader(html.H4("Services Status", className="mb-0")),
        dbc.CardBody(
            html.Div(id="services-status-container")
        )
    ], className="mb-4")

def create_network_metrics():
    return dbc.Card([
        dbc.CardHeader(html.H4("Network Metrics", className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    create_metric_card(
                        "Upload Speed",
                        html.Div(id="upload-speed-value"),
                        "fas fa-upload"
                    )
                ], width=6),
                dbc.Col([
                    create_metric_card(
                        "Download Speed",
                        html.Div(id="download-speed-value"),
                        "fas fa-download"
                    )
                ], width=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="network-metrics-graph")
                ])
            ])
        ])
    ], className="mb-4")

