import json
import networkx as nx
import matplotlib.pyplot as plt
import os

base_path = os.path.dirname(os.path.abspath(__file__))

# Define the file paths for the JSON files
authors_file_path = os.path.join(base_path, 'data', 'authors.json')
projects_file_path = os.path.join(base_path, 'data', 'projects.json')

# Open and load the authors.json file
with open(authors_file_path, 'r') as f:
    authors_data = json.load(f)

# Open and load the projects.json file
with open(projects_file_path, 'r') as f:
    projects_data = json.load(f)

G = nx.Graph()

# Add nodes for each member in the graph
for member in authors_data["members"]:
    orcid_id = member.get("ORCID_ID", None)  # Use None if 'ORCID_ID' is missing
    if orcid_id:
        G.add_node(orcid_id, label=member["name"], type='member')

# Add edges based on projects
for project in projects_data["projects"]:
    project_id = project["project_id"]
    G.add_node(project_id, label=project["name"], type='project')  
    
    for participant in project["participants"]:
        G.add_edge(participant, project_id)  

# Counting the pairs of authors that are in the same project
member_pairs = {}
for project in projects_data["projects"]:
    participants = project["participants"]
    for i in range(len(participants)):
        for j in range(i + 1, len(participants)):
            pair = tuple(sorted((participants[i], participants[j])))
            if pair not in member_pairs:
                member_pairs[pair] = 0
            member_pairs[pair] += 1
            
# showing results
for pair, count in member_pairs.items():
    print(f'Membros {pair} têm {count} projeto(s) em comum.')
    
# visualization of the graph
pos = nx.spring_layout(G)  
nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=10)
plt.show()

#some metrics
# Calculate various centrality metrics
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
closeness_centrality = nx.closeness_centrality(G)
eigenvector_centrality = nx.eigenvector_centrality(G)
pagerank_centrality = nx.pagerank(G)

# Function to draw the graph based on a centrality metric
def draw_graph(centrality, title):
    pos = nx.spring_layout(G)  # Positioning the nodes using spring layout
    node_sizes = [v * 1000 for v in centrality.values()]  # Scale node sizes based on centrality values
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color='lightblue', font_size=10)
    plt.title(title)
    plt.show()

# Visualize each centrality metric
draw_graph(degree_centrality, "Degree Centrality")
draw_graph(betweenness_centrality, "Betweenness Centrality")
draw_graph(closeness_centrality, "Closeness Centrality")
draw_graph(eigenvector_centrality, "Eigenvector Centrality")
draw_graph(pagerank_centrality, "PageRank Centrality")
