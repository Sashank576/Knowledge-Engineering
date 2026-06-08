from dash import html, dcc
import plotly.graph_objects as go
import networkx as nx

def _build_graph(edges_df):
    G = nx.Graph()

    # Option 1: Use cutoff value
    # Pro: clusters and lone nodes are very distinct
    # Con: the idea that closer nodes rae most similar does not really apply anymore
    edges_df = edges_df[edges_df["similarity"] >= 0.5]
    # ^^^ Do not consider negative similarities when building the graph to improve layout

    for _, row in edges_df.iterrows():
        G.add_edge(
            row["from_borough"],
            row["to_borough"],
            weight=row["similarity"]
        )

    # Mainly change this to change at which places the nodes get shown
    pos = nx.spring_layout(G, seed=7, weight="weight", k=10, iterations=575, scale=3)

    # # Option 2: Build the node layout based on top-x most similar boroughs (nearest neighbors)
    # # Pro: will conserve the idea that closer nodes are most similar
    # # Con: will make it that even some nodes with 0 edges will still be part of a cluster
    # edges_df = (
    #     edges_df
    #     .sort_values("similarity", ascending=False)
    #     .groupby("from_borough")
    #     .head(4)
    # )
    #
    # for _, row in edges_df.iterrows():
    #     G.add_edge(
    #         row["from_borough"],
    #         row["to_borough"],
    #         weight=row["similarity"]
    #     )
    #
    # pos = nx.spring_layout(G, weight="weight", seed=7, k=7, iterations=500, scale=3)
    return G, pos

def build_similarity_figure(edges_df, threshold):
    G, pos = _build_graph(edges_df)

    # Filter edges by similarity threshold
    filtered = edges_df[edges_df["similarity"] >= threshold]

    edge_traces = []

    for _, row in filtered.iterrows():
        a, b = row["from_borough"], row["to_borough"]
        sim = row["similarity"]

        x0, y0 = pos[a]
        x1, y1 = pos[b]

        # normalize similarity within visible range
        sim_norm = (sim - threshold) / (1 - threshold)
        sim_norm = max(0, min(1, sim_norm))

        # opacity mapping (keep edges subtle)
        opacity = 0.10 + 0.50 * sim_norm

        edge_traces.append(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                hoverinfo="none",
                line=dict(
                    width=1.0 + 1.5 * sim_norm,
                    color=f"rgba(80, 80, 80, {opacity})"
                ),
                showlegend=False,
            )
        )

    # node degrees (based on filtered graph)
    degree = {n: 0 for n in G.nodes()}
    for _, row in filtered.iterrows():
        degree[row["from_borough"]] += 1
        degree[row["to_borough"]] += 1

    node_x, node_y, node_text, node_size = [], [], [], []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        d = degree[node]
        node_size.append(5 + d * 2)
        node_text.append(f"{node}<br>Connections: {d}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(G.nodes()),
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",

        # Identify clicked point (link to selected_borough_panel.py)
        customdata=list(G.nodes()),

        marker=dict(
            size=node_size,
            color="royalblue",
            line=dict(width=1, color="black"),
        ),
    )

    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=30, b=0),
    )

    return fig

def render(all_boroughs, rq4_similarity):
    return html.Div(
        style={
            "height": "100%",
            "borderLeft": "1px solid #e0e0e0",
            "display": "flex",
            "flexDirection": "column",
        },
        children=[
            html.Div(
                style={
                    "padding": "10px 16px",
                    "borderBottom": "1px solid #e0e0e0",
                    "fontWeight": "600",
                    "fontSize": "13px",
                },
                children="Borough similarity",
            ),

            # Slider
            dcc.Slider(
                id="similarity-threshold-slider",
                min=0.90,
                max=1.00,
                step=0.01,
                value=0.90,
                marks={0.9: "0.9", 1.0: "1.0"},
            ),

            # Graph
            dcc.Graph(
                id="similarity-graph",
                style={"flex": "1"},
            ),
        ],
    )