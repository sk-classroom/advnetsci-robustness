# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy>=1.20.0",
#     "python-igraph>=0.11.0",
#     "pandas==2.3.1",
#     "scipy",
#     "requests>=2.31.0",
#     "marimo",
# ]
# ///

# %% Import
import sys
import os
import igraph
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from assignment.assignment import custom_edge_attack_sequence, degree_edge_attack_sequence
from utils import construct_london_transport_network

# %% Setup
graph = construct_london_transport_network()

# %% Helper Functions
def simulate_attack_effectiveness(graph, edge_sequence):
    """Simulate attack sequence and return connectivity profile"""
    connectivity_profile = []
    g_copy = graph.copy()
    total_nodes = g_copy.vcount()

    # Initial connectivity
    components = g_copy.connected_components()
    largest_component_size = max(len(comp) for comp in components) if components else 0
    connectivity = largest_component_size / total_nodes
    connectivity_profile.append(connectivity)

    # Remove edges one by one
    for edge in edge_sequence:
        try:
            # Find edge ID and remove
            edge_id = g_copy.get_eid(edge[0], edge[1], error=False)
            if edge_id != -1:
                g_copy.delete_edges([edge_id])

                # Calculate new connectivity
                components = g_copy.connected_components()
                largest_component_size = max(len(comp) for comp in components) if components else 0
                connectivity = largest_component_size / total_nodes
                connectivity_profile.append(connectivity)
        except:
            # Edge might not exist or already removed
            connectivity_profile.append(connectivity_profile[-1])

    return connectivity_profile


# %% Test Custom Edge Attack Sequence
print("=" * 60)
print("TEST 02: Custom Edge Attack Sequence")
print("=" * 60)

# ------------------------------------------------------------
# Test Setup
# ------------------------------------------------------------
if graph is None:
    print("❌ FAILED: Could not load test network")
    exit(1)

print(f"📊 Test network: {graph.vcount()} nodes, {graph.ecount()} edges")

try:
    custom_sequence = custom_edge_attack_sequence(graph)

    # ------------------------------------------------------------
    # Test 1: Function returns a list
    # ------------------------------------------------------------
    print(f"[Test 1] Function returns list: {isinstance(custom_sequence, list)}")
    assert isinstance(custom_sequence, list), "Function must return a list"

    # ------------------------------------------------------------
    # Test 2: Correct number of edges
    # ------------------------------------------------------------
    expected_edges = graph.ecount()
    print(f"[Test 2] Correct edge count: expected {expected_edges}, got {len(custom_sequence)}")
    assert len(custom_sequence) == expected_edges, f"Expected {expected_edges} edges, got {len(custom_sequence)}"

    # ------------------------------------------------------------
    # Test 3: All elements are tuples with 2 elements
    # ------------------------------------------------------------
    all_tuples = all(isinstance(edge, tuple) and len(edge) == 2 for edge in custom_sequence)
    print(f"[Test 3] All edges are (source, target) tuples: {all_tuples}")
    assert all_tuples, "All edges must be (source, target) tuples"

    # ------------------------------------------------------------
    # Test 4: All edges exist in the original graph
    # ------------------------------------------------------------
    original_edges = set((e.source, e.target) for e in graph.es)
    original_edges.update((e.target, e.source) for e in graph.es)  # Add reverse edges

    all_exist = all((source, target) in original_edges for source, target in custom_sequence)
    print(f"[Test 4] All edges exist in original graph: {all_exist}")
    assert all_exist, "All edges must exist in the original graph"

    # ------------------------------------------------------------
    # Test 5: No duplicate edges
    # ------------------------------------------------------------
    edge_set = set(custom_sequence)
    no_duplicates = len(edge_set) == len(custom_sequence)
    print(f"[Test 5] No duplicate edges: {no_duplicates} (unique: {len(edge_set)}, total: {len(custom_sequence)})")
    assert no_duplicates, f"Duplicate edges found. Unique: {len(edge_set)}, Total: {len(custom_sequence)}"

    # ------------------------------------------------------------
    # Test 6: Compare effectiveness with degree-based attack
    # ------------------------------------------------------------
    print("[Test 6] Comparing custom vs degree-based attack effectiveness...")

    try:
        degree_sequence = degree_edge_attack_sequence(graph)

        # Simulate both attack strategies
        custom_profile = simulate_attack_effectiveness(graph, custom_sequence)
        degree_profile = simulate_attack_effectiveness(graph, degree_sequence)

        # Find where connectivity drops below 50%
        def find_50_percent_threshold(profile):
            for i, conn in enumerate(profile):
                if conn < 0.5:
                    return i
            return len(profile)

        custom_threshold = find_50_percent_threshold(custom_profile)
        degree_threshold = find_50_percent_threshold(degree_profile)

        print(f"   Custom attack reaches 50% connectivity at: {custom_threshold} edge removals")
        print(f"   Degree attack reaches 50% connectivity at: {degree_threshold} edge removals")

        # Custom should be equal or better (reach 50% with same or fewer removals)
        if custom_threshold <= degree_threshold:
            improvement = degree_threshold - custom_threshold
            print(f"   Custom attack is {improvement} steps better or equal")
        else:
            deficit = custom_threshold - degree_threshold
            print(f"   WARNING: Custom attack is {deficit} steps worse than degree-based")

        # Check if custom attack uses a different strategy than degree-based
        strategy_difference = sum(1 for i in range(min(10, len(custom_sequence)))
                               if custom_sequence[i] != degree_sequence[i])

        different_strategy = strategy_difference > 5
        print(f"[Test 6] Custom strategy differs from degree-based: {different_strategy} ({strategy_difference}/10 different)")

    except Exception as e:
        print(f"   WARNING: Could not compare with degree-based attack: {e}")

    # ------------------------------------------------------------
    # Test 7: Advanced strategy detection
    # ------------------------------------------------------------
    print("[Test 7] Analyzing attack strategy sophistication...")

    # Check if using edge betweenness (common advanced strategy)
    try:
        edge_betweenness = graph.edge_betweenness()
        if len(edge_betweenness) > 0:
            # Get edges sorted by betweenness
            edges_with_betweenness = [(graph.es[i].tuple, edge_betweenness[i])
                                    for i in range(len(edge_betweenness))]
            edges_with_betweenness.sort(key=lambda x: x[1], reverse=True)

            # Check correlation with custom sequence
            betweenness_matches = 0
            for i in range(min(10, len(custom_sequence))):
                if i < len(edges_with_betweenness):
                    expected_edge = edges_with_betweenness[i][0]
                    actual_edge = custom_sequence[i]
                    if (expected_edge == actual_edge or
                        (expected_edge[1], expected_edge[0]) == actual_edge):
                        betweenness_matches += 1

            uses_betweenness = betweenness_matches >= 7
            print(f"   Strategy uses edge betweenness: {uses_betweenness} ({betweenness_matches}/10 matches)")
    except:
        print("   Could not determine if using edge betweenness")

    print("\n🎉 ALL TESTS PASSED! Custom edge attack sequence is correctly implemented.")

except Exception as e:
    print(f"❌ FAILED: Function raised an exception: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
