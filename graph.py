import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# Define the researchers and their relationships
researchers = [
    "Silvio Peroni",
    "Francesca Tomasi",
    "Fabio Vitali",
    "Aldo Gangemi",
    "Sofia Pescarin",
    "Giovanni Colavizza",
    "Marilena Daquino",
    "Paola Italia",
    "Monica Palmirani",
    "Ivan Heibi",
    "Arcangelo Massari",
    "Fabio Tamburini"
]

# Initialize adjacency matrix
adjacency_matrix = np.zeros((len(researchers), len(researchers)))

# Fill the adjacency matrix based on the collaborations
collaborations = [
    ("Silvio Peroni", "Francesca Tomasi"),
    ("Francesca Tomasi", "Silvio Peroni"),
    ("Silvio Peroni", "Arcangelo Massari"),
    ("Arcangelo Massari", "Silvio Peroni"),
    ("Fabio Vitali", "Aldo Gangemi"),
    ("Aldo Gangemi", "Fabio Vitali"),
    ("Silvio Peroni", "Giovanni Colavizza"),
    ("Giovanni Colavizza", "Silvio Peroni"),
    ("Marilena Daquino", "Silvio Peroni"),
    ("Silvio Peroni", "Marilena Daquino"),
    ("Ivan Heibi", "Silvio Peroni"),
    ("Silvio Peroni", "Ivan Heibi")
]

# Fill in the adjacency matrix based on collaborations
for colab in collaborations:
    i = researchers.index(colab[0])
    j = researchers.index(colab[1])
    adjacency_matrix[i][j] = 1  # Mark the presence of a collaboration

# Create a directed graph from the adjacency matrix
G = nx.from_numpy_array(adjacency_matrix, create_using=nx.DiGraph)

# Relabel the nodes to use researcher names
mapping = {i: researcher for i, researcher in enumerate(researchers)}
G = nx.relabel_nodes(G, mapping)

# Calculate and print Degree Centrality
degree_centrality = nx.degree_centrality(G)
print("Degree Centrality:")
for researcher, centrality in degree_centrality.items():
    print(f"{researcher}: {centrality:.4f}")

# Calculate and print Betweenness Centrality
betweenness_centrality = nx.betweenness_centrality(G)
print("\nBetweenness Centrality:")
for researcher, centrality in betweenness_centrality.items():
    print(f"{researcher}: {centrality:.4f}")

# Calculate and print Clustering Coefficient
clustering_coefficient = nx.clustering(G)
print("\nClustering Coefficient:")
for researcher, coefficient in clustering_coefficient.items():
    print(f"{researcher}: {coefficient:.4f}")

# Core-Periphery Analysis
degree_sorted = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
threshold = 0.3  # Adjust this value as necessary for your analysis
core_members = [node for node, centrality in degree_sorted if centrality > threshold]
peripheral_members = [node for node, centrality in degree_sorted if centrality <= threshold]

# Print Core-Periphery Analysis
print("\nCore Members:")
print(core_members)
print("\nPeripheral Members:")
print(peripheral_members)

# Draw the graph
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)  # positions for all nodes
nx.draw_networkx_nodes(G, pos, node_size=700)
nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20)
nx.draw_networkx_labels(G, pos, font_size=12)
plt.title("Research Collaborations in Digital Humanities at the University of Bologna")
plt.axis('off')  # Turn off the axis
plt.show()
