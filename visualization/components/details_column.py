from dash import html

def render():
    return html.Div(
        style={
            'padding': '24px 16px',
            'borderLeft': '1px solid #e0e0e0',
            'height': '100%',
            'boxSizing': 'border-box',
            'backgroundColor': '#fafafa',
            'overflowY': 'auto',
        },
        children=['xd']
    )