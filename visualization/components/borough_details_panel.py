from dash import html
from components.map_column import BOROUGH_DATA


def _level_color(level):
    return {
        "low": "#4caf50",
        "medium": "#f5a623",
        "high": "#f44336",
    }.get(level, "#999")


def _score_card(title, score, level, rank):
    return html.Div(
        style={
            "padding": "14px",
            "border": "1px solid #e5e7eb",
            "borderRadius": "10px",
            "marginBottom": "12px",
            "backgroundColor": "#ffffff",
        },
        children=[
            html.Div(
                title,
                style={
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "color": "#555",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.04em",
                    "marginBottom": "6px",
                },
            ),
            html.Div(
                f"{score:.2f}",
                style={
                    "fontSize": "28px",
                    "fontWeight": "700",
                    "color": "#111827",
                },
            ),
            html.Div(
                [
                    html.Span(
                        level.title(),
                        style={
                            "backgroundColor": _level_color(level),
                            "color": "#fff" if level != "medium" else "#111",
                            "padding": "2px 8px",
                            "borderRadius": "999px",
                            "fontSize": "11px",
                            "fontWeight": "700",
                            "marginRight": "8px",
                        },
                    ),
                    html.Span(
                        f"Rank #{rank}",
                        style={
                            "fontSize": "12px",
                            "color": "#6b7280",
                        },
                    ),
                ]
            ),
        ],
    )


def render_borough_details(borough=None):
    if borough is None:
        return html.Div(
            style={
                "padding": "24px",
                "color": "#6b7280",
            },
            children=[
                html.H3(
                    "Borough Details",
                    style={
                        "marginTop": 0,
                        "fontSize": "18px",
                        "color": "#111827",
                    },
                ),
                html.P("Click a borough on the map to see its scores."),
            ],
        )

    data = BOROUGH_DATA.get(borough)

    if data is None:
        return html.Div(
            style={"padding": "24px"},
            children=[
                html.H3("Borough details"),
                html.P("No data available for this borough."),
            ],
        )

    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(3, 1fr)",
            "gap": "12px",
            "margin": "16px",
        },
        children=[
            _score_card(
                "Transport Accessibility",
                data["transport_score"],
                data["transportation_indicator"],
                data["transport_rank"],
            ),
            _score_card(
                "Airbnb Pressure",
                data["airbnb_score"],
                data["airbnb_pressure_indicator"],
                data["airbnb_rank"],
            ),
            _score_card(
                "Housing Pressure",
                data["housing_score"],
                data["housing_indicator"],
                data["housing_rank"],
            ),
        ],
    )


def render():
    return html.Div(
        id="borough-details-panel",
        style={
            "height": "100%",
            "borderTop": "1px solid #e5e7eb",
            "backgroundColor": "#f9fafb",
        },
        children=render_borough_details(),
    )