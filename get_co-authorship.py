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

# Compute network metrics for graphs
def compute_metrics(G, filename_prefix):
    """Compute network centrality metrics and save them to CSV and GML files."""
    metrics = {
        "degree_centrality": nx.degree_centrality(G),
        "betweenness_centrality": nx.betweenness_centrality(G),
        "closeness_centrality": nx.closeness_centrality(G),
        "eigenvector_centrality": nx.eigenvector_centrality(G, max_iter=1000),
        "clustering_coefficient": nx.clustering(G),
    }

    # Convert the dictionary of dictionaries into a DataFrame
    df = pd.DataFrame(metrics)
    df.index.name = "Author"  # Set author names as index
    
    # Save DataFrame to CSV
    csv_filename = os.path.join(report_dir, f"{filename_prefix}_metrics.csv")
    df.to_csv(csv_filename)
    print(f"Metrics saved to {csv_filename}")

    # Generate a separate GML file for each metric
    for metric_name, values in metrics.items():
        G_metric = G.copy()

        # Assign the metric values as node attributes (ensuring valid key names)
        nx.set_node_attributes(G_metric, values, name=metric_name)

        # Save as GML file
        gml_filename = os.path.join(network_dir, f"{filename_prefix}_{metric_name}.gml")
        nx.write_gml(G_metric, gml_filename)
        print(f"GML file saved: {gml_filename}")

# Compute and save metrics for both networks
compute_metrics(G, "coauthorship_full")

print("GML files and metric CSVs successfully generated.")