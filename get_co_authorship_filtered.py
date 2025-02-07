import json
import networkx as nx
import pandas as pd
import os

# Define relative paths
network_dir = "network/co_authorship_filtered/"
report_dir = "report/co_authorship_filtered/"

# Ensure output directories exist
os.makedirs(network_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)

# Load the publication network
gml_file_path = "network/co_authorship/coauthorship_network.gml"
G_pub = nx.read_gml(gml_file_path)

# Load the JSON file with project authors
authors_file_path = "data/authors.json"

with open(authors_file_path, "r", encoding="utf-8") as f:
    authors_data = json.load(f)

# Extract the names of project network authors
project_authors = {author["name"] for author in authors_data["members"]}

# Create a subgraph from the publication network containing only project authors
G_pub_filtered_by_projects = G_pub.subgraph(project_authors).copy()

# Save the filtered network in GML format
filtered_gml_path = os.path.join(network_dir, "coauthorship_network_filtered_by_projects.gml")
nx.write_gml(G_pub_filtered_by_projects, filtered_gml_path)
print(f"Filtered GML saved to: {filtered_gml_path}")

# Compute network metrics
def compute_metrics(G, filename_prefix):
    """Compute network centrality metrics and save them to CSV."""
    if G.number_of_nodes() == 0:
        print("No nodes in the filtered network. Skipping metric computation.")
        return
    
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
    print(f"Metrics saved to: {csv_filename}")

# Compute and save metrics for the filtered publication network
compute_metrics(G_pub_filtered_by_projects, "coauthorship_filtered_by_projects")

print("Filtered GML and metric report successfully generated.")