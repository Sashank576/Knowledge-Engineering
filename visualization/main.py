from dash import Dash, html, Input, Output, State, callback, ctx
from components import map_column, filters_column, similarity_column, selected_borough_panel
import json
from rdflib import Graph
import time
from utilities.queries import GET_ALL_BOROUGHS, GET_ALL_LISTINGS
from utilities.knowledge_graph import query_to_dataframe
import pandas as pd

start = time.time()

app = Dash()

# # Load RDF graph
# knowledge_graph = Graph()
# knowledge_graph.parse("assets/london_airbnb_kg.ttl", format="turtle")

# all_boroughs = query_to_dataframe(knowledge_graph, GET_ALL_BOROUGHS, ["name"])

all_boroughs = pd.read_csv("assets/all_borough_indicators.csv")
all_listings = pd.read_csv("assets/all_listings.csv")

# calculate the rank for each borough
all_boroughs['transport_rank'] = all_boroughs['transport_score'].rank(method='min').astype(int)
all_boroughs['airbnb_rank']    = all_boroughs['airbnb_score'].rank(method='min').astype(int)
all_boroughs['housing_rank']   = all_boroughs['housing_score'].rank(method='min').astype(int)

# # make a dict with the name of the borough as the key
# all_boroughs = all_boroughs.set_index('name').to_dict('index')

# Make a dict with the name of the borough as the key
all_boroughs = (
    all_boroughs
    .rename(columns={"borough": "name"})  # if needed
    .set_index("name")
    .to_dict("index")
)

# all_listings = query_to_dataframe(knowledge_graph, GET_ALL_LISTINGS, ["name", "borough"]).to_dict('records')
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
        "backgroundColor": "#F5F6FA",
        "boxSizing": "border-box",
        "padding": "16px",
    },
    children=[
        html.Button(
            "☰ Filters",
            id="open-filter-drawer",
            n_clicks=0,
            style={
                "backgroundColor": "black",
                "color": "white",
                "border": "none",
                "borderRadius": "10px",
                "padding": "10px 16px",
                "fontWeight": "700",
                "cursor": "pointer",
                "marginBottom": "12px",
            },
        ),

        html.Div(
            id="filter-drawer",
            style={
                "position": "fixed",
                "top": "0",
                "left": "-320px",
                "width": "300px",
                "height": "100vh",
                "backgroundColor": "white",
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
                        "fontSize": "24px",
                        "border": "none",
                        "background": "none",
                        "cursor": "pointer",
                    },
                ),
                filters_column.render(),
            ],
        ),

        html.Div(
            style={
                "backgroundColor": "white",
                "borderRadius": "16px",
                "padding": "8px",
                "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                "marginBottom": "16px",
            },
            children=map_column.render(all_boroughs),
        ),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "16px",
            },
            children=[
                html.Div(
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "16px",
                        "padding": "16px",
                        "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                    },
                    children=selected_borough_panel.render(
                        all_boroughs, rq2_listings, rq3_hosts, rq4_similarity
                    ),
                ),

                html.Div(
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "16px",
                        "padding": "16px",
                        "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                    },
                    children=similarity_column.render(all_boroughs),
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

if __name__ == "__main__":
    app.run(debug=True)