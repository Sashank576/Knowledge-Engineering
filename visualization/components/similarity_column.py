from dash import html
import dash_cytoscape as cyto
from components.map_column import BOROUGH_DATA

INDICATORS = [
    "transportation_indicator",
    "airbnb_pressure_indicator",
    "housing_indicator",
]

MATCH_WEIGHTS = {3: 10, 2: 5, 1: 1}
MIN_WEIGHT = 2  # only show boroughs sharing 2+ indicators — keeps edge count manageable


def _build_elements():
    boroughs = list(BOROUGH_DATA.keys())
    nodes = [{"data": {"id": b, "label": b}} for b in boroughs]
    edges = []
    for i, a in enumerate(boroughs):
        for b in boroughs[i + 1:]:
            matches = sum(
                BOROUGH_DATA[a][ind] == BOROUGH_DATA[b][ind]
                for ind in INDICATORS
            )
            weight = MATCH_WEIGHTS.get(matches, 0)
            if weight >= MIN_WEIGHT:
                edges.append({
                    "data": {
                        "source":  a,
                        "target":  b,
                        "weight":  weight,
                        "matches": matches,
                    }
                })
    return nodes + edges


def _edge_color(matches):
    return {3: "#6366f1", 2: "#94a3b8", 1: "#e2e8f0"}.get(matches, "#e2e8f0")


STYLESHEET = [
    {
        "selector": "node",
        "style": {
            "label":            "data(label)",
            "font-size":        "8px",
            "text-valign":      "center",
            "text-halign":      "center",
            "text-wrap":        "wrap",
            "text-max-width":   "60px",
            "width":            "50px",
            "height":           "50px",
            "background-color": "#475569",
            "color":            "#fff",
            "border-width":     "2px",
            "border-color":     "#1e293b",
        },
    },
    {
        "selector": "node:selected",
        "style": {
            "background-color": "#6366f1",
            "border-color":     "#4338ca",
            "border-width":     "3px",
        },
    },
    *[
        {
            "selector": f"edge[matches = {m}]",
            "style": {
                "line-color":  _edge_color(m),
                "width":       MATCH_WEIGHTS[m] / 3,
                "opacity":     0.4 + m * 0.15,
                "curve-style": "bezier",
            },
        }
        for m in [1, 2, 3]
    ],
]


def render():
    return html.Div(
        style={
            "height":        "100%",
            "borderLeft":    "1px solid #e0e0e0",
            "display":       "flex",
            "flexDirection": "column",
        },
        children=[
            html.Div(
                style={
                    "padding":        "10px 16px",
                    "borderBottom":   "1px solid #e0e0e0",
                    "flexShrink":     "0",
                    "display":        "flex",
                    "alignItems":     "center",
                    "justifyContent": "space-between",
                },
                children=[
                    html.Span("Borough similarity", style={
                        "fontWeight": "600",
                        "fontSize":   "13px",
                        "color":      "#333",
                    }),
                    html.Button(
                        "↺ Reset layout",
                        id="reset-layout-btn",
                        n_clicks=0,
                        style={
                            "fontSize":       "11px",
                            "padding":        "4px 10px",
                            "border":         "1px solid #cbd5e1",
                            "borderRadius":   "4px",
                            "backgroundColor":"#fff",
                            "cursor":         "pointer",
                            "color":          "#555",
                        }
                    ),
                ]
            ),
            cyto.Cytoscape(
                id="borough-graph",
                elements=_build_elements(),
                layout={
                    "name":              "cose",
                    "animate":           False,  # compute fully before rendering — no timing issues
                    "randomize":         True,
                    "nodeDimensionsIncludeLabels": True,
                    "idealEdgeLength":   100,
                    "nodeOverlap":       20,
                    "nodeRepulsion":     400000,
                    "edgeElasticity":    100,
                    "nestingFactor":     5,
                    "gravity":           80,
                    "numIter":           1000,
                    "fit":               True,
                    "padding":           30,
                    "componentSpacing":  100,
                },
                stylesheet=STYLESHEET,
                style={"flex": "1"},
                minZoom=0.2,
                maxZoom=3.0,
            ),
        ]
    )