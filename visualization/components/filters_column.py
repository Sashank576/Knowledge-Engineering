from dash import html, dcc

INDICATOR_OPTIONS = [
    {"label": "Accessibility Pressure Indicator", "value": "transportation_indicator"},
    {"label": "Airbnb Pressure Indicator", "value": "airbnb_pressure_indicator"},
    {"label": "Housing Pressure Indicator", "value": "housing_indicator"},
]

LEVEL_COLORS = {
    "low":    "#4caf50",   # same as map markers
    "medium": "#ffeb3b",   # same as map markers
    "high":   "#f44336",   # same as map markers
}

LEVELS = ["low", "medium", "high"]


def _checklist_group(indicator_key: str, label: str) -> html.Div:
    return html.Div(
        style={"marginBottom": "16px"},
        children=[
            html.Div(
                label,
                style={
                    "fontSize": "12px",
                    "fontWeight": "600",
                    "color": "#444",
                    "marginBottom": "6px",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.04em",
                }
            ),
            # One styled toggle per level
            html.Div(
                style={"display": "flex", "flexDirection": "column", "gap": "4px"},
                children=[
                    dcc.Checklist(
                        id=f"filter-{indicator_key}",
                        options=[
                            {
                                "label": html.Span(
                                    lvl.capitalize(),
                                    style={
                                        "backgroundColor": LEVEL_COLORS[lvl],
                                        "color": "#000",
                                        "borderRadius": "4px",
                                        "padding": "1px 8px",
                                        "fontSize": "12px",
                                        "fontWeight": "600",
                                        "marginLeft": "6px",
                                    }
                                ),
                                "value": lvl,
                            }
                            for lvl in LEVELS
                        ],
                        value=LEVELS,           # all enabled by default
                        inline=True,
                        style={"gap": "8px"},
                        inputStyle={"cursor": "pointer"},
                        labelStyle={"cursor": "pointer", "display": "inline-flex", "alignItems": "center"},
                    )
                ]
            )
        ]
    )


def render():
    listing_filter_indicators = [
        ("transportation_indicator", "Accessibility Pressure Indicator"),
        ("airbnb_pressure_indicator", "Airbnb Pressure Indicator"),
        ("housing_indicator", "Housing Pressure Indicator"),
    ]

    return html.Div(
        style={
            'padding': '24px 16px',
            'borderRight': '1px solid #e0e0e0',
            'height': '100%',
            'boxSizing': 'border-box',
            'backgroundColor': '#fafafa',
            'overflowY': 'auto',
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

            # --- Map indicator dropdown ---
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
                style={'fontSize': '13px', 'marginBottom': '28px'},
            ),

            # --- Listing filters ---
            html.Div(
                "Filter listings by boroughs with:",
                style={
                    'fontSize': '13px',
                    'fontWeight': '500',
                    'color': '#555',
                    'marginBottom': '14px',
                }
            ),
            *[
                _checklist_group(key, label)
                for key, label in listing_filter_indicators
            ],
        ]
    )