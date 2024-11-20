# app/callbacks/theme_callbacks.py
from dash import callback, Input, Output, State
import dash_bootstrap_components as dbc

# Theme configuration
THEMES = {
    "light": {
        "icon": "fa-moon",
        "tooltip": "Switch to Dark Mode",
        "plotly": {
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
            "gridcolor": "#DFE4EA"
        }
    },
    "dark": {
        "icon": "fa-sun",
        "tooltip": "Switch to Light Mode",
        "plotly": {
            "paper_bgcolor": "#22272E",
            "plot_bgcolor": "#22272E",
            "gridcolor": "#374151"
        }
    }
}

@callback(
    Output("theme-store", "data"),
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    if not current_theme:
        current_theme = {"theme": "light"}
    
    new_theme = "dark" if current_theme["theme"] == "light" else "light"
    return {"theme": new_theme}

@callback(
    Output("_theme-update", "children"),
    Input("theme-store", "data")
)
def update_graph_theme(theme_data):
    """
    Update graph themes when the theme changes.
    This is a hidden callback that triggers graph updates.
    """
    if not theme_data:
        return None
    
    theme_name = theme_data["theme"]
    theme = THEMES[theme_name]
    
    # Store the plotly theme in a global variable that can be accessed by graph callbacks
    session["plotly_theme"] = theme["plotly"]
    
    return None