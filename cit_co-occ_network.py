import json
import networkx as nx
from pyvis.network import Network
from collections import Counter, defaultdict

# Load data from the JSON file
with open("data/publications.json", "r") as file:
    data = json.load(file)

# Normalize and unify keywords
def normalize_keyword(keyword):
    return keyword.lower().strip()

# Extract all keywords and count occurrences
all_keywords = []
for publication in data['publications']:
    all_keywords.extend(normalize_keyword(k) for k in publication.get('keywords', []))

# Get the 20 most frequent keywords
keyword_counts = Counter(all_keywords)
top_keywords = {kw for kw, _ in keyword_counts.most_common(20)}

# Create the graph (keyword co-occurrence network)
G = nx.Graph()

# Dictionary to store keyword co-occurrence counts
keyword_cooccurrence = defaultdict(int)

# Process publications to extract relationships among top keywords
for publication in data['publications']:
    keywords = {normalize_keyword(k) for k in publication.get('keywords', [])} & top_keywords
    
    # Create edges only between top keywords appearing together
    for keyword1 in keywords:
        for keyword2 in keywords:
            if keyword1 != keyword2:
                keyword_cooccurrence[(keyword1, keyword2)] += 1

# Add nodes and edges to the graph
for (keyword1, keyword2), weight in keyword_cooccurrence.items():
    G.add_edge(keyword1, keyword2, weight=weight)

# Calculate eigenvector centrality
eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000, tol=1e-6)

# Create subgraph with only the top 20 keywords
G_subgraph = G.subgraph(top_keywords)

# Initialize Pyvis network
net = Network(height="800px", width="100%", notebook=True)

# Add nodes and edges with size and color based on centrality and weight
for node in G_subgraph.nodes():
    centrality = eigenvector_centrality[node]
    # Set node color to green instead of gray
    net.add_node(node, size=100 * centrality, color='green' if node != max(eigenvector_centrality, key=eigenvector_centrality.get) else 'pink')

# Add edges with weight as a threshold for visual clarity
for u, v, data in G_subgraph.edges(data=True):
    weight = data['weight']
    net.add_edge(u, v, value=weight)

# Disable the physics completely (no movement at all)
net.physics = False

# Manually set the node positions to be spread out
net.show_buttons(filter_=['physics'])  # This allows you to turn physics on/off if needed in the interface

# Show the interactive network (this saves the visualization as an HTML file)
net.show("keyword_network_nodes.html")
