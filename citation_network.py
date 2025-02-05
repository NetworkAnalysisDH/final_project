import json
import networkx as nx
import matplotlib.pyplot as plt
from tabulate import tabulate  # Import tabulate

# Load data from the JSON file
with open("data/publications.json", "r") as file:
    data = json.load(file)

# Create the graph (citation network)
G = nx.DiGraph()  # Directed graph, since citations are directional

# Add nodes and connections (internal citations based on authors)
for i, publication in enumerate(data['publications']):
    # Check if the 'title' key exists
    if 'title' not in publication:
        continue  # Skip this publication if it doesn't have a 'title'

    title = publication['title']
    
    # Check if the 'author' key exists
    if 'author' not in publication:
        continue  # Skip this publication if it doesn't have 'author'
    
    authors = publication['author']
    
    # Add the node for the publication
    G.add_node(title, authors=authors)

    # Create connections only between papers that have at least 2 authors in common
    for j, other_publication in enumerate(data['publications']):
        if i != j:  # We don't want a paper to cite itself
            # Check if 'title' exists for the paper being compared
            if 'title' not in other_publication:
                continue  # Skip this publication if it doesn't have a 'title'

            if 'author' not in other_publication:
                continue  # Skip this publication if it doesn't have 'author'

            other_title = other_publication['title']
            other_authors = other_publication['author']

            # If there are at least 2 common authors, add a citation (an edge)
            if len(set(authors) & set(other_authors)) >= 2:  # If there are at least 2 common authors
                G.add_edge(title, other_title)

# Calculate eigenvector centrality
eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000, tol=1e-6)

# Analyze authors with the most publications
author_counts = {}
for publication in data['publications']:
    # Check if 'author' exists
    if 'author' not in publication:
        continue  # Skip this publication if it doesn't have 'author'
    
    for author in publication['author']:
        if author not in author_counts:
            author_counts[author] = 0
        author_counts[author] += 1

# Sort authors by the number of publications
sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)

# Extract the top 10 and bottom 10 authors
top_authors = {author for author, _ in sorted_authors[:15]}  # Top 15 most frequent authors
bottom_authors = {author for author, _ in sorted_authors[-15:]}  # Bottom 15 least frequent authors

# Extract the top 10 most central papers
sorted_papers = sorted(eigenvector_centrality.items(), key=lambda x: x[1], reverse=True)[:15]
top_papers = {paper[0] for paper in sorted_papers}  # Top 15 most central papers

# Visualization of the network with Eigenvector Centrality
# Only the top 10 most central papers
titles = [paper[0] for paper in sorted_papers]  # Top 10 titles

# Create a subgraph
G_subgraph = G.subgraph(titles)

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
    elif any(author in top_authors for author in authors):
        node_colors.append('blue')  # Blue for the most frequent authors
    elif any(author in bottom_authors for author in authors):
        node_colors.append('coral')  # Coral for the least frequent authors
    else:
        node_colors.append('gray')  # Neutral color for others

# Draw nodes
node_size = [5000 * eigenvector_centrality[node] for node in G_subgraph.nodes()]
nx.draw_networkx_nodes(G_subgraph, pos, node_size=node_size, node_color=node_colors, alpha=0.7)

# Draw edges without labels
nx.draw_networkx_edges(G_subgraph, pos, width=2, alpha=0.5, edge_color='gray')

# Draw node labels (the titles of the papers)
nx.draw_networkx_labels(G_subgraph, pos, font_size=7, font_weight='bold', font_color='black')  # Increased font_size

# Add title to the graph
plt.title("Citation Network - Eigenvector Centrality (Top 15)", size=20)  # Increased title size

plt.axis('off')  # Removes axes
plt.show()
