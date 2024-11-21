from dash import callback, Input, Output, State, dcc
import pandas as pd
from io import BytesIO
import json
from ..data.data_handler import DataHandler

# Initialize data handler
data_handler = DataHandler()

@callback(
    Output("download-data", "data"),
    Input("export-menu", "n_clicks"),
    State("computer-selector", "value"),
    prevent_initial_call=True
)
def export_data(n_clicks, computer_name):
    if not n_clicks or not computer_name:
        return None
    
    # Get all relevant data
    metrics = data_handler.get_latest_metrics(computer_name)
    services = data_handler.get_service_status(computer_name)
    
    # Extract IP information from metrics
    ip_info = {
        'local_ip': metrics.get('local_ip', 'N/A'),
        'public_ip': metrics.get('public_ip', 'N/A')
    }
    
    # Combine all data
    export_data = {
        "computer_name": computer_name,
        "timestamp": pd.Timestamp.now().isoformat(),
        "metrics": metrics,
        "services": services,
        "network": ip_info
    }
    
    # Create Excel file with multiple sheets
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # System Metrics Sheet
        pd.DataFrame([metrics]).to_excel(writer, sheet_name='System Metrics', index=False)
        
        # Services Status Sheet
        pd.DataFrame([services]).to_excel(writer, sheet_name='Services Status', index=False)
        
        # Network Information Sheet
        pd.DataFrame([ip_info]).to_excel(writer, sheet_name='Network Info', index=False)
    
    return dcc.send_bytes(
        output.getvalue(),
        f"franchise_monitor_{computer_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    if not n_clicks or not computer_name:
        return None
    
    # Get all relevant data
    metrics = data_handler.get_latest_metrics(computer_name)
    services = data_handler.get_service_status(computer_name)
    ip_info = data_handler.get_ip_information(computer_name)
    
    # Combine all data
    export_data = {
        "computer_name": computer_name,
        "timestamp": pd.Timestamp.now().isoformat(),
        "metrics": metrics,
        "services": services,
        "network": ip_info
    }
    
    # Create Excel file with multiple sheets
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # System Metrics Sheet
        pd.DataFrame([metrics]).to_excel(writer, sheet_name='System Metrics', index=False)
        
        # Services Status Sheet
        pd.DataFrame([services]).to_excel(writer, sheet_name='Services Status', index=False)
        
        # Network Information Sheet
        pd.DataFrame([ip_info]).to_excel(writer, sheet_name='Network Info', index=False)
    
    return dcc.send_bytes(
        output.getvalue(),
        f"franchise_monitor_{computer_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )