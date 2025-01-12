import json
import networkx as nx
import os
import pandas as pd
import matplotlib.pyplot as plt
from community import community_louvain

# Load data using relative paths
with open('data/authors.json', 'r') as f:
    authors_data = json.load(f)

with open('data/projects.json', 'r') as f:
    projects_data = json.load(f)

# Extract author names
author_names = [author['name'] for author in authors_data['members']]

# Count projects for each author
project_count = {author: 0 for author in author_names}

for project in projects_data['projects']:
    participants = project.get('participants', [])
    for author in participants:
        project_count[author] += 1

# Create a graph
G = nx.Graph()
for author, count in project_count.items():
    G.add_node(author, size=count)

# Add edges based on project participants
for project in projects_data['projects']:
    participants = project.get('participants', [])
    for i, author1 in enumerate(participants):
        for author2 in participants[i+1:]:
            if G.has_edge(author1, author2):
                G[author1][author2]['weight'] += 1
            else:
                G.add_edge(author1, author2, weight=1)

# Calculate network measures
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
closeness_centrality = nx.closeness_centrality(G)
eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
clustering_coefficient = nx.clustering(G)

# Export functions
def export_to_graphml(G, filename):
    # Add centrality measures as node attributes
    nx.set_node_attributes(G, degree_centrality, 'degree_centrality')
    nx.set_node_attributes(G, betweenness_centrality, 'betweenness_centrality')
    nx.set_node_attributes(G, closeness_centrality, 'closeness_centrality')
    nx.set_node_attributes(G, eigenvector_centrality, 'eigenvector_centrality')
    nx.set_node_attributes(G, clustering_coefficient, 'clustering_coefficient')
    
    # Add community as node attribute
    partition = community_louvain.best_partition(G)
    nx.set_node_attributes(G, partition, 'community')
    
    nx.write_graphml(G, filename)

def export_node_metrics(G, filename):
    node_metrics = pd.DataFrame({
        'Node': list(G.nodes()),
        'Degree': [G.degree(n) for n in G.nodes()],
        'Degree Centrality': [degree_centrality[n] for n in G.nodes()],
        'Betweenness Centrality': [betweenness_centrality[n] for n in G.nodes()],
        'Closeness Centrality': [closeness_centrality[n] for n in G.nodes()],
        'Eigenvector Centrality': [eigenvector_centrality[n] for n in G.nodes()],
        'Clustering Coefficient': [clustering_coefficient[n] for n in G.nodes()]
    })
    node_metrics.to_csv(filename, index=False)

def export_graph_for_measure(G, centrality_measure, filename, centrality_dict):
    # Set node sizes or colors based on the centrality measure
    node_sizes = [centrality_dict[node] * 1000 for node in G.nodes()]
    
    # Create a graph and plot it
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, font_size=10, node_color=node_sizes, cmap=plt.cm.Blues)
    plt.title(f"{centrality_measure} of Authors")
    plt.savefig(filename)
    plt.close()

def export_global_metrics(G, filename):
    # Calculate global network metrics
    density = nx.density(G)
    diameter = nx.diameter(G) if nx.is_connected(G) else "Inf"  # Only compute diameter if the graph is connected
    average_degree = sum(dict(G.degree()).values()) / len(G.nodes())
    average_clustering = nx.average_clustering(G)
    average_shortest_path_length = nx.average_shortest_path_length(G) if nx.is_connected(G) else "Inf"
    
    global_metrics = {
        'Density': density,
        'Diameter': diameter,
        'Average Degree': average_degree,
        'Average Clustering Coefficient': average_clustering,
        'Average Shortest Path Length': average_shortest_path_length
    }
    
    # Save global metrics to CSV
    global_metrics_df = pd.DataFrame(global_metrics, index=[0])
    global_metrics_df.to_csv(filename, index=False)

# Output directories
network_dir = 'network/social'
report_dir = 'report/social'
os.makedirs(network_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)

# Export graphs and metrics for each measure in .graphml format
export_to_graphml(G, f'{network_dir}/general_projects_author_collaboration_network.graphml')

# Export graph for each centrality measure as a .graphml file
G_degree_centrality = G.copy()
nx.set_node_attributes(G_degree_centrality, degree_centrality, 'degree_centrality')
export_to_graphml(G_degree_centrality, f'{network_dir}/degree_centrality_graph.graphml')

G_betweenness_centrality = G.copy()
nx.set_node_attributes(G_betweenness_centrality, betweenness_centrality, 'betweenness_centrality')
export_to_graphml(G_betweenness_centrality, f'{network_dir}/betweenness_centrality_graph.graphml')

G_closeness_centrality = G.copy()
nx.set_node_attributes(G_closeness_centrality, closeness_centrality, 'closeness_centrality')
export_to_graphml(G_closeness_centrality, f'{network_dir}/closeness_centrality_graph.graphml')

G_eigenvector_centrality = G.copy()
nx.set_node_attributes(G_eigenvector_centrality, eigenvector_centrality, 'eigenvector_centrality')
export_to_graphml(G_eigenvector_centrality, f'{network_dir}/eigenvector_centrality_graph.graphml')

G_clustering_coefficient = G.copy()
nx.set_node_attributes(G_clustering_coefficient, clustering_coefficient, 'clustering_coefficient')
export_to_graphml(G_clustering_coefficient, f'{network_dir}/clustering_coefficient_graph.graphml')

# Export node metrics CSV
export_node_metrics(G, f'{report_dir}/projects_node_metrics.csv')

# Export global metrics CSV
export_global_metrics(G, f'{report_dir}/projects_global_metrics.csv')

print("All files have been saved successfully!")
