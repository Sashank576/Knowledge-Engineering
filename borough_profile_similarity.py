import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import plotly.graph_objects as go

# Load the file
# df = pd.read_csv("data/new_combined_aggregate_scores.csv")

# Standardize features (should be fine without, but just to be sure)
# features = df[["airbnb_pressure_score","housing_pressure_score","transport_pressure_score"]]
scaler = StandardScaler()
X = scaler.fit_transform(features)

# Calculate borough (cosine) similarity matrix
sim_matrix = cosine_similarity(X)

# Show the similarity matrix
sim_df = pd.DataFrame(sim_matrix, index=df["borough"], columns=df["borough"])
print(sim_df.round(3))

# Build the graph
G = nx.Graph()
boroughs = df["borough"].tolist()

# Add nodes for every borough
for borough in boroughs:
    G.add_node(borough)

# Add edges between every borough with similarity weight
for i in range(len(boroughs)):
    for j in range(i + 1, len(boroughs)):
        similarity = sim_matrix[i, j]
        # (Dis)Allow negative similarity
        G.add_edge(boroughs[i], boroughs[j], weight=similarity)
        # G.add_edge(boroughs[i], boroughs[j], weight=max(similarity, 0))

# Create a fixed layout (so node positions do not move with interactive slider)
# NOTE: Change the k and iterations to get different layout for the nodes.
# Could also try different layouts and change whether negative similarity is allowed
node_layout = nx.spring_layout(G, seed=7, weight="weight", k=10, iterations=600)

# Slider thresholds
slider_thresholds = [i / 100 for i in range(80, 101, 2)]
all_traces = []

for threshold in slider_thresholds:
    # Build filtered graph
    H = nx.Graph()
    H.add_nodes_from(G.nodes(data=True))

    for node_from, node_to, similarity_weight in G.edges(data=True):
        if similarity_weight["weight"] >= threshold:
            H.add_edge(node_from, node_to, **similarity_weight)

    # Edges
    edge_x = []
    edge_y = []

    for node_from, node_to in H.edges():
        x0, y0 = node_layout[node_from]
        x1, y1 = node_layout[node_to]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(
            width=2,
            color="lightgray"
        ),
        hoverinfo="none",
        visible=False
    )

    # Nodes
    degrees = dict(H.degree())

    node_x = []
    node_y = []
    node_text = []
    node_sizes = []

    for node in H.nodes():
        x, y = node_layout[node]

        node_x.append(x)
        node_y.append(y)

        # Scale node size by degree
        degree = degrees[node]
        node_sizes.append(10 + degree * 3)

        # Informative tooltip (when hovering over the node)
        node_text.append(
            f"{node}<br>"
            f"Degree: {degree}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(H.nodes()),
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(
            size=node_sizes,
            color="royalblue",
            line=dict(width=1, color="black")
        ),
        visible=False
    )

    all_traces.extend([edge_trace, node_trace])

# Show lowest threshold initially
all_traces[0].visible = True
all_traces[1].visible = True

# Show initial plot
fig = go.Figure(data=all_traces)

# Plot with slider thresholds
steps = []

for i, threshold in enumerate(slider_thresholds):
    visible = [False] * len(all_traces)

    # Each threshold contributes 2 traces: edge trace + node trace
    visible[2 * i] = True
    visible[2 * i + 1] = True

    step = dict(
        method="update",
        args=[
            {
                "visible": visible
            },
            {
                "title.text": (
                    f"Borough profile similarity graph "
                    f"(cosine similarity threshold = {threshold:.2f})"
                )
            }
        ],
        label=f"{threshold:.2f}"
    )

    steps.append(step)

fig.update_layout(
    title=f"Borough profile similarity graph (cosine similarity threshold = {slider_thresholds[0]:.2f})",
    showlegend=False,
    hovermode="closest",
    plot_bgcolor="white",

    # Remove x-axis and y-axis
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        visible=False
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        visible=False
    ),

    sliders=[
        dict(
            active=0,
            currentvalue={
                "prefix": "Cosine similarity threshold: "
            },
            pad={"t": 50},
            steps=steps
        )
    ]
)

fig.show()

# Add to csv
edges = []

for i, b1 in enumerate(sim_df.index):
    for j, b2 in enumerate(sim_df.columns):
        if i >= j:
            continue  # avoid duplicates + self-loops

        sim = sim_df.loc[b1, b2]
        edges.append([b1, b2, sim])

edges_df = pd.DataFrame(edges, columns=[
    "source",
    "target",
    "similarity"
])

import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.hist(edges_df["similarity"], bins=30, edgecolor="black", color="steelblue")
plt.xlabel("Similarity")
plt.ylabel("Frequency")
plt.title("Distribution of ProfileSimilarity Values")
plt.axvline(0, color="red", linestyle="--", linewidth=1, label="0 (no similarity)")
plt.legend()
plt.tight_layout()
plt.savefig("similarity_distribution.png", dpi=300)

edges_df.to_csv("data/borough_profile_similarity.csv", index=False)