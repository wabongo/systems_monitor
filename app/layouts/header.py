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
                
                # Right side - Controls
                dbc.Col([
                    html.Div([
                        # Dark mode toggle
                        html.Div([
                            html.Button([
                                html.I(id="theme-toggle-icon", className="fas fa-moon")
                            ], id="theme-toggle", className="theme-toggle-btn")
                        ], className="theme-toggle-wrapper me-3"),
                        
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
