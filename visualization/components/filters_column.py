from dash import html, dcc
from utilities.style import COLORS

INDICATOR_OPTIONS = [
    {"label": "Accessibility Pressure Indicator", "value": "transportation_indicator"},
    {"label": "Airbnb Pressure Indicator", "value": "airbnb_pressure_indicator"},
    {"label": "Housing Pressure Indicator", "value": "housing_indicator"},
]


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
                    "color": COLORS['text_secondary'],
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
                                        "backgroundColor": COLORS[lvl.lower()],
                                        "color": "#fff" if lvl != "low" else "#000",
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
            'padding': '18px 8px 24px 8px',
            'height': '100%',
            'boxSizing': 'border-box',
            'backgroundColor': COLORS['surface'],
            'overflowY': 'auto',
        },
        children=[
            html.H3(
                "Filters",
                style={
                    'marginTop': 0,
                    'marginBottom': '24px',
                    'fontSize': '18px',
                    'fontWeight': '800',
                    'color': COLORS['primary_dark'],
                }
            ),

            # --- Map indicator dropdown ---
            html.Label(
                "Show indicator",
                style={
                    'fontSize': '13px',
                    'fontWeight': '500',
                    'color': COLORS['text_secondary'],
                    'marginBottom': '8px',
                    'display': 'block',
                }
            ),
            dcc.Dropdown(
                id="indicator-dropdown",
                options=INDICATOR_OPTIONS,
                value="airbnb_pressure_indicator",
                clearable=False,
                style={'fontSize': '13px', 'marginBottom': '28px'},
            ),

            # --- Listing filters ---
            html.Div(
                "Filter listings by boroughs with:",
                style={
                    'fontSize': '13px',
                    'fontWeight': '500',
                    'color': COLORS['text_secondary'],
                    'marginBottom': '14px',
                }
            ),
            *[
                _checklist_group(key, label)
                for key, label in listing_filter_indicators
            ],
        ]
    )