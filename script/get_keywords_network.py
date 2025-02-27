import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
import community as community_louvain
from collections import defaultdict

base_path = os.path.abspath("data")
file_path = os.path.join(base_path, "publications.json")
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def load_publications(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Access the list of publications
    if "publications" in data:
        data = data["publications"]
    else:
        raise ValueError("The JSON file does not contain the 'publications' key.")

    # Check that it is a list
    if not isinstance(data, list):
        raise ValueError("The 'publications' key must contain a list of articles.")
    
    return data

# Creating the graph
def create_cooccurrence_network(data):
    # Create the graph
    graph = nx.Graph()
    excluded_keywords = {"digital humanities", "computer science", "computer science (all)", 
                         "theoretical computer science", "software"}

    for index, entry in enumerate(data):
        # Extract the available identifier: DOI, URL, or ISBN
        article_id = entry.get("id") or entry.get("doi") or entry.get("url") or entry.get("isbn") or entry.get("title")
       
        if isinstance(article_id, list):
            article_id = str(article_id[0]) 
        
        # If no identifier is available, skip this article
        if not article_id:
            #print(f"Article without identifier (DOI, URL, ISBN, ID, or title): {entry.get('title', 'Title not available')}")
            continue

        # Retrieve the keywords
        keywords = entry.get("keywords", [])

        # If keywords are a string, split by commas or semicolons and clean the values
        if isinstance(keywords, str):
            # Replace semicolons with commas and then split by commas
            keywords = [kw.strip().replace('}', '').title() for kw in keywords.replace(';', ',').split(',') if kw.strip()]
        
        # If keywords are already a list, handle both commas and semicolons in each string
        elif isinstance(keywords, list):
            # Flatten the list by splitting each string by both commas and semicolons
            keywords = [kw.strip().replace('}', '').title() 
                        for keyword in keywords 
                        for kw in keyword.replace(';', ',').split(',') if kw.strip()]
       
       

        keywords = ['Italian Literature' if kw.lower() == 'letteratura italiana' else kw for kw in keywords]
        keywords = ['Ontologies' if kw.lower() == 'ontology' else kw for kw in keywords]

        # Exclude unwanted keywords
        keywords = [kw for kw in keywords if kw.lower() not in excluded_keywords]

        # Output the cleaned list of keywords
        #print(f"Cleaned keywords for article {article_id}: {keywords}")

        # Add nodes for each keyword (nodes are unique keywords)
        for keyword in keywords:
            if keyword not in graph:
                graph.add_node(keyword, type="keyword")  # Adding 'type' as "keyword"
        
        # Add the article as a node with 'type' as "article"
        if article_id not in graph:
            graph.add_node(article_id, type="article")  # Adding 'type' as "article"
        
        # Add edges between keywords based on the article they appear in
        for keyword1 in keywords:
            for keyword2 in keywords:
                if keyword1 != keyword2:  # Avoid self-loops
                    # If an edge exists between the two keywords, increment the weight
                    if graph.has_edge(keyword1, keyword2):
                        graph[keyword1][keyword2]["weight"] += 1
                        #print(f"Updated edge between {keyword1} and {keyword2} with new weight: {graph[keyword1][keyword2]['weight']}")
                    else:
                        # Otherwise, add a new edge with weight 1
                        graph.add_edge(keyword1, keyword2, weight=1)
                        #print(f"Added edge between {keyword1} and {keyword2} with weight 1")

            # Add the article as an edge connecting each keyword to the article
            graph.add_edge(article_id, keyword, weight=1)  # Articles are connected to keywords
            #print(f"Added edge between article {article_id} and keyword {keyword} with weight 1")

    # After all processing, print some nodes and edges for debugging
    print("\n--- Graph Summary ---")
    print(f"Number of nodes: {len(graph.nodes)}")
    print(f"Number of edges: {len(graph.edges)}")
    
    # Print a few nodes and edges to inspect the structure
    #print("\nSome nodes in the graph:")
    #print(list(graph.nodes)[:10])  # Print the first 10 nodes
    
    #print("\nSome edges in the graph:")
    #print(list(graph.edges)[:10])  # Print the first 10 edges

    return graph

# Function to create and export the adjacency matrix
def export_adjacency_matrix(G, output_path):
    # Generate the adjacency matrix as a DataFrame
    adjacency_matrix = nx.to_pandas_adjacency(G, dtype=int)
    
    # Export the adjacency matrix to a CSV file
    adjacency_matrix.to_csv(output_path, index=True)
    print(f"Adjacency matrix exported to: {output_path}")

# Network analysis metrics calculation
def analyze_network(G):
    print("\n--- Network Analysis ---")
    print("\nAverage degree:", sum(dict(G.degree()).values()) / G.number_of_nodes())

    # Calculate advanced metrics
    print("\n--- Centrality ---")
    # Degree centrality
    degree_centrality = nx.degree_centrality(G)
    print("Top 10 nodes by degree centrality:")
    for node, centrality_score in sorted(degree_centrality.items(), key=lambda x: -x[1])[:10]:
        print(f"{node}: {centrality_score:.4f}")

    # Betweenness centrality
    betweenness_centrality = nx.betweenness_centrality(G)
    print("\nTop 10 nodes by betweenness centrality:")
    for node, centrality_score in sorted(betweenness_centrality.items(), key=lambda x: -x[1])[:10]:
        print(f"{node}: {centrality_score:.4f}")

    # Closeness centrality
    closeness_centrality = nx.closeness_centrality(G)
    print("\nTop 10 nodes by closeness centrality:")
    for node, centrality_score in sorted(closeness_centrality.items(), key=lambda x: -x[1])[:10]:
        print(f"{node}: {centrality_score:.4f}")

    # Modularity
    print("\n--- Community Detection ---")
    partition = community_louvain.best_partition(G)  # Community detection
    modularity = community_louvain.modularity(partition, G)  # Modularity score
    print(f"\nLouvain algorithm detected {len(set(partition.values()))} communities with modularity: {community_louvain.modularity(partition, G):.4f}")

    # Group nodes by community
    clusters = defaultdict(list)
    for node, cluster_id in partition.items():
        clusters[cluster_id].append(node)

    # Print the total number of communities
    num_communities = len(clusters)
    print(f"Total number of communities (clusters): {num_communities}")

    # Other metrics
    print("\n--- Cohesion and Structure ---")
    # Diameter of the network (if the network is connected)
    if nx.is_connected(G):
        diameter = nx.diameter(G)
        print(f"Network diameter: {diameter}")
    else:
        print("The network is not connected, cannot calculate the diameter.") 

    # Network density
    density = nx.density(G)
    print(f"Network density: {density:.4f}")

    # Connected components
    connected_components = list(nx.connected_components(G))
    print(f"Number of connected components: {len(connected_components)}")

    # Clustering (average clustering coefficient)
    clustering_coefficient = nx.average_clustering(G)
    print(f"Average clustering coefficient: {clustering_coefficient:.4f}")

# Function to create a DataFrame with network metrics
def export_analysis_to_pandas(G):
    # Check if the graph is connected
    is_connected = nx.is_connected(G)
    
    # Basic metrics
    nodes = list(G.nodes)
    degrees = dict(G.degree())
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    clustering_coefficients = nx.clustering(G)

    # Community detection and modularity
    partition = community_louvain.best_partition(G)  # Community detection
    modularity = community_louvain.modularity(partition, G)  # Modularity score
    
    # Group nodes by community
    clusters = defaultdict(list)
    for node, cluster_id in partition.items():
        clusters[cluster_id].append(node)

    # Number of communities
    num_communities = len(clusters)

    # Prepare data for the DataFrame (Node-level metrics)
    data = {
        "Node": nodes,
        "Degree": [degrees[node] for node in nodes],
        "Degree Centrality": [degree_centrality[node] for node in nodes],
        "Betweenness Centrality": [betweenness_centrality[node] for node in nodes],
        "Closeness Centrality": [closeness_centrality[node] for node in nodes],
        "Clustering Coefficient": [clustering_coefficients[node] for node in nodes],
    }

    # Create the DataFrame for node-level data
    node_df = pd.DataFrame(data)

    # Prepare global metrics (Network-level metrics)
    global_metrics = {
        "Network Density": nx.density(G),
        "Number of Nodes": len(G.nodes),
        "Number of Edges": len(G.edges),
        "Average Clustering Coefficient": nx.average_clustering(G),
        "Number of Connected Components": len(list(nx.connected_components(G))),
        "Is Connected": is_connected,
        "Modularity": modularity,
        "Total Number of clusters": num_communities,
    }

    # Create a DataFrame for global metrics and append it
    global_metrics_df = pd.DataFrame(global_metrics, index=[0])

    # Print node-level and global metrics DataFrames
    # print("\nNode-level Analysis:")
    # print(node_df.head())

    # print("\nGlobal Metrics:")
    # print(global_metrics_df)

    return node_df, global_metrics_df

# Export the graph to GML format
def export_to_gml(G, output_path):
    nx.write_gml(G, output_path)
    print(f"Graph exported to: {output_path}")

# Main script
if __name__ == "__main__":
    # Load the data
    data = load_publications(file_path)

    # Create the graph
    graph = create_cooccurrence_network(data)
    partition = community_louvain.best_partition(graph)

    # Analyze the graph
    analyze_network(graph)

    # Export network analysis results as DataFrames
    node_df, global_metrics_df = export_analysis_to_pandas(graph)

    # Ensure the 'report' directory exists
    output_path = os.path.join(output_dir, 'report', 'keyword')
    os.makedirs(output_path, exist_ok=True)

    # Save node-level analysis and global metrics to CSV files
    node_df.to_csv(os.path.join(output_path, "kw_node_level_analysis_general.csv"), index=False)
    global_metrics_df.to_csv(os.path.join(output_path, "kw_global_metrics_general.csv"), index=False)

    # Convert the graph to an adjacency matrix
    #adjacency_matrix = nx.to_pandas_adjacency(graph)

    # Export the adjacency matrix
    #adjacency_matrix_output_path = os.path.join(output_path, "kw_adjacency_matrix_general.csv")
    #adjacency_matrix.to_csv(adjacency_matrix_output_path, index=True)
    # save the adjacency matrix to a CSV file
    #adjacency_matrix_output_path = os.path.join(output_path, "kw_adjacency_matrix_general.csv")
    #export_adjacency_matrix(graph, adjacency_matrix_output_path)

    # Export for GML format
    output_file_gml = os.path.abspath(os.path.join(output_dir, "network", "keyword", "keyword_cooccurrence_general.gml"))
    export_to_gml(graph, output_file_gml)
