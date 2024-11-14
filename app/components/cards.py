# app/components/cards.py
import dash_bootstrap_components as dbc
from dash import html

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