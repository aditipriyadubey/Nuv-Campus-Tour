"""
============================================================
 NAVRACHNA UNIVERSITY – CAMPUS SHORTEST PATH NAVIGATOR
 File: navigator.py
 Algorithm: Dijkstra's Shortest Path (Manual Implementation)
 Data: campus.txt (Weighted Bidirectional Graph)
============================================================
"""

import heapq
import os


# ============================================================
# 1. BUILD GRAPH FROM FILE
# ============================================================

def build_graph(filepath="campus.txt"):
    graph = {}
    nodes = set()

    if not os.path.exists(filepath):
        print(f"[ERROR] File '{filepath}' not found.")
        return graph, nodes

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) != 3:
                print(f"[WARNING] Line {line_num} skipped (bad format): '{line}'")
                continue

            node_a, node_b, weight_str = parts
            try:
                weight = int(weight_str)
            except ValueError:
                print(f"[WARNING] Line {line_num} skipped (invalid weight): '{line}'")
                continue

            # Add bidirectional edges
            if node_a not in graph:
                graph[node_a] = []
            if node_b not in graph:
                graph[node_b] = []

            graph[node_a].append((node_b, weight))
            graph[node_b].append((node_a, weight))

            nodes.add(node_a)
            nodes.add(node_b)

    print(f"[INFO] Graph built: {len(nodes)} nodes, "
          f"{sum(len(v) for v in graph.values()) // 2} edges")
    return graph, nodes

 
# ============================================================

def dijkstra(graph, source):
    # Initialize all distances to infinity
    dist = {node: float("inf") for node in graph}
    prev = {node: None for node in graph}

    if source not in graph:
        print(f"[ERROR] Source node '{source}' not in graph.")
        return dist, prev

    dist[source] = 0

    # Min-heap: (distance, node)
    heap = [(0, source)]

    while heap:
        current_dist, current_node = heapq.heappop(heap)

        # Skip if we've already found a better path
        if current_dist > dist[current_node]:
            continue

        # Explore all neighbors
        for neighbor, weight in graph.get(current_node, []):
            new_dist = current_dist + weight

            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current_node
                heapq.heappush(heap, (new_dist, neighbor))

    return dist, prev


# ============================================================
# 3. RECONSTRUCT PATH
# ============================================================

def get_path(prev, source, destination):
    
    path = []
    current = destination

    while current is not None:
        path.append(current)
        current = prev[current]

    path.reverse()

    # Validate that path actually starts from source
    if path and path[0] == source:
        return path
    return []  # No path found


# ============================================================
# 4. FORMAT TIME
# ============================================================

def format_time(seconds):

    mins = seconds // 60
    secs = seconds % 60
    if mins > 0:
        return f"{mins} min {secs} sec"
    return f"{secs} sec"


# ============================================================
# 5. DETECT VERTICAL MOVEMENT TYPE IN PATH
# ============================================================

def classify_path(path):

    uses_lift = any("_L1" in n or "_L2" in n for n in path)
    uses_s2 = any("_S2" in n for n in path)
    uses_s1 = any("_S1" in n for n in path)
    uses_s3 = any("_S3" in n for n in path)
    uses_fire = any("_FIRE" in n for n in path)

    tags = []
    if uses_lift:
        tags.append("Lift")
    if uses_s2:
        tags.append(" Stair S2 ")
    if uses_s1:
        tags.append(" Stair S1")
    if uses_s3:
        tags.append(" Stair S3")
    if uses_fire:
        tags.append(" Fire Exit")
    return ", ".join(tags) if tags else "Flat/Same-floor route"


# ============================================================
# 6. FIND AND DISPLAY SHORTEST PATH
# ============================================================

def find_shortest_path(graph, source, destination):
    """
    Main function: Runs Dijkstra and prints a clean result.
    Also tries alternate entry points via stairs vs lift.
    """
    print("\n" + "=" * 60)
    print("  NAVRACHNA UNIVERSITY – CAMPUS NAVIGATOR")
    print("=" * 60)

    # Validate nodes
    if source not in graph:
        print(f"[ERROR] '{source}' is not a valid location.")
        return
    if destination not in graph:
        print(f"[ERROR] '{destination}' is not a valid location.")
        return

    # Run Dijkstra
    dist, prev = dijkstra(graph, source)

    # Check reachability
    if dist[destination] == float("inf"):
        print(f"\n No path found from '{source}' to '{destination}'.")
        print("   Check if both nodes are connected in campus.txt")
        return

    # Get path
    path = get_path(prev, source, destination)
    total_time = dist[destination]
    vertical_tag = classify_path(path)

    print(f"\n FROM : {source}")
    print(f" TO   : {destination}")
    print(f"\n SHORTEST PATH ({len(path)} stops):")
    print()

    for i, node in enumerate(path):
        if i == 0:
            print(f"    START → {node}")
        elif i == len(path) - 1:
            print(f"    END   → {node}")
        else:
            # Show edge weight to next node
            next_node = path[i + 1]
            edge_w = next(
                (w for nb, w in graph[node] if nb == next_node), "?"
            )
            print(f"     [{edge_w}s] {node}")

    print()
    print(f"  TOTAL TIME  : {format_time(total_time)}  ({total_time} seconds)")
    print(f"  MOVEMENT    : {vertical_tag}")
    print("=" * 60)


# ============================================================
# 7. COMPARE LIFT vs STAIRS PATHS
# ============================================================

def compare_routes(graph, source, destination):
    """
    Compares 3 possible routing strategies:
      1. Default Dijkstra (optimal)
      2. Lift-only preferred (artificially boost lift)
      3. Stair S2-only preferred
    Prints a comparison table.
    """
    print("\n" + "=" * 60)
    print("  ROUTE COMPARISON: LIFT vs STAIRS")
    print("=" * 60)

    # Strategy 1: Normal Dijkstra
    dist_normal, prev_normal = dijkstra(graph, source)
    path_normal = get_path(prev_normal, source, destination)
    time_normal = dist_normal.get(destination, float("inf"))

    # Strategy 2: Penalize stairs (add 50s to all stair edges → Lift preferred)
    graph_lift = penalize_edges(graph, keywords=["_S1", "_S2", "_S3", "_FIRE"],
                                penalty=50)
    dist_lift, prev_lift = dijkstra(graph_lift, source)
    path_lift = get_path(prev_lift, source, destination)
    time_lift = dist_normal.get(destination, float("inf"))
    # Recompute actual time on original graph
    time_lift = sum_path_time(graph, path_lift)

    # Strategy 3: Penalize lifts → Stairs preferred
    graph_stair = penalize_edges(graph, keywords=["_L1", "_L2"], penalty=50)
    dist_stair, prev_stair = dijkstra(graph_stair, source)
    path_stair = get_path(prev_stair, source, destination)
    time_stair = sum_path_time(graph, path_stair)

    routes = [        
        (" Lift Preferred", path_lift, time_lift),
        (" Stairs Preferred", path_stair, time_stair),
    ]

    for label, path, t in routes:
        tag = classify_path(path)
        print(f"\n  {label}")
        print(f"     Stops : {len(path)}")
        print(f"     Time  : {format_time(t)} ({t}s)")
        print(f"     Via   : {tag}")

    print("\n" + "=" * 60)


def penalize_edges(graph, keywords, penalty):
    """Returns a modified graph copy with penalty added to edges matching keywords."""
    import copy
    g = copy.deepcopy(graph)
    for node in g:
        new_edges = []
        for (nb, w) in g[node]:
            # If this edge involves a penalized node
            if any(k in node for k in keywords) or any(k in nb for k in keywords):
                new_edges.append((nb, w + penalty))
            else:
                new_edges.append((nb, w))
        g[node] = new_edges
    return g


def sum_path_time(graph, path):
    """Calculates actual travel time for a given path on the original graph."""
    total = 0
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        edge_w = next((w for nb, w in graph.get(a, []) if nb == b), None)
        if edge_w is None:
            return float("inf")
        total += edge_w
    return total


# ============================================================
# 8. INTERACTIVE MENU
# ============================================================

def interactive_menu(graph, nodes):
    """Simple CLI menu for the user to enter source and destination."""
    sorted_nodes = sorted(nodes)

    print("\n" + "=" * 60)
    print("  NAVRACHNA UNIVERSITY – CAMPUS NAVIGATOR")
    print("  Type 'LIST' to see all locations")
    print("  Type 'QUIT' to exit")
    print("=" * 60)

    while True:
        print()
        source = input(" Enter SOURCE location : ").strip().upper()
        if source == "QUIT":
            print("Goodbye! ")
            break
        if source == "LIST":
            print("\n All Locations:")
            for i, n in enumerate(sorted_nodes, 1):
                print(f"   {i:3}. {n}")
            continue

        destination = input(" Enter DESTINATION    : ").strip().upper()
        if destination == "QUIT":
            print("Goodbye! ")
            break
        if destination == "LIST":
            print("\n All Locations:")
            for i, n in enumerate(sorted_nodes, 1):
                print(f"   {i:3}. {n}")
            continue

        find_shortest_path(graph, source, destination)

        choice = input("\n Compare Lift vs Stairs? (y/n): ").strip().lower()
        if choice == "y":
            compare_routes(graph, source, destination)

        again = input("\n Search another path? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye! ")
            break


# ============================================================
# 9. MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Build the graph from file
    graph, nodes = build_graph("campus.txt")

    if not graph:
        print("[ERROR] Graph is empty. Check campus.txt file.")
        exit(1)

    
    # ---- Interactive mode ----
    interactive_menu(graph, nodes)
