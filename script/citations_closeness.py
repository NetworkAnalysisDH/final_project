import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Load data from the JSON file
with open("data/publications.json", "r") as file:
    data = json.load(file)

# Create the graph (citation network)
G = nx.DiGraph()

# Add nodes and connections (edges for papers with ≥1 common authors)
for i, publication in enumerate(data["publications"]):
    if "title" not in publication or "author" not in publication:
        continue
    title = publication["title"]
    authors = publication["author"]
    G.add_node(title, authors=authors)

    for j, other_publication in enumerate(data["publications"]):
        if i != j:
            if "title" not in other_publication or "author" not in other_publication:
                continue
            other_title = other_publication["title"]
            other_authors = other_publication["author"]
            if len(set(authors) & set(other_authors)) >= 2:
                G.add_edge(title, other_title)

# Remove isolated nodes and convert to undirected graph
G.remove_nodes_from(list(nx.isolates(G)))
G_undirected = G.to_undirected()

# Calculate closeness centrality
closeness_centrality = nx.closeness_centrality(G_undirected)

# Convert to DataFrame and sort
closeness_df = pd.DataFrame(
    {
        "Title": list(closeness_centrality.keys()),
        "Closeness Centrality": list(closeness_centrality.values()),
    }
)

# Filter top 15
top_15_closeness = closeness_df.sort_values(
    by="Closeness Centrality", ascending=False
).head(15)

# Save to CSV
top_15_closeness.to_csv("top_15_closeness_centrality_citaions_results.csv", index=False)

# Visualization
titles = top_15_closeness["Title"].tolist()
G_subgraph = G_undirected.subgraph(titles)
pos = nx.spring_layout(G_subgraph, seed=42)
plt.figure(figsize=(15, 12))

node_size = [15000 * closeness_centrality[node] for node in G_subgraph.nodes()]
nx.draw_networkx_nodes(
    G_subgraph, pos, node_size=node_size, node_color="purple", alpha=0.7
)
nx.draw_networkx_edges(G_subgraph, pos, width=2, alpha=0.5, edge_color="gray")
nx.draw_networkx_labels(
    G_subgraph, pos, font_size=7, font_weight="bold", font_color="black"
)

plt.title("Citation Network - Closeness Centrality (Top 15)", size=20)
plt.axis("off")
plt.savefig("closeness_centrality_citaions_visualization.png")
plt.show()
