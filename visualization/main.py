from dash import Dash, html, Input, Output, callback
from components import map_column, filters_column, similarity_column, selected_borough_panel
import json
from rdflib import Graph
import time
from utilities.queries import GET_ALL_BOROUGHS, GET_ALL_LISTINGS
from utilities.knowledge_graph import query_to_dataframe

start = time.time()

app = Dash()

# Load RDF graph
knowledge_graph = Graph()
knowledge_graph.parse("assets/london_airbnb_kg.ttl", format="turtle")

all_boroughs = query_to_dataframe(knowledge_graph, GET_ALL_BOROUGHS, ["name"])
# calculate the rank for each borough
all_boroughs['transport_rank'] = all_boroughs['transport_score'].rank(method='min').astype(int)
all_boroughs['airbnb_rank']    = all_boroughs['airbnb_score'].rank(method='min').astype(int)
all_boroughs['housing_rank']   = all_boroughs['housing_score'].rank(method='min').astype(int)

# make a dict with the name of the borough as the key
all_boroughs = all_boroughs.set_index('name').to_dict('index')

all_listings = query_to_dataframe(knowledge_graph, GET_ALL_LISTINGS, ["name", "borough"]).to_dict('records')

with open("assets/london_boroughs.geojson") as f:
    GEOJSON = json.load(f)


end = time.time()
length = end - start
print("It took", length, "seconds to start the app!")

app.layout = html.Div(
    style={
        "display": "grid",
        "gridTemplateRows": "68% 32%",
        "height": "100vh",
        "boxSizing": "border-box",
    },
    children=[
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "18% 57% 25%",
                "minHeight": 0,
            },
            children=[
                filters_column.render(),
                map_column.render(all_boroughs),
                similarity_column.render(all_boroughs),
            ],
        ),

        selected_borough_panel.render(all_boroughs),
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

    return selected_borough_panel.render_selected_borough(all_boroughs, borough)

if __name__ == "__main__":
    app.run(debug=True)