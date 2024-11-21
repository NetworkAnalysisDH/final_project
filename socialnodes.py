import json
import networkx as nx
import matplotlib.pyplot as plt

# Carregando dados de membros e projetos
with open('members.json') as f:
    members_data = json.load(f)
    
with open('projects.json') as f:
    projects_data = json.load(f)

G = nx.Graph()

# Adicionando nós para membros
for member in members_data["members"]:
    G.add_node(member["members_id"], label=member["name"], type='member')

# Adicionando nós para projetos e arestas
for project in projects_data["projects"]:
    project_id = project["project_id"]
    G.add_node(project_id, label=project["name"], type='project')  
    
    for participant in project["participants"]:
        G.add_edge(participant, project_id)  


member_pairs = {}
for project in projects_data["projects"]:
    participants = project["participants"]
    for i in range(len(participants)):
        for j in range(i + 1, len(participants)):
            pair = tuple(sorted((participants[i], participants[j])))
            if pair not in member_pairs:
                member_pairs[pair] = 0
            member_pairs[pair] += 1
            

for pair, count in member_pairs.items():
    print(f'Membros {pair} têm {count} projeto(s) em comum.')


pos = nx.spring_layout(G)  
nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=10)
plt.show()
