from dash import html


def _level_color(level):
    return {
        "Low": "#4caf50",
        "Medium": "#f5a623",
        "High": "#f44336",
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
                    "color": "#fff" if level != "Medium" else "#111",
                    "padding": "1px 6px",
                    "borderRadius": "999px",
                    "fontSize": "10px",
                    "fontWeight": "700",
                },
            ),
            html.Span(f"#{rank}", style={"color": "#6b7280"}),
        ],
    )

# Sometimes the borough names will have _ instead of spaces. This function normalizes it to use spaces.
def _normalize_borough(name):
    return name.replace("_", " ").strip().lower()

def _get_similar_boroughs(borough):
    if borough == "Redbridge":
        return ["Barnet", "Harrow", "Hillingdon"]

    return ["Camden", "Islington", "Hackney"]

def render_selected_borough(all_boroughs, borough=None, rq2_listings=None, rq3_hosts=None, rq4_similarity=None):
    if borough is None:
        return html.Div(
            style={"padding": "20px 24px", "color": "#6b7280"},
            children=[
                html.H3("Selected Borough Details", style={"marginTop": 0}),
                html.P("Click a borough on the map to view scores  and related listings/hosts."),
            ],
        )

    data = all_boroughs.get(borough)
    selected_borough = _normalize_borough(borough)

    # Prepare the RQ2 entire-home listing data.
    # Only take the top-x borough (with the most reviews), otherwise it doesn't load properly.
    all_entire_home_listings = [
        listing for listing in rq2_listings
        if listing["borough"] == borough
    ]

    top_x_examples = sorted(
        all_entire_home_listings,
        key=lambda x: x["reviews"],
        reverse=True,
    )[:150]

    # Prepare the RQ3 multi-borough hosts data.
    # When clicking on a borough, we should find hosts active in the selected borough (+ at least one other borough).
    all_matching_hosts = [
        host
        for host in rq3_hosts
        if selected_borough in [
            _normalize_borough(borough)
            for borough in host["boroughs"].split(",")
        ]
    ]

    # Show top-x hosts active in most boroughs
    top_x_hosts = sorted(
        all_matching_hosts,
        key=lambda x: x["boroughCount"],
        reverse=True,
    )[:150]

    # Prepare the RQ4 borough profile similarity data.
    # It will find the 5 boroughs with the highest similarity score to the selected_borough.
    if rq4_similarity is None:
        similar_boroughs = []
    else:
        # Find all rows with similarity scores relating to the currently selected borough
        matches = rq4_similarity[
            (rq4_similarity["from_borough"] == borough) |
            (rq4_similarity["to_borough"] == borough)
            ].copy()

        # Find the borough which the selected borough is connected to
        matches["other_borough"] = matches.apply(
            lambda row: (
                row["to_borough"]
                if row["from_borough"] == borough
                else row["from_borough"]
            ),
            axis=1,
        )

        # Sort all found matches so the most similar boroughs come first
        matches = matches.sort_values("similarity", ascending=False)

        # Keep the top 5 most similar boroughs
        similar_boroughs = (
            matches["other_borough"]
            .drop_duplicates()
            .head(5)
            .tolist()
        )

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
                    "marginTop": "8px",
                    "marginBottom": "12px",
                    "fontSize": "13px",
                    "color": "#4b5563",
                },
                children=[
                    html.Span(
                        "Most similar boroughs by pressure profile: ",
                        style={"fontWeight": "600"},
                    ),
                    ", ".join(similar_boroughs) if similar_boroughs else "No similar boroughs found"
                ]
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
                                f"Relevant entire-home listings (found {len(all_entire_home_listings)} listings, showing top {len(top_x_examples)} reviewed listings)" ,
                                style={"marginTop": 0}
                            ),

                            # Show the RQ2 entire-home listings
                            html.Div(
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "8px",
                                    "maxHeight": "260px",
                                    "overflowY": "auto",
                                },
                                children=(
                                    [
                                        html.Div(
                                            style={
                                                "padding": "8px",
                                                "borderRadius": "8px",
                                                "backgroundColor": "#f8fafc",
                                            },
                                            children=[
                                                html.Div(
                                                    f"{listing['listingName']} (ID {listing['listing']})",
                                                    style={"fontWeight": "600"},
                                                ),
                                                html.Div(
                                                    f"£{listing['price']:.0f}/night • {listing['reviews']} reviews/month",
                                                    style={
                                                        "fontSize": "12px",
                                                        "color": "#6b7280",
                                                    },
                                                ),
                                            ],
                                        )
                                        for listing in top_x_examples
                                    ]
                                    if top_x_examples
                                    else [
                                        html.Div(
                                            "No relevant entire-home listings available for this borough (not a high Airbnb and Housing Pressure borough).",
                                            style={
                                                "fontSize": "13px",
                                                "color": "#6b7280",
                                                "fontStyle": "italic",
                                            },
                                        )
                                    ]
                                ),
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
                                f"Multi-borough hosts (found {len(all_matching_hosts)} hosts, showing top {len(top_x_hosts)} most multi-borough active hosts)",
                                style={"marginTop": 0}
                            ),

                            html.Div(
                                style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "8px",
                                    "maxHeight": "260px",
                                    "overflowY": "auto",
                                },
                                children=(
                                    [
                                        html.Div(
                                            style={
                                                "padding": "8px",
                                                "borderRadius": "8px",
                                                "backgroundColor": "#f8fafc",
                                            },
                                            children=[
                                                html.Div(
                                                    f"Host {host['hostName']} (ID {host['host']})",
                                                    style={"fontWeight": "600"},
                                                ),
                                                html.Div(
                                                    f"Active in {host['boroughCount']} boroughs • {host['hostListingCount']} listings",
                                                    style={
                                                        "fontSize": "12px",
                                                        "color": "#6b7280",
                                                    },
                                                ),
                                                html.Div(
                                                    host["boroughs"].replace("_", " "),
                                                    style={
                                                        "fontSize": "11px",
                                                        "color": "#6b7280",
                                                        "marginTop": "4px",
                                                    },
                                                ),
                                            ],
                                        )
                                        for host in top_x_hosts
                                    ]
                                    if top_x_hosts
                                    else [
                                        html.Div(
                                            "No multi-borough hosts found.",
                                            style={
                                                "fontSize": "13px",
                                                "color": "#6b7280",
                                                "fontStyle": "italic",
                                            },
                                        )
                                    ]
                                ),
                            )
                        ],
                    ),
                ],
            ),
        ],
    )


def render(all_boroughs, rq2_listings, rq3_hosts, rq4_similarity):
    return html.Div(
        id="selected-borough-panel",
        style={
            "borderTop": "1px solid #e5e7eb",
            "backgroundColor": "#f9fafb",
            "minHeight": 0,
        },
        children=render_selected_borough(all_boroughs),
    )