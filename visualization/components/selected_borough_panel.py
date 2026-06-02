from dash import html
from components.map_column import BOROUGH_DATA


def _level_color(level):
    return {
        "low": "#4caf50",
        "medium": "#f5a623",
        "high": "#f44336",
    }.get(level, "#999")


def _score_chip(title, score, level, rank):
    return html.Span(
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "gap": "6px",
            "padding": "5px 10px",
            "border": "1px solid #e5e7eb",
            "borderRadius": "999px",
            "backgroundColor": "#ffffff",
            "fontSize": "12px",
            "whiteSpace": "nowrap",
        },
        children=[
            html.Span(title, style={"fontWeight": "700", "color": "#374151"}),
            html.Span(f"{score:.2f}", style={"fontWeight": "700", "color": "#111827"}),
            html.Span(
                level.title(),
                style={
                    "backgroundColor": _level_color(level),
                    "color": "#fff" if level != "medium" else "#111",
                    "padding": "1px 6px",
                    "borderRadius": "999px",
                    "fontSize": "10px",
                    "fontWeight": "700",
                },
            ),
            html.Span(f"#{rank}", style={"color": "#6b7280"}),
        ],
    )

def render_selected_borough(borough=None):
    if borough is None:
        return html.Div(
            style={"padding": "20px 24px", "color": "#6b7280"},
            children=[
                html.H3("Selected Borough Intelligence", style={"marginTop": 0}),
                html.P("Click a borough on the map to view scores  and related listings/hosts."),
            ],
        )

    data = BOROUGH_DATA.get(borough)

    if data is None:
        return html.Div(
            style={"padding": "20px 24px"},
            children=[
                html.H3("Selected Borough Details"),
                html.P("No data available for this borough."),
            ],
        )

    return html.Div(
        style={
            "padding": "12px 24px",
            "height": "100%",
            "boxSizing": "border-box",
            "overflowY": "auto",
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "flexWrap": "wrap",
                    "marginBottom": "6px",
                },
                children=[
                    html.H3(
                        borough,
                        style={
                            "margin": 0,
                            "fontSize": "20px",
                            "color": "#111827",
                            "marginRight": "8px",
                        },
                    ),
                    _score_chip(
                        "Transport",
                        data["transport_score"],
                        data["transportation_indicator"],
                        data["transport_rank"],
                    ),
                    _score_chip(
                        "Airbnb",
                        data["airbnb_score"],
                        data["airbnb_pressure_indicator"],
                        data["airbnb_rank"],
                    ),
                    _score_chip(
                        "Housing",
                        data["housing_score"],
                        data["housing_indicator"],
                        data["housing_rank"],
                    ),
                ],
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr",
                    "gap": "14px",
                    "marginTop": "8px",
                },
                children=[
                    html.Div(
                        style={
                            "border": "1px solid #e5e7eb",
                            "borderRadius": "10px",
                            "padding": "12px",
                            "backgroundColor": "#fff",
                        },
                        children=[
                            html.H4(
                                "Relevant entire-home listings",
                                style={"marginTop": 0}
                            ),

                            html.Div(
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "8px",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "padding": "8px",
                                            "borderRadius": "8px",
                                            "backgroundColor": "#f8fafc",
                                        },
                                        children=[
                                            html.Div(
                                                "Modern Flat in Barnet",
                                                style={"fontWeight": "600"}
                                            ),
                                            html.Div(
                                                "Entire home • £145/night",
                                                style={
                                                    "fontSize": "12px",
                                                    "color": "#6b7280",
                                                }
                                            ),
                                        ]
                                    ),

                                    html.Div(
                                        style={
                                            "padding": "8px",
                                            "borderRadius": "8px",
                                            "backgroundColor": "#f8fafc",
                                        },
                                        children=[
                                            html.Div(
                                                "Garden Apartment",
                                                style={"fontWeight": "600"}
                                            ),
                                            html.Div(
                                                "Entire home • £132/night",
                                                style={
                                                    "fontSize": "12px",
                                                    "color": "#6b7280",
                                                }
                                            ),
                                        ]
                                    ),

                                    html.Div(
                                        style={
                                            "padding": "8px",
                                            "borderRadius": "8px",
                                            "backgroundColor": "#f8fafc",
                                        },
                                        children=[
                                            html.Div(
                                                "Family House",
                                                style={"fontWeight": "600"}
                                            ),
                                            html.Div(
                                                "Entire home • £168/night",
                                                style={
                                                    "fontSize": "12px",
                                                    "color": "#6b7280",
                                                }
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                    ),
                    
                    html.Div(
                        style={
                            "border": "1px solid #e5e7eb",
                            "borderRadius": "10px",
                            "padding": "12px",
                            "backgroundColor": "#fff",
                        },
                        children=[
                            html.H4(
                                "Multi-borough hosts",
                                style={"marginTop": 0}
                            ),

                            html.Div(
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "8px",
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "padding": "8px",
                                            "borderRadius": "8px",
                                            "backgroundColor": "#f8fafc",
                                        },
                                        children=[
                                            html.Div(
                                                "Host_1024",
                                                style={"fontWeight": "600"}
                                            ),
                                            html.Div(
                                                "5 listings • Barnet, Camden",
                                                style={
                                                    "fontSize": "12px",
                                                    "color": "#6b7280",
                                                }
                                            ),
                                        ]
                                    ),

                                    html.Div(
                                        style={
                                            "padding": "8px",
                                            "borderRadius": "8px",
                                            "backgroundColor": "#f8fafc",
                                        },
                                        children=[
                                            html.Div(
                                                "Host_887",
                                                style={"fontWeight": "600"}
                                            ),
                                            html.Div(
                                                "3 listings • Barnet, Islington",
                                                style={
                                                    "fontSize": "12px",
                                                    "color": "#6b7280",
                                                }
                                            ),
                                        ]
                                    ),

                                    html.Div(
                                        style={
                                            "padding": "8px",
                                            "borderRadius": "8px",
                                            "backgroundColor": "#f8fafc",
                                        },
                                        children=[
                                            html.Div(
                                                "Host_341",
                                                style={"fontWeight": "600"}
                                            ),
                                            html.Div(
                                                "7 listings • Barnet, Camden, Hackney",
                                                style={
                                                    "fontSize": "12px",
                                                    "color": "#6b7280",
                                                }
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                    ),
                ],
            ),
        ],
    )


def render():
    return html.Div(
        id="selected-borough-panel",
        style={
            "borderTop": "1px solid #e5e7eb",
            "backgroundColor": "#f9fafb",
            "minHeight": 0,
        },
        children=render_selected_borough(),
    )