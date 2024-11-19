# app/layouts/header.py
import dash_bootstrap_components as dbc
from dash import html

def create_header():
    return html.Nav(
        dbc.Container([
            dbc.Row([
                # Left side - Brand
                dbc.Col([
                    html.Div([
                        html.I(className="fas fa-server text-primary", style={"font-size": "1.5rem"}),
                        html.H1("EQA Franchise Monitor", className="navbar-brand")
                    ], className="d-flex align-items-center gap-3")
                ], width="auto"),
                
                # Center - IP Address Information
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-network-wired me-2"),
                            html.Span("Local IP: ", className="text-muted"),
                            html.Span(id="local-ip-display", className="fw-bold")
                        ], className="me-4"),
                        html.Div([
                            html.I(className="fas fa-globe me-2"),
                            html.Span("Public IP: ", className="text-muted"),
                            html.Span(id="public-ip-display", className="fw-bold")
                        ])
                    ], className="d-flex align-items-center justify-content-center")
                ], className="text-center"),
                
                # Right side - Controls
                dbc.Col([
                    html.Div([
                        # IP Change Alert
                        html.Div([
                            dbc.Alert(
                                id="ip-change-alert",
                                is_open=False,
                                duration=0,
                                color="warning",
                                className="position-fixed top-0 end-0 m-3"
                            )
                        ]),
                        # Export button
                        dbc.Button([
                            html.I(className="fas fa-download me-2"),
                            "Export"
                        ], id="export-menu", color="primary", size="sm", className="export-btn")
                    ], className="d-flex align-items-center")
                ], width="auto", className="ms-auto")
            ], className="align-items-center", style={"height": "70px"})
        ], fluid=True),
        className="navbar-custom py-2 mb-4"
    )
