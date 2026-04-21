"""
============================================================
 NAVRACHNA UNIVERSITY – CAMPUS NAVIGATOR BACKEND
 File: app.py
 Framework: Flask (pip install flask)
 Run: python app.py
 API: http://localhost:5000
============================================================
"""

from flask import Flask, request, jsonify, send_from_directory
import heapq
import os

app = Flask(__name__, static_folder=".")

# ============================================================
# GRAPH BUILDER (same logic as navigator.py)
# ============================================================

from navigator import (
    build_graph,
    dijkstra,
    get_path,
    format_time,
    sum_path_time,
    penalize_edges,
    classify_path
)
# Load graph once at startup
GRAPH, NODES = build_graph("campus.txt")


# ============================================================
# API ROUTES
# ============================================================

@app.route("/")
def index():
    """Serve the frontend HTML file."""
    return send_from_directory(".", "index.html")


@app.route("/api/nodes", methods=["GET"])
def get_nodes():
    """Return all node names sorted (for dropdowns)."""
    return jsonify({"nodes": sorted(NODES)})


@app.route("/api/shortest-path", methods=["POST"])
def shortest_path():
    """
    POST body: { "source": "A_1_ENTRY", "destination": "A_8_TINKER" }
    Returns optimal path + lift/stairs comparison.
    """
    data = request.get_json()
    source = data.get("source", "").strip().upper()
    destination = data.get("destination", "").strip().upper()

    if source not in GRAPH:
        return jsonify({"error": f"Source '{source}' not found in campus map."}), 400
    if destination not in GRAPH:
        return jsonify({"error": f"Destination '{destination}' not found in campus map."}), 400

    # --- Route 1: Optimal ---
    dist, prev = dijkstra(GRAPH, source)
    if dist[destination] == float("inf"):
        return jsonify({"error": "No path found between these locations."}), 404

    path = get_path(prev, source, destination)
    time_optimal = dist[destination]

    # --- Route 2: Lift preferred ---
    g_lift = penalize_edges(GRAPH, ["_S1", "_S2", "_S3", "_FIRE"], 50)
    d2, p2 = dijkstra(g_lift, source)
    path_lift = get_path(p2, source, destination)
    time_lift = sum_path_time(GRAPH, path_lift)

    # --- Route 3: Stairs preferred ---
    g_stair = penalize_edges(GRAPH, ["_L1", "_L2"], 50)
    d3, p3 = dijkstra(g_stair, source)
    path_stair = get_path(p3, source, destination)
    time_stair = sum_path_time(GRAPH, path_stair)

    return jsonify({
        "optimal": {
            "path": path,
            "time_seconds": time_optimal,
            "time_formatted": format_time(time_optimal),
            "stops": len(path),
            "movement": classify_path(path)
        },
        "lift_preferred": {
            "path": path_lift,
            "time_seconds": time_lift,
            "time_formatted": format_time(time_lift),
            "stops": len(path_lift),
            "movement": classify_path(path_lift)
        },
        "stair_preferred": {
            "path": path_stair,
            "time_seconds": time_stair,
            "time_formatted": format_time(time_stair),
            "stops": len(path_stair),
            "movement": classify_path(path_stair)
        }
    })


if __name__ == "__main__":
    print("=" * 50)
    print(" Navrachna University Campus Navigator")
    print(" Running at http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
