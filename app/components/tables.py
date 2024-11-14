# app/components/tables.py
import dash_table
import pandas as pd

def create_data_table(dataframe):
  """Create a Dash DataTable from a DataFrame."""
  return dash_table.DataTable(
      data=dataframe.to_dict('records'),
      columns=[{"name": i, "id": i} for i in dataframe.columns],
      page_size=10,
      style_table={'overflowX': 'auto'},
      style_cell={
          'textAlign': 'left',
          'padding': '5px',
      },
      style_header={
          'backgroundColor': 'lightgrey',
          'fontWeight': 'bold'
      }
  )