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

# Additional network analysis
def analyze_network(G):
    print("\n--- Network Analysis ---")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    print(f"Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes():.2f}")
    
    print("\n--- Centrality Measures ---")
    centrality_measures = {
        "Degree Centrality": degree_centrality,
        "Betweenness Centrality": betweenness_centrality,
        "Closeness Centrality": closeness_centrality,
        "Eigenvector Centrality": eigenvector_centrality
    }
    
    for measure_name, measure_dict in centrality_measures.items():
        print(f"\nTop 5 nodes by {measure_name}:")
        for node, score in sorted(measure_dict.items(), key=lambda x: -x[1])[:5]:
            print(f"{node}: {score:.4f}")
    
    print("\n--- Community Detection ---")
    partition = community_louvain.best_partition(G)
    modularity = community_louvain.modularity(partition, G)
    print(f"Modularity: {modularity:.4f}")
    print(f"Number of communities: {len(set(partition.values()))}")
    
    print("\n--- Cohesion and Structure ---")
    if nx.is_connected(G):
        print(f"Network diameter: {nx.diameter(G)}")
    else:
        print("The network is not connected.")
    
    print(f"Network density: {nx.density(G):.4f}")
    print(f"Number of connected components: {nx.number_connected_components(G)}")
    print(f"Average clustering coefficient: {nx.average_clustering(G):.4f}")
    print(f"Assortativity: {nx.degree_assortativity_coefficient(G):.4f}")

    return partition

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

def export_adjacency_matrix(G, filename):
    adj_matrix = nx.to_pandas_adjacency(G)
    adj_matrix.to_csv(filename)

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

def export_global_metrics(G, filename):
    global_metrics = pd.DataFrame({
        'Metric': ['Number of Nodes', 'Number of Edges', 'Average Degree', 'Density', 'Number of Connected Components', 'Average Clustering Coefficient', 'Assortativity'],
        'Value': [G.number_of_nodes(), G.number_of_edges(), sum(dict(G.degree()).values()) / G.number_of_nodes(), nx.density(G), nx.number_connected_components(G), nx.average_clustering(G), nx.degree_assortativity_coefficient(G)]
    })
    global_metrics.to_csv(filename, index=False)

# Output directories
network_dir = 'network'
report_dir = '/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/final_project/report'
os.makedirs(network_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)

# Analyze network
partition = analyze_network(G)

# Export files
export_to_graphml(G, f'{network_dir}/projects_author_collaboration_network.graphml')
export_adjacency_matrix(G, f'{report_dir}/projects_adjacency_matrix.csv')
export_node_metrics(G, f'{report_dir}/projects_node_metrics.csv')
export_global_metrics(G, f'{report_dir}/projects_global_metrics.csv')

print("All files have been saved successfully!")
