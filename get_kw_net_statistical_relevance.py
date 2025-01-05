import os
import json
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
from community import community_louvain

# Absolute path to the JSON file
base_path = "/Users/carlamenegat/Documents/GitHub/final_project/Information-Modeling-and-Web-Technologies/final_project"
file_path = os.path.join(base_path, "data", "publications.json")

def load_publications(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "publications" in data:
        data = data["publications"]
    else:
        raise ValueError("The JSON file does not contain the 'publications' key.")
    if not isinstance(data, list):
        raise ValueError("The 'publications' key must contain a list of articles.")
    return data

def get_article_id(entry):
    return entry.get("id") or entry.get("doi") or entry.get("url") or entry.get("isbn") or entry.get("title")

def find_duplicates(publications):
    seen = defaultdict(list)
    duplicates = []
    for index, entry in enumerate(publications):
        article_id = get_article_id(entry)
        if article_id:
            if article_id in seen:
                duplicates.append((seen[article_id], index))
            seen[article_id].append(index)
    return duplicates

def create_cooccurrence_network(data):
    graph = nx.Graph()
    excluded_keywords = {"digital humanities", "computer science", "computer science (all)", 
                         "theoretical computer science", "italian literature", "software"}
    for index, entry in enumerate(data):
        article_id = get_article_id(entry)
        if isinstance(article_id, list):
            article_id = str(article_id[0]) 
        if not article_id:
            continue
        keywords = entry.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [kw.strip().replace('}', '').title() for kw in keywords.replace(';', ',').split(',') if kw.strip()]
        elif isinstance(keywords, list):
            keywords = [kw.strip().replace('}', '').title() 
                        for keyword in keywords 
                        for kw in keyword.replace(';', ',').split(',') if kw.strip()]
        keywords = ['Italian Literature' if kw.lower() == 'letteratura italiana' else kw for kw in keywords]
        keywords = ['Ontologies' if kw.lower() == 'ontology' else kw for kw in keywords]
        keywords = [kw for kw in keywords if kw.lower() not in excluded_keywords]
        for keyword in keywords:
            if keyword not in graph:
                graph.add_node(keyword)
        for keyword1 in keywords:
            for keyword2 in keywords:
                if keyword1 != keyword2:
                    if graph.has_edge(keyword1, keyword2):
                        graph[keyword1][keyword2]["weight"] += 1
                    else:
                        graph.add_edge(keyword1, keyword2, weight=1)
            graph.add_edge(article_id, keyword, weight=1)
    print("\n--- Graph Summary ---")
    print(f"Number of nodes: {len(graph.nodes)}")
    print(f"Number of edges: {len(graph.edges)}")
    return graph

def filter_graph_by_degree_centrality(G, threshold=0.01):
    degree_centrality = nx.degree_centrality(G)
    filtered_nodes = {node for node, centrality in degree_centrality.items() if centrality > threshold}
    return G.subgraph(filtered_nodes)

def export_adjacency_matrix(G, output_path):
    adjacency_matrix = nx.to_pandas_adjacency(G, dtype=int)
    adjacency_matrix.to_csv(output_path, index=True)
    print(f"Adjacency matrix exported to: {output_path}")

def visualize_network(G):
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='skyblue')
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black')
    plt.title("Keyword Co-occurrence Network Visualization")
    plt.axis('off')
    plt.show()

def analyze_network(G):
    print("Average degree:", sum(dict(G.degree()).values()) / G.number_of_nodes())
    print("\n--- Centrality ---")
    degree_centrality = nx.degree_centrality(G)
    print("Top 10 nodes by degree centrality:")
    for node, centrality_score in sorted(degree_centrality.items(), key=lambda x: -x[1])[:10]:
        print(f"{node}: {centrality_score:.4f}")
    betweenness_centrality = nx.betweenness_centrality(G)
    print("\nTop 10 nodes by betweenness centrality:")
    for node, centrality_score in sorted(betweenness_centrality.items(), key=lambda x: -x[1])[:10]:
        print(f"{node}: {centrality_score:.4f}")
    closeness_centrality = nx.closeness_centrality(G)
    print("\nTop 10 nodes by closeness centrality:")
    for node, centrality_score in sorted(closeness_centrality.items(), key=lambda x: -x[1])[:10]:
        print(f"{node}: {centrality_score:.4f}")
    eigenvector_centrality = nx.eigenvector_centrality(G)
    print("\nTop 10 nodes by eigenvector centrality:")
    for node, centrality_score in sorted(eigenvector_centrality.items(), key=lambda x: -x[1])[:10]:
        print(f"{node}: {centrality_score:.4f}")
    print("\n--- Community Detection ---")
    partition = community_louvain.best_partition(G)
    modularity = community_louvain.modularity(partition, G)
    print(f"Modularity: {modularity:.4f}")
    clusters = defaultdict(list)
    for node, cluster_id in partition.items():
        clusters[cluster_id].append(node)
    num_communities = len(clusters)
    print(f"Total number of communities: {num_communities}")
    print("\n--- Cohesion and Structure ---")
    if nx.is_connected(G):
        diameter = nx.diameter(G)
        print(f"Network diameter: {diameter}")
    else:
        print("The network is not connected, cannot calculate the diameter.") 
    density = nx.density(G)
    print(f"Network density: {density:.4f}")
    connected_components = list(nx.connected_components(G))
    print(f"Number of connected components: {len(connected_components)}")
    clustering_coefficient = nx.average_clustering(G)
    print(f"Average clustering coefficient: {clustering_coefficient:.4f}")
    assortativity = nx.degree_assortativity_coefficient(G)
    print(f"Assortativity: {assortativity:.4f}")

def export_to_gephi(G, output_path):
    nx.write_graphml(G, output_path)

def export_analysis_to_pandas(G):
    is_connected = nx.is_connected(G)
    nodes = list(G.nodes)
    degrees = dict(G.degree())
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    eigenvector_centrality = nx.eigenvector_centrality(G)
    clustering_coefficients = nx.clustering(G)
    partition = community_louvain.best_partition(G)
    modularity = community_louvain.modularity(partition, G)
    clusters = defaultdict(list)
    for node, cluster_id in partition.items():
        clusters[cluster_id].append(node)
    num_communities = len(clusters)
    data = {
        "Node": nodes,
        "Degree": [degrees[node] for node in nodes],
        "Degree Centrality": [degree_centrality[node] for node in nodes],
        "Betweenness Centrality": [betweenness_centrality[node] for node in nodes],
        "Closeness Centrality": [closeness_centrality[node] for node in nodes],
        "Eigenvector Centrality": [eigenvector_centrality[node] for node in nodes],
        "Clustering Coefficient": [clustering_coefficients[node] for node in nodes],
    }
    node_df = pd.DataFrame(data)
    global_metrics = {
        "Network Density": nx.density(G),
        "Number of Nodes": len(G.nodes),
        "Number of Edges": len(G.edges),
        "Average Clustering Coefficient": nx.average_clustering(G),
        "Number of Connected Components": len(list(nx.connected_components(G))),
        "Is Connected": is_connected,
        "Assortativity": nx.degree_assortativity_coefficient(G),
        "Modularity": modularity,
        "Total Number of Communities": num_communities,
    }
    global_metrics_df = pd.DataFrame(global_metrics, index=[0])
    return node_df, global_metrics_df

def export_to_gml(G, output_path):
    nx.write_gml(G, output_path)
    print(f"Graph exported to: {output_path}")

if __name__ == "__main__":
    publications = load_publications(file_path)
    duplicates = find_duplicates(publications)
    if duplicates:
        print("Found duplicates:")
        for dup in duplicates:
            print(f"Duplicate entries found at indices: {dup[0]} and {dup[1]}")
            for idx in dup[0]:
                print(f"Entry {idx}: {publications[idx]}")
            print(f"Entry {dup[1]}: {publications[dup[1]]}")
            print("-" * 80)
    else:
        print("No duplicates found.")
    graph = create_cooccurrence_network(publications)
    filtered_graph = filter_graph_by_degree_centrality(graph)
    analyze_network(filtered_graph)
    output_file = os.path.join(base_path, "network", "stats_relevance_keyword_cooccurrence.graphml")
    export_to_gephi(filtered_graph, output_file)
    node_df, global_metrics_df = export_analysis_to_pandas(filtered_graph)
    output_dir = os.path.join(base_path, "Report")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    node_df.to_csv(os.path.join(output_dir, "stats_relevance_node_level_analysis.csv"), index=False)
    global_metrics_df.to_csv(os.path.join(output_dir, "stats_relevance_global_metrics.csv"), index=False)
    adjacency_matrix_output_path = os.path.join(output_dir, "stats_relevance_adjacency_matrix.csv")
    export_adjacency_matrix(filtered_graph, adjacency_matrix_output_path)
    output_file_gml = os.path.join(base_path, "network", "stats_relevance_keyword_cooccurrence.gml")
    export_to_gml(filtered_graph, output_file_gml)

print(f"Loading file from: {file_path}")