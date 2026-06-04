from dash import Dash, html, Input, Output, callback
from components import map_column, filters_column, details_column, selected_borough_panel
import json
from rdflib import Graph
import time
from utilities.queries import GET_ALL_BOROUGHS
from utilities.knowledge_graph import query_to_dataframe

start = time.time()

app = Dash()

# Load listings once at startup — swap with your real data source.
# Each listing needs "lat", "lon", "name", "borough", and one key per indicator.
AIRBNB_LISTINGS = [
    {"lat": 51.5155, "lon": -0.0922, "name": "Cosy flat",          "borough": "Hackney"},
    {"lat": 51.5190, "lon": -0.0880, "name": "Victorian terrace",  "borough": "Hackney"},
    {"lat": 51.5210, "lon": -0.0950, "name": "Studio flat",        "borough": "Hackney"},
    {"lat": 51.5074, "lon": -0.1278, "name": "Central studio",     "borough": "Westminster"},
    {"lat": 51.5010, "lon": -0.1350, "name": "Soho apartment",     "borough": "Westminster"},
    {"lat": 51.5120, "lon": -0.1420, "name": "Marylebone flat",    "borough": "Westminster"},
    {"lat": 51.5200, "lon": -0.1000, "name": "Modern loft",        "borough": "Islington"},
    {"lat": 51.5230, "lon": -0.1050, "name": "Angel studio",       "borough": "Islington"},
    {"lat": 51.5260, "lon": -0.0980, "name": "Highbury room",      "borough": "Islington"},
    {"lat": 51.4900, "lon": -0.1450, "name": "Bright room",        "borough": "Lambeth"},
    {"lat": 51.4850, "lon": -0.1150, "name": "Brixton flat",       "borough": "Lambeth"},
    {"lat": 51.4870, "lon": -0.1230, "name": "Stockwell studio",   "borough": "Lambeth"},
    {"lat": 51.5050, "lon": -0.0800, "name": "Bermondsey spot",    "borough": "Southwark"},
    {"lat": 51.4980, "lon": -0.0750, "name": "Peckham studio",     "borough": "Southwark"},
    {"lat": 51.5020, "lon": -0.0820, "name": "Borough flat",       "borough": "Southwark"},
    {"lat": 51.5300, "lon": -0.1200, "name": "Camden townhouse",   "borough": "Camden"},
    {"lat": 51.5340, "lon": -0.1280, "name": "Kentish Town room",  "borough": "Camden"},
    {"lat": 51.5280, "lon": -0.1150, "name": "Primrose Hill flat", "borough": "Camden"},
    {"lat": 51.5400, "lon": -0.0600, "name": "Stoke Newington",    "borough": "Hackney"},
    {"lat": 51.5370, "lon": -0.0430, "name": "Dalston double",     "borough": "Hackney"},
    {"lat": 51.5100, "lon": -0.1900, "name": "Notting Hill flat",  "borough": "Kensington and Chelsea"},
    {"lat": 51.4950, "lon": -0.1750, "name": "Earls Court studio", "borough": "Kensington and Chelsea"},
    {"lat": 51.5080, "lon": -0.1960, "name": "Holland Park room",  "borough": "Kensington and Chelsea"},
    {"lat": 51.5250, "lon": -0.0750, "name": "Hoxton loft",        "borough": "Hackney"},
    {"lat": 51.5350, "lon": -0.1450, "name": "Fitzrovia flat",     "borough": "Camden"},
    {"lat": 51.5450, "lon": -0.0200, "name": "Clapton terrace",    "borough": "Hackney"},
    {"lat": 51.5150, "lon": -0.0400, "name": "Bethnal Green flat", "borough": "Tower Hamlets"},
    {"lat": 51.5080, "lon": -0.0560, "name": "Whitechapel flat",   "borough": "Tower Hamlets"},
    {"lat": 51.5060, "lon": -0.0490, "name": "Stepney studio",     "borough": "Tower Hamlets"},
    {"lat": 51.4990, "lon": -0.2100, "name": "Hammersmith flat",   "borough": "Hammersmith and Fulham"},
    {"lat": 51.5130, "lon": -0.2200, "name": "Shepherd's Bush",    "borough": "Hammersmith and Fulham"},
    {"lat": 51.4760, "lon": -0.1550, "name": "Balham room",        "borough": "Wandsworth"},
    {"lat": 51.4630, "lon": -0.1400, "name": "Tooting double",     "borough": "Wandsworth"},
    {"lat": 51.4700, "lon": -0.1700, "name": "Streatham flat",     "borough": "Lambeth"},
    {"lat": 51.5560, "lon": -0.1050, "name": "Archway flat",       "borough": "Islington"},
    {"lat": 51.5500, "lon": -0.0900, "name": "Finsbury Park room", "borough": "Islington"},
]

# Load RDF graph
knowledge_graph = Graph()
knowledge_graph.parse("assets/london_airbnb_kg.ttl", format="turtle")

all_boroughs = query_to_dataframe(knowledge_graph, GET_ALL_BOROUGHS, ["name"])
# make a list of the name of the borough the key
all_boroughs = all_boroughs.set_index('name').to_dict('index')

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
                details_column.render(),
            ],
        ),

        selected_borough_panel.render(),
    ],
)
def filter_listings(listings, transport_levels, pressure_levels, housing_levels):
    """
    Keep listings whose borough's indicators match all enabled levels.
    Indicator values are looked up from map_column.BOROUGH_DATA, not stored
    on the listing itself.
    """
    borough_data = map_column.BOROUGH_DATA
    return [
        l for l in listings
        if (row := borough_data.get(l["borough"])) is not None
        and row["transportation_indicator"]  in (transport_levels or [])
        and row["airbnb_pressure_indicator"] in (pressure_levels  or [])
        and row["housing_indicator"]         in (housing_levels   or [])
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

    visible = filter_listings(AIRBNB_LISTINGS, transport_levels, pressure_levels, housing_levels)

    fig = map_column.build_figure(all_boroughs, GEOJSON, indicator, visible, zoom=zoom, center=center)
    overlay_children = map_column.build_cooccurrence_overlay(all_boroughs, indicator).children
    return fig, overlay_children


@callback(
    Output("selected-borough-panel", "children"),
    Input("choropleth-map", "clickData"),
)
def update_selected_borough_panel(clickData):
    if not clickData:
        return selected_borough_panel.render_selected_borough()

    borough = clickData["points"][0].get("location")

    if not borough:
        return selected_borough_panel.render_selected_borough()

    return selected_borough_panel.render_selected_borough(borough)

if __name__ == "__main__":
    app.run(debug=True)