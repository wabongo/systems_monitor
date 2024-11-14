# app/layouts/header.py
import dash_bootstrap_components as dbc
from dash import html

def create_header():
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(html.I(className="fas fa-server fa-2x text-white"), width="auto"),
                dbc.Col(dbc.NavbarBrand("Franchise Monitor", className="ms-2")),
            ], align="center"),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        html.I(className="fas fa-moon"),
                        id="theme-toggle",
                        color="light",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Button(
                        html.I(className="fas fa-download"),
                        id="export-menu",
                        color="light",
                        size="sm"
                    ),
                ])
            ])
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4"
    )

