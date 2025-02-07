import json
import networkx as nx
import pandas as pd
import os

# Define relative paths
network_dir = "network/co_authorship/"
report_dir = "report/co_authorship/"

# Ensure output directories exist
os.makedirs(network_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)

# Load publication data
publications_file = os.path.join("data/publications.json")

with open(publications_file, "r", encoding="utf-8") as f:
    publications_data = json.load(f)

# Create an undirected graph
G = nx.Graph()

# Build the co-authorship network
for publication in publications_data["publications"]:
    authors = publication.get("author", [])
    
    # Create an edge between each pair of authors
    for i in range(len(authors)):
        for j in range(i + 1, len(authors)):
            if G.has_edge(authors[i], authors[j]):
                G[authors[i]][authors[j]]["weight"] += 1
            else:
                G.add_edge(authors[i], authors[j], weight=1)

# Save the full co-authorship network in GML format
nx.write_gml(G, os.path.join(network_dir, "coauthorship_network.gml"))

# Create a subgraph with only collaborations of at least 3 publications
G_filtered = nx.Graph([(u, v, d) for u, v, d in G.edges(data=True) if d["weight"] >= 3])

# Save the filtered network in GML format
nx.write_gml(G_filtered, os.path.join(network_dir, "coauthorship_network_filtered.gml"))

# Compute network metrics for both graphs
def compute_metrics(G, filename):
    """Compute network centrality metrics and save them to a CSV file."""
    metrics = {
        "Author": list(G.nodes()),
        "Degree Centrality": list(nx.degree_centrality(G).values()),
        "Betweenness Centrality": list(nx.betweenness_centrality(G).values()),
        "Closeness Centrality": list(nx.closeness_centrality(G).values()),
        "Eigenvector Centrality": list(nx.eigenvector_centrality(G, max_iter=1000).values()),
        "Clustering Coefficient": list(nx.clustering(G).values()),
    }

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(metrics)
    df.to_csv(filename, index=False)
    print(f"Metrics saved to {filename}")

# Compute and save metrics for both networks
compute_metrics(G, os.path.join(report_dir, "coauthorship_metrics_full.csv"))
compute_metrics(G_filtered, os.path.join(report_dir, "coauthorship_metrics_filtered.csv"))

print("GML files and metric CSVs successfully generated.")