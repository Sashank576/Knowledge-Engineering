from dash import html, dcc
import plotly.graph_objects as go
import json
from collections import Counter, defaultdict

# Data lives here — swap for a real source if needed
BOROUGH_DATA = {
    "City of London":        {"transportation_indicator": "low",    "airbnb_pressure_indicator": "low",    "housing_indicator": "high"},
    "Barking and Dagenham":  {"transportation_indicator": "medium", "airbnb_pressure_indicator": "high",   "housing_indicator": "medium"},
    "Barnet":                {"transportation_indicator": "medium", "airbnb_pressure_indicator": "medium", "housing_indicator": "high"},
    "Bexley":                {"transportation_indicator": "low",    "airbnb_pressure_indicator": "low",    "housing_indicator": "medium"},
    "Brent":                 {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Bromley":               {"transportation_indicator": "medium", "airbnb_pressure_indicator": "low",    "housing_indicator": "medium"},
    "Camden":                {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Croydon":               {"transportation_indicator": "medium", "airbnb_pressure_indicator": "medium", "housing_indicator": "high"},
    "Ealing":                {"transportation_indicator": "high",   "airbnb_pressure_indicator": "medium", "housing_indicator": "medium"},
    "Enfield":               {"transportation_indicator": "low",    "airbnb_pressure_indicator": "medium", "housing_indicator": "medium"},
    "Greenwich":             {"transportation_indicator": "medium", "airbnb_pressure_indicator": "medium", "housing_indicator": "medium"},
    "Hackney":               {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Hammersmith and Fulham":{"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Haringey":              {"transportation_indicator": "medium", "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Harrow":                {"transportation_indicator": "medium", "airbnb_pressure_indicator": "medium", "housing_indicator": "medium"},
    "Havering":              {"transportation_indicator": "low",    "airbnb_pressure_indicator": "low",    "housing_indicator": "low"},
    "Hillingdon":            {"transportation_indicator": "medium", "airbnb_pressure_indicator": "medium", "housing_indicator": "medium"},
    "Hounslow":              {"transportation_indicator": "high",   "airbnb_pressure_indicator": "medium", "housing_indicator": "medium"},
    "Islington":             {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Kensington and Chelsea":{"transportation_indicator": "high",   "airbnb_pressure_indicator": "medium", "housing_indicator": "high"},
    "Kingston upon Thames":  {"transportation_indicator": "medium", "airbnb_pressure_indicator": "low",    "housing_indicator": "medium"},
    "Lambeth":               {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Lewisham":              {"transportation_indicator": "medium", "airbnb_pressure_indicator": "medium", "housing_indicator": "high"},
    "Merton":                {"transportation_indicator": "medium", "airbnb_pressure_indicator": "low",    "housing_indicator": "medium"},
    "Newham":                {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Redbridge":             {"transportation_indicator": "medium", "airbnb_pressure_indicator": "medium", "housing_indicator": "medium"},
    "Richmond upon Thames":  {"transportation_indicator": "medium", "airbnb_pressure_indicator": "low",    "housing_indicator": "medium"},
    "Southwark":             {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Sutton":                {"transportation_indicator": "low",    "airbnb_pressure_indicator": "low",    "housing_indicator": "low"},
    "Tower Hamlets":         {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
    "Waltham Forest":        {"transportation_indicator": "medium", "airbnb_pressure_indicator": "medium", "housing_indicator": "high"},
    "Wandsworth":            {"transportation_indicator": "high",   "airbnb_pressure_indicator": "medium", "housing_indicator": "high"},
    "Westminster":           {"transportation_indicator": "high",   "airbnb_pressure_indicator": "high",   "housing_indicator": "high"},
}

ALL_INDICATORS = ["transportation_indicator", "airbnb_pressure_indicator", "housing_indicator"]

INDICATOR_LABELS = {
    "transportation_indicator":   "Transport",
    "airbnb_pressure_indicator":  "Airbnb Pressure",
    "housing_indicator":          "Housing",
}

LEVEL_COLORS = {
    "low":    "#4caf50",
    "medium": "#f5a623",
    "high":   "#f44336",
}

# One trace per level — order here = legend order, guaranteed
LEVELS = [
    ("low",    "#4caf50", "Low"),
    ("medium", "#ffeb3b", "Medium"),
    ("high",   "#f44336", "High"),
]


def build_cooccurrence_overlay(indicator: str) -> html.Div:
    """
    For boroughs where `indicator` == 'high', count how the OTHER
    two indicators are distributed across low / medium / high.
    """
    other_indicators = [i for i in ALL_INDICATORS if i != indicator]

    # Collect only the high-pressure boroughs
    high_boroughs = [
        data for data in BOROUGH_DATA.values()
        if data.get(indicator) == "high"
    ]
    total = len(high_boroughs)

    if total == 0:
        return html.Div()

    def level_pill(level: str, count: int, total: int) -> html.Span:
        return html.Span(
            f"{level.capitalize()} {count}/{total}",
            style={
                "backgroundColor": LEVEL_COLORS[level],
                "color": "#fff" if level in ("high", "medium") else "#333",
                "borderRadius": "4px",
                "padding": "1px 7px",
                "fontSize": "11px",
                "fontWeight": "600",
                "marginRight": "4px",
            }
        )

    rows = []
    for ind in other_indicators:
        counts = Counter(b[ind] for b in high_boroughs)
        pills = [
            level_pill(lvl, counts.get(lvl, 0), total)
            for lvl in ["low", "medium", "high"]
            if counts.get(lvl, 0) > 0
        ]
        rows.append(html.Div(
            style={"marginBottom": "6px"},
            children=[
                html.Span(
                    INDICATOR_LABELS[ind],
                    style={
                        "fontSize": "11px",
                        "color": "#555",
                        "display": "block",
                        "marginBottom": "3px",
                    }
                ),
                html.Div(pills),
            ]
        ))

    return html.Div(
        id="cooccurrence-overlay",
        style={
            "position": "absolute",
            "top": "12px",
            "left": "12px",
            "zIndex": 999,
            "backgroundColor": "rgba(255,255,255,0.92)",
            "borderRadius": "8px",
            "padding": "10px 14px",
            "boxShadow": "0 1px 6px rgba(0,0,0,0.15)",
            "minWidth": "190px",
            "pointerEvents": "none",  # don't block map interactions
        },
        children=[
            html.Div(
                style={
                    "fontSize": "11px",
                    "fontWeight": "700",
                    "color": "#333",
                    "marginBottom": "8px",
                    "borderBottom": "1px solid #eee",
                    "paddingBottom": "6px",
                },
                children=[
                    html.Span("Indicator co-occurrence for"),
                    html.Br(),
                    html.Span(f"high {INDICATOR_LABELS[indicator].lower()} boroughs ({total})"),
                ]
            ),
            *rows,
        ]
    )



# Zoom level at which we switch from borough clusters to individual dots
INDIVIDUAL_ZOOM_THRESHOLD = 13


def cluster_listings(listings: list[dict], zoom: float) -> list[dict]:
    """
    Borough-based clustering. Below INDIVIDUAL_ZOOM_THRESHOLD all listings in
    the same borough are collapsed into one dot placed at their centroid, sized
    by count. Above the threshold every listing is shown individually.
    Each listing dict must have "lat", "lon", and "borough" keys.
    """
    if zoom >= INDIVIDUAL_ZOOM_THRESHOLD:
        return [
            {
                "lat":  l["lat"],
                "lon":  l["lon"],
                "text": l.get("name", "Airbnb listing"),
                "size": 6,
            }
            for l in listings
        ]

    buckets: dict[str, list] = defaultdict(list)
    for l in listings:
        buckets[l.get("borough", "Unknown")].append(l)

    points = []
    for borough, members in buckets.items():
        avg_lat = sum(m["lat"] for m in members) / len(members)
        avg_lon = sum(m["lon"] for m in members) / len(members)
        count   = len(members)
        # Scale dot size: min 12 for small clusters, up to 40 for large ones
        size = min(12 + (count ** 0.4) * 3, 40)
        points.append({
            "lat":  avg_lat,
            "lon":  avg_lon,
            "text": str(count),
            "size": size,
        })

    return points

def build_figure(geojson, indicator: str, airbnb_listings: list[dict] | None = None, zoom: float = 9, center: dict | None = None):
    """
    airbnb_listings: list of dicts with keys "lat", "lon", and optionally "name"
    e.g. [{"lat": 51.51, "lon": -0.12, "name": "Cosy flat in Hackney"}, ...]
    """
    # Bucket boroughs by level
    buckets = {"low": [], "medium": [], "high": []}
    for feature in geojson["features"]:
        name = feature["properties"]["name"]
        row = BOROUGH_DATA.get(name)
        if row is None:
            continue
        level = row.get(indicator, "low")
        buckets[level].append(name)

    fig = go.Figure()

    for level, colour, label in LEVELS:
        boroughs = buckets[level]
        fig.add_trace(
            go.Choroplethmapbox(
                name=label,
                geojson=geojson,
                locations=boroughs,
                featureidkey="properties.name",
                # z must be supplied; use a constant so the colorscale is irrelevant
                z=[0] * len(boroughs),
                colorscale=[[0, colour], [1, colour]],
                showscale=False,
                marker_opacity=1,            # opacity of the boroughs
                marker_line_width=1,         # thickness of the line between the boroughs
                marker_line_color="#000000", # color of the line between the boroughs
                hovertemplate="<b>%{location}</b><br>"
                              + indicator.replace("_", " ").title()
                              + f": {label}<extra></extra>",
                showlegend=True,
            )
        )

    # Airbnb listings dot layer — pass airbnb_listings to enable
    if airbnb_listings:
        points = cluster_listings(airbnb_listings, zoom)
        is_clustered = zoom < INDIVIDUAL_ZOOM_THRESHOLD

        lats   = [p["lat"]   for p in points]
        lons   = [p["lon"]   for p in points]
        texts  = [p["text"]  for p in points]
        sizes  = [p["size"]  for p in points]

        fig.add_trace(
            go.Scattermapbox(
                name="Airbnb listings",
                lat=lats,
                lon=lons,
                mode="markers+text" if is_clustered else "markers",
                marker=dict(
                    size=sizes,
                    color="#0077ff",   # blue
                    opacity=0.7,
                ),
                text=texts,
                textfont=dict(size=10, color="#fff"),
                textposition="middle center",
                hovertemplate=(
                    "<b>%{text} listings</b><extra></extra>"
                    if is_clustered else
                    "<b>%{text}</b><br>%{lat:.4f}, %{lon:.4f}<extra></extra>"
                ),
                showlegend=True,
            )
        )

    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_zoom=zoom,
        mapbox_center=center if center else {"lat": 51.5074, "lon": -0.1278},
        # Force the layout to ignore all margins
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        # Ensure the plot fills the available space
        autosize=True,
        # This prevents the legend from forcing a margin on the right side
        legend=dict(
            title=dict(text="Indicator"),
            bgcolor="rgba(255,255,255,0.8)",
            x=0.82,  # Move it to the left so it doesn't push the right boundary
            y=0.95
        ),
    )

    return fig


def render(indicator: str = "transportation_indicator"):
    with open("assets/london_boroughs.geojson") as f:
        geojson = json.load(f)

    fig = build_figure(geojson, indicator)

    return html.Div(
        # position: relative so the overlay can anchor absolutely inside it
        style={"height": "100%", "position": "relative"},
        children=[
            build_cooccurrence_overlay(indicator),
            dcc.Graph(
                id="choropleth-map",
                figure=fig,
                style={"height": "100%"},
                config={"scrollZoom": True},
            ),
        ]
    )