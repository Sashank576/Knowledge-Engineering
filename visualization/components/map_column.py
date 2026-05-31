from dash import html, dcc
import plotly.express as px
import pandas as pd
import random
import json

def render():
    with open("assets/london_boroughs.geojson") as f:
        geojson = json.load(f)

    # extract borough names for dummy data
    boroughs = [f["properties"]["name"] for f in geojson["features"]]


    df = pd.DataFrame({
        "borough": boroughs,
        "value": [random.randint(1, 100) for _ in boroughs]
    })

    # if we want google maps style
    # fig = px.choropleth_map(
    #     df,
    #     geojson=geojson,
    #     locations="borough",
    #     featureidkey="properties.name",
    #     color="value",
    #     map_style="carto-positron",
    #     zoom=9,
    #     center={"lat": 51.5074, "lon": -0.1278},
    #     color_continuous_scale="Blues",
    # )
    # fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    fig = px.choropleth_map(
        df,
        geojson=geojson,
        locations="borough",
        featureidkey="properties.name",
        color="value",
        map_style="white-bg",
        color_continuous_scale="Blues",
        zoom=8,
        center={"lat": 51.5074, "lon": -0.1278},
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},

    )

    return html.Div(
        style={'height': '100%'},
        children=[
            dcc.Graph(figure=fig, style={'height': '100%'})
        ]
    )