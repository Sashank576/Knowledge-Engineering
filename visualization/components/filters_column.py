from dash import html, dcc

INDICATOR_OPTIONS = [
    {"label": "Airbnb Pressure Indicator", "value": "airbnb_pressure_indicator"},
    {"label": "Housing Indicator", "value": "housing_indicator"},
    {"label": "Transportation Indicator", "value": "transportation_indicator"},
]

def render():
    return html.Div(
        style={
            'padding': '24px 16px',
            'borderRight': '1px solid #e0e0e0',
            'height': '100%',
            'boxSizing': 'border-box',
            'backgroundColor': '#fafafa',
        },
        children=[
            html.H3(
                "Filters",
                style={
                    'marginTop': 0,
                    'marginBottom': '24px',
                    'fontSize': '16px',
                    'fontWeight': '600',
                    'color': '#333',
                }
            ),
            html.Label(
                "Show indicator",
                style={
                    'fontSize': '13px',
                    'fontWeight': '500',
                    'color': '#555',
                    'marginBottom': '8px',
                    'display': 'block',
                }
            ),
            dcc.Dropdown(
                id="indicator-dropdown",
                options=INDICATOR_OPTIONS,
                value="transportation_indicator",
                clearable=False,
                style={'fontSize': '13px'},
            ),
        ]
    )