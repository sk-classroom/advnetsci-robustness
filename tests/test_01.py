# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy>=1.20.0",
#     "python-igraph>=0.11.0",
#     "requests>=2.31.0",
#     "marimo",
# ]
# ///

# %% Import
import sys
import os
import igraph

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from assignment.assignment import degree_edge_attack_sequence
from utils import construct_london_transport_network

# %% Setup
g = construct_london_transport_network()

# %% Test Degree-based Edge Attack Sequence
print("=" * 60)
print("TEST 01: Degree-based Edge Attack Sequence")
print("=" * 60)

# ------------------------------------------------------------
# Test Setup
# ------------------------------------------------------------
if g is None:
    print("❌ FAILED: Could not load test network")
    exit(1)

print(f"📊 Test network: {g.vcount()} nodes, {g.ecount()} edges")

try:
    edge_sequence = degree_edge_attack_sequence(g)

    # ------------------------------------------------------------
    # Test 1: Function returns a list
    # ------------------------------------------------------------
    print(f"[Test 1] Function returns list: {isinstance(edge_sequence, list)}")
    assert isinstance(edge_sequence, list), "Function must return a list"

    # ------------------------------------------------------------
    # Test 2: Correct number of edges
    # ------------------------------------------------------------
    expected_edges = g.ecount()
    print(f"[Test 2] Correct edge count: expected {expected_edges}, got {len(edge_sequence)}")
    assert len(edge_sequence) == expected_edges, f"Expected {expected_edges} edges, got {len(edge_sequence)}"

    # ------------------------------------------------------------
    # Test 3: All elements are tuples with 2 elements
    # ------------------------------------------------------------
    all_tuples = all(isinstance(edge, tuple) and len(edge) == 2 for edge in edge_sequence)
    print(f"[Test 3] All edges are (source, target) tuples: {all_tuples}")
    assert all_tuples, "All edges must be (source, target) tuples"

    # ------------------------------------------------------------
    # Test 4: All edges exist in the original graph
    # ------------------------------------------------------------
    original_edges = set((e.source, e.target) for e in g.es)
    original_edges.update((e.target, e.source) for e in g.es)  # Add reverse edges

    all_exist = all((source, target) in original_edges for source, target in edge_sequence)
    print(f"[Test 4] All edges exist in original graph: {all_exist}")
    assert all_exist, "All edges must exist in the original graph"

    # ------------------------------------------------------------
    # Test 5: No duplicate edges
    # ------------------------------------------------------------
    edge_set = set(edge_sequence)
    no_duplicates = len(edge_set) == len(edge_sequence)
    print(f"[Test 5] No duplicate edges: {no_duplicates} (unique: {len(edge_set)}, total: {len(edge_sequence)})")
    assert no_duplicates, f"Duplicate edges found. Unique: {len(edge_set)}, Total: {len(edge_sequence)}"

    # ------------------------------------------------------------
    # Test 6: Edges are sorted by degree product (descending order)
    # ------------------------------------------------------------
    degrees = g.degree()
    degree_products = []
    for edge in edge_sequence:
        source, target = edge
        degree_product = degrees[source] * degrees[target]
        degree_products.append(degree_product)

    # Check if sorted in descending order
    is_sorted = all(degree_products[i] >= degree_products[i+1] for i in range(len(degree_products)-1))
    print(f"[Test 6] Edges sorted by degree product (descending): {is_sorted}")
    if not is_sorted:
        print(f"   First 10 degree products: {degree_products[:10]}")
    assert is_sorted, "Edges must be sorted by degree product (descending)"

    # ------------------------------------------------------------
    # Test 7: Strategy effectiveness analysis
    # ------------------------------------------------------------
    print(f"[Test 7] Strategy analysis:")
    print(f"   Highest degree product: {degree_products[0]}")
    print(f"   Lowest degree product: {degree_products[-1]}")
    print(f"   Average degree product: {sum(degree_products) / len(degree_products):.2f}")

    # First few edges should connect high-degree nodes
    high_degree_threshold = max(degrees) * 0.7
    high_degree_edges = sum(1 for i in range(min(10, len(edge_sequence)))
                           if degrees[edge_sequence[i][0]] >= high_degree_threshold or
                              degrees[edge_sequence[i][1]] >= high_degree_threshold)

    print(f"   High-degree edges in top 10: {high_degree_edges}/10")

    print("\n🎉 ALL TESTS PASSED! Degree-based edge attack sequence is correctly implemented.")

except Exception as e:
    print(f"❌ FAILED: Function raised an exception: {e}")
    import traceback
    traceback.print_exc()
    exit(1)