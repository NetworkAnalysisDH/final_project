import os
import json
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
from community import community_louvain

# Relative path to the JSON file
base_path = os.path.dirname(os.path.abspath(__file__)) 
print(f"Output folder: {base_path}")
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
    print("\n--- Community Detection ---")
    partition = community_louvain.best_partition(G)
    modularity = community_louvain.modularity(partition, G)
    print(f"Modularity: {modularity:.4f}")
    clusters = defaultdict(list)

    for node, cluster_id in partition.items():
        clusters[cluster_id].append(node)
        print("Partition:", partition)
        print("Clusters:", clusters)
    num_communities = len(clusters)
    print(f"Total number of communities: {num_communities}")

    # Create subgraphs for each community
    output_folder = os.path.abspath(os.path.join(base_path, 'network', 'keyword', 'community_graphs'))
    print(f"Output folder: {output_folder}")
    os.makedirs(output_folder, exist_ok=True)

    for community_id, nodes in clusters.items():
        subgraph = G.subgraph(nodes).copy()  # Create a subgraph for each community
        print(f"\nSubgraph for Community {community_id} - Number of nodes: {len(subgraph.nodes)}")
        
        try:
            nx.write_gml(subgraph, os.path.join(output_folder, f"community_{community_id}.gml"))
            print(f"GML file saved for community {community_id}")
        except Exception as e:
            print(f"Error saving GML for community {community_id}: {e}")
        

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

def export_to_gephi(G, output_path):
    nx.write_gml(G, output_path)

def export_analysis_to_pandas(G):
    is_connected = nx.is_connected(G)
    nodes = list(G.nodes)
    degrees = dict(G.degree())
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
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
        "Modularity": modularity,
        "Total Number of Communities": num_communities,
    }
    global_metrics_df = pd.DataFrame(global_metrics, index=[0])
    return node_df, global_metrics_df

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
    
    # Creating separate graphs for each measure and exporting
    output_folder = os.path.join(base_path, "network", "keyword")
    os.makedirs(output_folder, exist_ok=True)
    
    # Degree Centrality Graph
    degree_centrality_graph = nx.Graph()
    degree_centrality = nx.degree_centrality(filtered_graph)
    for node, centrality in degree_centrality.items():
        degree_centrality_graph.add_node(node, centrality=centrality)
    nx.write_gml(degree_centrality_graph, os.path.join(output_folder, "kw_degree_centrality.gml"))
    
    # Betweenness Centrality Graph
    betweenness_centrality_graph = nx.Graph()
    betweenness_centrality = nx.betweenness_centrality(filtered_graph)
    for node, centrality in betweenness_centrality.items():
        betweenness_centrality_graph.add_node(node, centrality=centrality)
    nx.write_gml(betweenness_centrality_graph, os.path.join(output_folder, "kw_betweenness_centrality.gml"))
    
    # Closeness Centrality Graph
    closeness_centrality_graph = nx.Graph()
    closeness_centrality = nx.closeness_centrality(filtered_graph)
    for node, centrality in closeness_centrality.items():
        closeness_centrality_graph.add_node(node, centrality=centrality)
    nx.write_gml(closeness_centrality_graph, os.path.join(output_folder, "kw_closeness_centrality.gml"))
    
    # Exporting CSV reports to the 'report/keyword' folder
    report_folder = os.path.join(base_path, "report", "keyword")
    os.makedirs(report_folder, exist_ok=True)
    
    # Node-level CSV export
    node_df, global_metrics_df = export_analysis_to_pandas(filtered_graph)
    node_df.to_csv(os.path.join(report_folder, "kw_node_analysis_statiscal_relevance.csv"), index=False)
    global_metrics_df.to_csv(os.path.join(report_folder, "kw_global_metrics_statistical_relevance.csv"), index=False)
    
    # Adjacency matrix export
    export_adjacency_matrix(filtered_graph, os.path.join(report_folder, "kw_adjacency_matrix_statistical_relevance.csv"))
