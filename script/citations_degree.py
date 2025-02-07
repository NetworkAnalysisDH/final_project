import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Load data from the JSON file
with open ("data/publications.json", "r") as file:
    data = json.load(file)

# Create the graph (citation network)
G = nx.DiGraph()  

# Add nodes and connections (internal citations based on authors)
for i, publication in enumerate(data['publications']):
    if 'title' not in publication or 'author' not in publication:
        continue  # Skip if title or author is missing
    title = publication['title']
    authors = publication['author']
    G.add_node(title, authors=authors)

    for j, other_publication in enumerate(data['publications']):
        if i != j:  # Avoid self-citations
            if 'title' not in other_publication or 'author' not in other_publication:
                continue  # Skip if title or author is missing
            other_title = other_publication['title']
            other_authors = other_publication['author']
            if len(set(authors) & set(other_authors)) >= 2:  # At least 2 common authors
                G.add_edge(title, other_title)

# Calculate degree centrality (in-degree and out-degree)
in_degree_centrality = nx.in_degree_centrality(G)
out_degree_centrality = nx.out_degree_centrality(G)

# Combine in-degree and out-degree centrality into a single DataFrame
degree_centrality_df = pd.DataFrame({
    'Title': list(in_degree_centrality.keys()),
    'In-Degree Centrality': list(in_degree_centrality.values()),
    'Out-Degree Centrality': list(out_degree_centrality.values())
})

# Sort by in-degree centrality and get the top 15
top_15_degree = degree_centrality_df.sort_values(by='In-Degree Centrality', ascending=False).head(15)

# Save the top 15 results to a CSV file
top_15_degree.to_csv('top_15_degree_centrality_results.csv', index=False)

# Visualization of the top 15 nodes based on degree centrality
titles = top_15_degree['Title'].tolist()  # Top 15 titles
G_subgraph = G.subgraph(titles)  # Create a subgraph with the top 15 nodes

# Calculate the number of citations for each node (number of incoming edges)
citation_counts = {node: G.in_degree(node) for node in G_subgraph.nodes()}

# Layout to organize the nodes aesthetically
pos = nx.spring_layout(G_subgraph, seed=42)

# Increase the figure size
plt.figure(figsize=(15, 12))  # Larger size for the titles

# Draw nodes with custom colors
node_colors = []
for node in G_subgraph.nodes():
    authors = G_subgraph.nodes[node]['authors']
    # If the node has the most citations, color it pink
    if citation_counts[node] == max(citation_counts.values()):
        node_colors.append('pink')  # Pink for the most cited papers
    else:
        node_colors.append('blue')  # Blue for other nodes

# Draw nodes
node_size = [5000 * in_degree_centrality[node] for node in G_subgraph.nodes()]
nx.draw_networkx_nodes(G_subgraph, pos, node_size=node_size, node_color=node_colors, alpha=0.7)

# Draw edges without labels
nx.draw_networkx_edges(G_subgraph, pos, width=2, alpha=0.5, edge_color='gray')

# Draw node labels (the titles of the papers)
nx.draw_networkx_labels(G_subgraph, pos, font_size=7, font_weight='bold', font_color='black')  # Increased font_size

# Add title to the graph
plt.title("Citation Network - Degree Centrality (Top 15)", size=20)  # Increased title size

plt.axis('off')  # Removes axes
plt.savefig('degree_centrality_visualization.png')  # Save the visualization as a PNG file
plt.show()  # Display the visualization