from dash import Dash, html, Input, Output, callback
from components import map_column, filters_column
import json

app = Dash()

app.layout = html.Div(
    style={
        "display": "grid",
        "gridTemplateColumns": "20% 50% 30%",
        "height": "100vh",
        "boxSizing": "border-box",
    },
    children=[
        filters_column.render(),
        map_column.render(),           # renders with default indicator on load
        html.Div("Details (30%)"),
    ],
)


@callback(
    Output("choropleth-map", "figure"),
    Input("indicator-dropdown", "value"),
)
def update_map(indicator):
    with open("assets/london_boroughs.geojson") as f:
        geojson = json.load(f)
    return map_column.build_figure(geojson, indicator)


if __name__ == "__main__":
    app.run(debug=True)