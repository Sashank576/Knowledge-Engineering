from dash import html
from utilities.style import COLORS





def _normalize_borough(name):
    return str(name).replace("_", " ").strip().lower()


def _score_card(title, score, level, rank):
    level = str(level).title()

    return html.Div(
        style={
            "border": f"1px solid {COLORS['border']}",
            "borderRadius": "14px",
            "padding": "12px",
            "backgroundColor": COLORS['card'],
            "boxShadow": COLORS['shadow_soft'],
        },
        children=[
            html.Div(
                title,
                style={
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "color": COLORS['text_secondary'],
                    "marginBottom": "6px",
                },
            ),
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "gap": "10px",
                },
                children=[
                    html.Span(
                        f"{score:.2f}",
                        style={
                            "fontSize": "20px",
                            "fontWeight": "700",
                            "color": COLORS['text'],
                        },
                    ),
                    html.Span(
                        level,
                        style={
                            "backgroundColor": COLORS[level.lower()],
                            "color": "#111827" if level == "Low" else "#fff",
                            "padding": "3px 8px",
                            "borderRadius": "999px",
                            "fontSize": "11px",
                            "fontWeight": "700",
                        },
                    ),
                ],
            ),
            html.Div(
                f"Rank #{rank}",
                style={
                    "fontSize": "11px",
                    "color": COLORS['text_secondary'],
                    "marginTop": "4px",
                },
            ),
        ],
    )


def _section_title(title, subtitle=None):
    return html.Div(
        style={"marginTop": "18px", "marginBottom": "10px"},
        children=[
            html.H4(
                title,
                style={
                    "margin": "0",
                    "fontSize": "15px",
                    "fontWeight": "700",
                    "color": COLORS['primary_dark'],
                },
            ),
            html.Div(
                subtitle or "",
                style={
                    "fontSize": "11px",
                    "color": COLORS['text_secondary'],
                    "marginTop": "2px",
                },
            ),
        ],
    )


def _listing_card(listing):
    return html.Div(
        style={
            "padding": "10px",
            "borderRadius": "12px",
            "border": f"1px solid {COLORS['border']}",
            "backgroundColor": COLORS['card_muted'],
        },
        children=[
            html.Div(
                listing["listingName"],
                style={
                    "fontWeight": "600",
                    "fontSize": "12px",
                    "color": COLORS['text'],
                    "lineHeight": "1.3",
                },
            ),
            html.Div(
                f"£{listing['price']:.0f}/night • {listing['reviews']} reviews/month",
                style={
                    "fontSize": "11px",
                    "color": COLORS['text_secondary'],
                    "marginTop": "4px",
                },
            ),
        ],
    )


def _host_card(host):
    return html.Div(
        style={
            "padding": "10px",
            "borderRadius": "12px",
            "border": f"1px solid {COLORS['border']}",
            "backgroundColor": COLORS['card_muted'],
        },
        children=[
            html.Div(
                host["hostName"],
                style={
                    "fontWeight": "600",
                    "fontSize": "12px",
                    "color": COLORS['text'],
                    "lineHeight": "1.3",
                },
            ),
            html.Div(
                f"Active in {host['boroughCount']} boroughs • {host['hostListingCount']} listings",
                style={
                    "fontSize": "11px",
                    "color": COLORS['text_secondary'],
                    "marginTop": "4px",
                },
            ),
            html.Div(
                str(host["boroughs"]).replace("_", " "),
                style={
                    "fontSize": "10px",
                    "color": COLORS['text_secondary'],
                    "marginTop": "4px",
                    "lineHeight": "1.3",
                },
            ),
        ],
    )


def _empty_state(message):
    return html.Div(
        message,
        style={
            "fontSize": "12px",
            "color": COLORS['text_secondary'],
            "fontStyle": "italic",
            "padding": "10px",
            "borderRadius": "10px",
            "backgroundColor": COLORS['card'],
            "border": f"1px solid {COLORS['border']}",
        },
    )


def render_selected_borough(
    all_boroughs,
    borough=None,
    rq2_listings=None,
    rq3_hosts=None,
    rq4_similarity=None,
):
    if borough is None:
        return html.Div(
            style={"color": COLORS['text_secondary']},
            children=[
                html.H3(
                    "Selected Borough",
                    style={
                        "marginTop": 0,
                        "color": COLORS['primary_dark'],
                        "fontSize": "18px",
                    },
                ),
                html.P(
                    "Click a borough on the map to view pressure scores, listings, hosts, and similar boroughs.",
                    style={"fontSize": "13px", "lineHeight": "1.45"},
                ),
            ],
        )

    data = all_boroughs.get(borough)
    if data is None:
        return html.Div(
            children=[
                html.H3("Selected Borough", style={"color": COLORS['primary_dark']}),
                html.P("No data available for this borough."),
            ],
        )

    rq2_listings = rq2_listings or []
    rq3_hosts = rq3_hosts or []
    selected_borough = _normalize_borough(borough)

    # Prepare the RQ2 entire-home listing data.
    # Only take the top-x borough (with the most reviews), otherwise it doesn't load properly.
    all_entire_home_listings = [
        listing for listing in rq2_listings
        if listing["borough"] == borough
    ]

    top_listings = sorted(
        all_entire_home_listings,
        key=lambda x: x["reviews"],
        reverse=True,
    )[:50]

    # Prepare the RQ3 multi-borough hosts data.
    # When clicking on a borough, we should find hosts active in the selected borough (+ at least one other borough).
    all_matching_hosts = [
        host
        for host in rq3_hosts
        if selected_borough in [
            _normalize_borough(b)
            for b in str(host["boroughs"]).split(",")
        ]
    ]

    # Show top hosts active in most boroughs
    top_hosts = sorted(
        all_matching_hosts,
        key=lambda x: x["boroughCount"],
        reverse=True,
    )[:50]

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
        if matches.empty:
            similar_boroughs = []
        else:
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
                matches.sort_values("similarity", ascending=False)["other_borough"]
                .drop_duplicates()
                .head(5)
                .tolist()
            )

    return html.Div(
        style={
            "height": "100%",
            "boxSizing": "border-box",
            "overflowY": "auto",
        },
        children=[
            html.H3(
                borough,
                style={
                    "margin": "0 0 12px 0",
                    "fontSize": "24px",
                    "fontWeight": "700",
                    "color": COLORS['primary_dark'],
                    "lineHeight": "1.2",
                },
            ),

            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr",
                    "gap": "10px",
                },
                children=[
                    _score_card(
                        "Airbnb pressure",
                        data["airbnb_score"],
                        data["airbnb_pressure_indicator"],
                        data["airbnb_rank"],
                    ),
                    _score_card(
                        "Housing pressure",
                        data["housing_score"],
                        data["housing_indicator"],
                        data["housing_rank"],
                    ),
                    _score_card(
                        "Accessibility pressure",
                        data["transport_score"],
                        data["transportation_indicator"],
                        data["transport_rank"],
                    ),
                ],
            ),

            _section_title("Similar boroughs", "Based on pressure profile similarity"),
            html.Div(
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "6px",
                },
                children=(
                    [
                        html.Span(
                            b,
                            style={
                                "backgroundColor": "#EEF2FF",
                                "color": COLORS['primary_dark'],
                                "border": f"1px solid {COLORS['border']}",
                                "borderRadius": "999px",
                                "padding": "4px 8px",
                                "fontSize": "11px",
                                "fontWeight": "600",
                            },
                        )
                        for b in similar_boroughs
                    ]
                    if similar_boroughs
                    else [_empty_state("No similar boroughs found.")]
                ),
            ),

            _section_title(
                "Entire-home listings",
                f"{len(all_entire_home_listings)} relevant listings found",
            ),
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "10px",
                    "maxHeight": "260px",
                    "overflowY": "auto",
                },
                children=(
                    [_listing_card(listing) for listing in top_listings]
                    if top_listings
                    else [_empty_state("No relevant entire-home listings for this borough. Please select a high-pressure (Airbnb + Housing) borough. Such boroughs can be found using the filter tool.")]
                ),
            ),

            _section_title(
                "Multi-borough hosts",
                f"{len(all_matching_hosts)} hosts found",
            ),
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "10px",
                    "maxHeight": "260px",
                    "overflowY": "auto",
                },
                children=(
                    [_host_card(host) for host in top_hosts]
                    if top_hosts
                    else [_empty_state("No multi-borough hosts found.")]
                ),
            ),
        ],
    )


def render(all_boroughs, rq2_listings, rq3_hosts, rq4_similarity):
    return html.Div(
        id="selected-borough-panel",
        style={
            "height": "100%",
            "minHeight": 0,
            "backgroundColor": "transparent",
        },
        children=render_selected_borough(all_boroughs, rq2_listings=rq2_listings, rq3_hosts=rq3_hosts, rq4_similarity=rq4_similarity),
    )