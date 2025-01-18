import json
import networkx as nx
import os

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
            G.add_edge(author1, author2)

# Calculate network measures
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
closeness_centrality = nx.closeness_centrality(G)
eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
clustering_coefficient = nx.clustering(G)

# Output directory
output_dir = 'network'

# Annotate nodes with each centrality measure and export to GraphML
def annotate_and_save(graph, measure_dict, filename):
    nx.set_node_attributes(graph, measure_dict, 'value')
    file_path = os.path.join(output_dir, f'projects_{filename}')
    nx.write_graphml(graph, file_path)
    print(f"Graph saved to {file_path}")

annotate_and_save(G, degree_centrality, 'degree_centrality.graphml')
annotate_and_save(G, betweenness_centrality, 'betweenness_centrality.graphml')
annotate_and_save(G, closeness_centrality, 'closeness_centrality.graphml')
annotate_and_save(G, eigenvector_centrality, 'eigenvector_centrality.graphml')
annotate_and_save(G, clustering_coefficient, 'clustering_coefficient.graphml')

print("All files have been saved successfully!")