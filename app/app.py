import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from dash import html, dcc
from .layouts.main import create_layout  # Note the dot before layouts
from .callbacks import dashboard_callbacks, export_callbacks, theme_callbacks

# Initialize the app with Bootstrap and Font Awesome
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://use.fontawesome.com/releases/v5.15.4/css/all.css'
    ],
    suppress_callback_exceptions=True
)

app.layout = create_layout()

# Add theme toggle clientside callback
app.clientside_callback(
    """
    function(theme) {
        if (theme) {
            document.documentElement.setAttribute('data-theme', theme.theme);
            return theme.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        return 'fas fa-moon';
    }
    """,
    Output("theme-toggle", "children"),
    Input("theme-store", "data")
)