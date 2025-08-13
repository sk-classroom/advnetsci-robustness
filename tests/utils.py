"""
Utilities for network construction and testing.

This module provides functions to construct networks from various data sources
for testing purposes in the network robustness assignment.
"""

import igraph as ig
import requests
import zipfile
import io
import csv
import os
from typing import Tuple, List, Optional


def construct_london_transport_network() -> ig.Graph:
    """
    Construct the London Transportation Network from the Network Repository data.
    
    Downloads and parses the London Transport network dataset from:
    https://networks.skewed.de/net/london_transport/files/london_transport.csv.zip
    
    The dataset contains edges in the format: source, target, weight, layer
    This function creates an igraph Graph object with the network structure.
    
    Returns:
        ig.Graph: London Transportation Network as an igraph Graph object
        
    Raises:
        requests.RequestException: If download fails
        zipfile.BadZipFile: If the downloaded file is not a valid zip
        FileNotFoundError: If the expected CSV file is not found in the archive
        ValueError: If the CSV data cannot be parsed properly
    """
    
    # URL for the London Transport network data
    data_url = "https://networks.skewed.de/net/london_transport/files/london_transport.csv.zip"
    
    try:
        # Download the zip file
        print("Downloading London Transport network data...")
        response = requests.get(data_url, timeout=30)
        response.raise_for_status()
        
        # Open the zip file
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            # Look for the edges CSV file
            csv_filename = "Network Catalogue/edges.csv"
            
            if csv_filename not in zip_file.namelist():
                # Try alternative naming patterns
                possible_names = [
                    "edges.csv",
                    "london_transport_edges.csv", 
                    "Network Catalogue/london_transport_edges.csv"
                ]
                
                found_file = None
                for name in possible_names:
                    if name in zip_file.namelist():
                        found_file = name
                        break
                
                if not found_file:
                    available_files = zip_file.namelist()
                    raise FileNotFoundError(
                        f"Could not find edges CSV file. Available files: {available_files}"
                    )
                csv_filename = found_file
            
            # Read the CSV data
            with zip_file.open(csv_filename) as csv_file:
                # Decode bytes to string and create CSV reader
                csv_content = csv_file.read().decode('utf-8')
                csv_reader = csv.reader(io.StringIO(csv_content))
                
                # Skip header if present (check if first row contains non-numeric data)
                edges_data = []
                first_row = True
                
                for row in csv_reader:
                    if not row or len(row) < 2:  # Skip empty rows
                        continue
                        
                    # Check if first row is header
                    if first_row:
                        try:
                            int(row[0])  # Try to convert first element to int
                            first_row = False
                        except ValueError:
                            # First row is header, skip it
                            first_row = False
                            continue
                    
                    # Parse edge data: source, target, weight, layer
                    try:
                        source = int(row[0])
                        target = int(row[1])
                        # weight and layer are available but not needed for basic graph construction
                        edges_data.append((source, target))
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Skipping invalid row {row}: {e}")
                        continue
        
        if not edges_data:
            raise ValueError("No valid edges found in the dataset")
        
        # Remove duplicate edges - normalize edge direction and use set for deduplication
        unique_edges = set()
        for source, target in edges_data:
            # Normalize edge direction (smaller node first) for undirected graph
            edge = (min(source, target), max(source, target))
            unique_edges.add(edge)
        
        # Convert back to list
        original_count = len(edges_data)
        edges_data = list(unique_edges)
        print(f"Removed {original_count - len(edges_data)} duplicate edges")
        
        # Get all unique nodes
        all_nodes = set()
        for source, target in edges_data:
            all_nodes.add(source)
            all_nodes.add(target)
        
        # Create igraph Graph
        print(f"Creating network with {len(all_nodes)} nodes and {len(edges_data)} edges...")
        
        # Create graph with specified number of vertices
        max_node = max(all_nodes)
        graph = ig.Graph(n=max_node + 1, directed=False)
        
        # Add edges (igraph handles duplicate edges automatically)
        graph.add_edges(edges_data)
        
        # Remove isolated vertices to match typical network analysis conventions
        to_remove = []
        for i in range(graph.vcount()):
            if graph.degree(i) == 0:
                to_remove.append(i)
        
        if to_remove:
            graph.delete_vertices(to_remove)
            print(f"Removed {len(to_remove)} isolated vertices")
        
        print(f"Final network: {graph.vcount()} nodes, {graph.ecount()} edges")
        
        # Add basic vertex attributes
        graph.vs["id"] = list(range(graph.vcount()))
        
        return graph
        
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to download data: {e}")
    except zipfile.BadZipFile as e:
        raise zipfile.BadZipFile(f"Invalid zip file: {e}")
    except Exception as e:
        raise ValueError(f"Error processing network data: {e}")


def get_network_info(graph: ig.Graph) -> dict:
    """
    Get basic information about a network.
    
    Args:
        graph: igraph Graph object
        
    Returns:
        dict: Dictionary containing network statistics
    """
    return {
        "nodes": graph.vcount(),
        "edges": graph.ecount(),
        "density": graph.density(),
        "is_connected": graph.is_connected(),
        "components": len(graph.connected_components()),
        "diameter": graph.diameter() if graph.is_connected() else None,
        "average_degree": sum(graph.degree()) / graph.vcount()
    }


def compare_networks(graph1: ig.Graph, graph2: ig.Graph) -> dict:
    """
    Compare basic statistics between two networks.
    
    Args:
        graph1: First network
        graph2: Second network
        
    Returns:
        dict: Comparison statistics
    """
    info1 = get_network_info(graph1)
    info2 = get_network_info(graph2)
    
    comparison = {}
    for key in info1:
        comparison[key] = {
            "network1": info1[key],
            "network2": info2[key],
            "difference": info2[key] - info1[key] if isinstance(info1[key], (int, float)) and info1[key] is not None and info2[key] is not None else None
        }
    
    return comparison


if __name__ == "__main__":
    # Test the function
    try:
        network = construct_london_transport_network()
        info = get_network_info(network)
        
        print("\nLondon Transport Network Statistics:")
        print("=" * 40)
        for key, value in info.items():
            print(f"{key.capitalize().replace('_', ' ')}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")