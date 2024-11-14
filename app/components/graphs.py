# app/components/graphs.py
import plotly.graph_objects as go

def create_line_graph(x_data, y_data, title, x_title, y_title):
  """Create a line graph."""
  fig = go.Figure()
  fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines+markers'))
  
  fig.update_layout(
      title=title,
      xaxis_title=x_title,
      yaxis_title=y_title,
      hovermode='x unified'
  )
  
  return fig