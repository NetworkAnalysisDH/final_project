import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Load data from the JSON file
with open ("date/publications.json", "r") as file:
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
                continue
            other_title = other_publication['title']
            other_authors = other_publication['author']
            if len(set(authors) & set(other_authors)) >= 1:  # decreased to at least 1 common authors
                G.add_edge(title, other_title)

# Remove isolated nodes
G.remove_nodes_from(list(nx.isolates(G)))

# Convert to undirected graph for betweenness centrality
G_undirected = G.to_undirected()

# Calculate betweenness centrality
betweenness_centrality = nx.betweenness_centrality(G_undirected)

# Convert to DataFrame and sort by centrality
betweenness_df = pd.DataFrame({
    'Title': list(betweenness_centrality.keys()),
    'Betweenness Centrality': list(betweenness_centrality.values())
})

# Filter top 15 nodes
top_15_betweenness = betweenness_df.sort_values(by='Betweenness Centrality', ascending=False).head(15)

# Save to CSV
top_15_betweenness.to_csv('top_15_betweenness_centrality_results_citations.csv', index=False)

# Visualization of the top 15 nodes
titles = top_15_betweenness['Title'].tolist()
G_subgraph = G_undirected.subgraph(titles)

# Layout and styling
pos = nx.spring_layout(G_subgraph, seed=42)
plt.figure(figsize=(15, 12))

# Node colors/sizes based on betweenness centrality
node_colors = 'green'  # Single color for simplicity
node_size = [15000 * betweenness_centrality[node] for node in G_subgraph.nodes()]

# Draw elements
nx.draw_networkx_nodes(G_subgraph, pos, node_size=node_size, node_color=node_colors, alpha=0.7)
nx.draw_networkx_edges(G_subgraph, pos, width=2, alpha=0.5, edge_color='gray')
nx.draw_networkx_labels(G_subgraph, pos, font_size=7, font_weight='bold', font_color='black')

# Title and save
plt.title("Citation Network - Betweenness Centrality (Top 15)", size=20)
plt.axis('off')
plt.savefig('betweenness_centrality_visualization_citation.png')
plt.show()