# app/callbacks/theme_callbacks.py
from dash import callback, Input, Output, State
import dash_bootstrap_components as dbc

@callback(
    [Output("theme-store", "data"),
     Output("_pages_location", "href")],
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    if not current_theme:
        current_theme = {"theme": "light"}
    
    new_theme = "dark" if current_theme["theme"] == "light" else "light"
    return {"theme": new_theme}, None

