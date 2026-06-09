from dash import Dash, html, Input, Output, State, callback, ctx, no_update
from components import map_column, filters_column, similarity_column, selected_borough_panel
import json
import time
import pandas as pd
from utilities.style import COLORS

start = time.time()

app = Dash()

# Load all listings and borough pressure indicators
all_boroughs = pd.read_csv("assets/all_borough_indicators.csv")
all_listings = pd.read_csv("assets/all_listings.csv")

# Calculate the rank for each borough
all_boroughs['transport_rank'] = all_boroughs['transport_score'].rank(method='min').astype(int)
all_boroughs['airbnb_rank']    = all_boroughs['airbnb_score'].rank(method='min').astype(int)
all_boroughs['housing_rank']   = all_boroughs['housing_score'].rank(method='min').astype(int)

# Make a dict with the name of the borough as the key
all_boroughs = (
    all_boroughs
    .rename(columns={"borough": "name"})  # if needed
    .set_index("name")
    .to_dict("index")
)
all_listings = all_listings.to_dict("records")

# Load all entire-home listings in borough with both high Airbnb and housing pressure
rq2_listings = pd.read_csv("assets/rq2_entire_home_examples.csv")
rq2_listings = rq2_listings.to_dict("records")

# Load all the multi-borough hosts
rq3_hosts = pd.read_csv("assets/rq3_multiborough_hosts.csv")
rq3_hosts = rq3_hosts.to_dict("records")

# Load all the borough profile (cosine) similarity scores
rq4_similarity = pd.read_csv("assets/rq4_similarity_pairs.csv")

with open("assets/london_boroughs.geojson") as f:
    GEOJSON = json.load(f)

end = time.time()
length = end - start
print("It took", length, "seconds to start the app!")

app.layout = html.Div(
    style={
        "minHeight": "100vh",
        "backgroundColor": COLORS["background"],
        "fontFamily": "Poppins, Arial, sans-serif",
        "boxSizing": "border-box",
        "padding": "14px",
    },
    children=[
        # Header
        html.Div(
            style={
                "backgroundColor": COLORS["background"],
                "borderRadius": "16px",
                "padding": "12px 18px",
                "marginBottom": "14px",
                "border": "1px solid #E2E8F0",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
            },
            children=[
                html.Div([
                    # Left side: Logo + Title
                    html.Div([
                        html.Img(
                            src="/assets/underground-logo.png",
                            style={
                                "height": "50px",
                                "width": "auto",
                                "marginRight": "5px",
                            },
                        ),
                        html.H1(
                            "London Accommodation Pressure Monitor",
                            style={
                                "margin": "0",
                                "color": COLORS['primary_dark'],
                                "fontSize": "26px",
                                "fontWeight": "700",
                            },
                        ),
                    ], style={"display": "flex", "alignItems": "center", "gap": "12px"}),

                    # Right side: Button
                    html.Button(
                        "☰ Filters",
                        id="open-filter-drawer",
                        n_clicks=0,
                        style={
                            "backgroundColor": COLORS['primary_dark'],
                            "color": "white",
                            "border": "none",
                            "borderRadius": "10px",
                            "padding": "10px 16px",
                            "fontWeight": "600",
                            "cursor": "pointer",
                        },
                    ),
                ], style={
                    "display": "flex",
                    "justifyContent": "space-between",  # pushes button to the right
                    "alignItems": "center",
                    "width": "100%",
                }),
            ],
        ),

        # Filter drawer
        html.Div(
            id="filter-drawer",
            style={
                "position": "fixed",
                "top": "0",
                "left": "-330px",
                "width": "310px",
                "height": "100vh",
                "backgroundColor": COLORS["background"],
                "zIndex": "9999",
                "boxShadow": "4px 0 20px rgba(0,0,0,0.18)",
                "transition": "left 0.25s ease",
                "padding": "20px",
                "boxSizing": "border-box",
                "overflowY": "auto",
            },
            children=[
                html.Button(
                    "×",
                    id="close-filter-drawer",
                    n_clicks=0,
                    style={
                        "float": "right",
                        "fontSize": "26px",
                        "border": "none",
                        "background": "none",
                        "cursor": "pointer",
                        "color": COLORS['primary_dark'],
                    },
                ),
                filters_column.render(),
            ],
        ),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "25% 50% 25%",
                "gap": "14px",
                "height": "calc(100vh - 105px)",
                "minHeight": "650px",
            },
            children=[
                # Left: selected borough explorer
                html.Div(
                    style={
                        "backgroundColor": COLORS["background"],
                        "borderRadius": "16px",
                        "padding": "14px",
                        "overflowY": "auto",
                        "border": "1px solid #E2E8F0",
                        "minHeight": 0,
                    },
                    children=selected_borough_panel.render(
                        all_boroughs,
                        rq2_listings,
                        rq3_hosts,
                        rq4_similarity,
                    ),
                ),

                # Center: map
                html.Div(
                    style={
                        "backgroundColor": COLORS["background"],
                        "borderRadius": "16px",
                        "padding": "8px",
                        "border": "1px solid #E2E8F0",
                        "minHeight": 0,
                    },
                    children=map_column.render(all_boroughs),
                ),

                # Right: similarity graph
                html.Div(
                    style={
                        "backgroundColor": COLORS["background"],
                        "borderRadius": "16px",
                        "padding": "14px",
                        "overflowY": "auto",
                        "border": "1px solid #E2E8F0",
                        "minHeight": 0,
                    },
                    children=similarity_column.render(all_boroughs, rq4_similarity),
                ),
            ],
        ),
    ],
)
def filter_listings(listings, transport_levels, pressure_levels, housing_levels):
    """
    Keep listings whose borough's indicators match all enabled levels.
    Indicator values are looked up from map_column.BOROUGH_DATA, not stored
    on the listing itself.
    """
    borough_data = all_boroughs

    return [
        l for l in listings
        if (row := borough_data.get(l["borough"])) is not None
        and row["transportation_indicator"].lower()  in (transport_levels or [])
        and row["airbnb_pressure_indicator"].lower() in (pressure_levels  or [])
        and row["housing_indicator"].lower()         in (housing_levels   or [])
    ]


@callback(
    Output("choropleth-map", "figure"),
    Output("cooccurrence-overlay", "children"),
    Input("indicator-dropdown",               "value"),
    Input("choropleth-map",                   "relayoutData"),
    Input("filter-transportation_indicator",  "value"),
    Input("filter-airbnb_pressure_indicator", "value"),
    Input("filter-housing_indicator",         "value"),
)
def update_map(indicator, relayout_data, transport_levels, pressure_levels, housing_levels):
    # Preserve whatever zoom/center the user has scrolled to
    zoom   = 9
    center = None
    if relayout_data:
        if "mapbox.zoom" in relayout_data:
            zoom = relayout_data["mapbox.zoom"]
        if "mapbox.center" in relayout_data:
            center = relayout_data["mapbox.center"]

    visible = filter_listings(all_listings, transport_levels, pressure_levels, housing_levels)

    fig = map_column.build_figure(all_boroughs, GEOJSON, indicator, visible, zoom=zoom, center=center)
    overlay_children = map_column.build_cooccurrence_overlay(all_boroughs, indicator).children
    return fig, overlay_children


@callback(
    Output("selected-borough-panel", "children"),
    Input("choropleth-map", "clickData"),
)
def update_selected_borough_panel(clickData):
    if not clickData:
        return selected_borough_panel.render_selected_borough(all_boroughs)

    borough = clickData["points"][0].get("location")

    if not borough:
        return selected_borough_panel.render_selected_borough(all_boroughs)

    return selected_borough_panel.render_selected_borough(all_boroughs, borough, rq2_listings, rq3_hosts, rq4_similarity)

@callback(
    Output("similarity-graph", "figure"),
    Input("similarity-threshold-slider", "value"),
)
def update_similarity(threshold):
    return similarity_column.build_similarity_figure(
        rq4_similarity,
        threshold
    )

@callback(
    Output("filter-drawer", "style"),
    Input("open-filter-drawer", "n_clicks"),
    Input("close-filter-drawer", "n_clicks"),
    State("filter-drawer", "style"),
)
def toggle_filter_drawer(_, __, current_style):
    style = current_style.copy()

    if not ctx.triggered_id:
        return style

    if ctx.triggered_id == "open-filter-drawer":
        style["left"] = "0"

    if ctx.triggered_id == "close-filter-drawer":
        style["left"] = "-320px"

    return style

# Make it so that if you click on a borough node in the similarity graph, it will pull up that borough in the panel
@callback(
    Output("selected-borough-panel", "children", allow_duplicate=True),
    Input("similarity-graph", "clickData"),
    prevent_initial_call=True,
)
def update_selected_from_similarity(clickData):
    if not clickData:
        return no_update

    borough = clickData["points"][0].get("customdata")

    if not borough:
        return no_update

    return selected_borough_panel.render_selected_borough(
        all_boroughs,
        borough,
        rq2_listings,
        rq3_hosts,
        rq4_similarity
    )

if __name__ == "__main__":
    app.run(debug=True)