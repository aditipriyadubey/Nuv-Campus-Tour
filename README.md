# Navrachna University Campus Tour: Shortest Path Navigation System
### DAA End-Semester Project Report

---

## 1. Problem Statement

Universities are large, multi-floor, multi-building environments where students, staff, and visitors frequently struggle to navigate from one location to another — especially in time-sensitive situations such as reaching a class before it begins, finding the admin office, or locating a specific lab.

**The Problem:**
> Given any two locations within Navrachna University's campus, find the *shortest path* (minimum travel time in seconds) between them, considering all possible walking routes, staircases, lifts, and inter-block outdoor connections.

**Why this matters:**
- A new student may not know the fastest path from C Block Admission to A Block's Tinker Lab on Floor 8.
- A visitor needs to reach the Moot Court from the main gate efficiently.
- Faculty need to move between buildings between back-to-back lectures.

**Real-World Application:**
This project mirrors how Google Maps, airport navigation kiosks, and hospital wayfinding systems work. The core insight is the same: model the physical space as a *graph* and use a proven shortest-path algorithm to compute optimal routes in milliseconds.

---

## 2. Graph Modeling: How the Campus Becomes a Data Structure

### 2.1 The 3D Graph Concept

Navrachna University is a **3-dimensional space**:

| Dimension | Represents | Example |
|-----------|-----------|---------|
| X-axis | Block | A, B, C |
| Y-axis | Location (room/area) | 601, LABS, STAFF, ADMIN |
| Z-axis | Floor number | 1 through 8 |

Every location is encoded as a node with the naming convention:

```
Block_Floor_Location
e.g.: A_6_LABS, B_3_302, C_G_CANTEEN
```

Where `G` = Ground, `B` = Basement.

### 2.2 Nodes (Vertices)

Each node represents a *physical location*:
- **Classrooms**: A_1_109, B_2_201, etc.
- **Staircases**: A_1_S1, A_1_S2, A_1_S3, A_1_FIRE
- **Lifts**: A_1_L1, A_1_L2
- **Special rooms**: A_8_TINKER, A_5_AUDITORIUM, A_8_COUNSELL, A_3_WOMEN_SLEEP
- **Ground facilities**: A_G_LIBRARY, A_G_MOOTCOURT, A_G_TEAPOST, A_G_NCC
- **Inter-block**: C_G_CANTEEN, C_1_ADMISSION, B_G_GATE, B_B_MUSIC

### 2.3 Edges (Connections)

Each edge represents a *walkable path* between two locations. The edge weight is **travel time in seconds**.

```
A_6_601 → A_6_LABS   weight = 20  (20 seconds to walk to lab from 601)
A_1_L1  → A_2_L1     weight = 5   (5 seconds per floor in lift)
A_1_S2  → A_2_S2     weight = 15  (15 seconds per floor, fastest stair)
```

All edges are **bidirectional**: if you can walk A→B, you can walk B→A in the same time.

### 2.4 Vertical Movement Summary

| Route | Speed | Notes |
|-------|-------|-------|
| Lift L1 / L2 | 5 sec/floor | Fastest but may have wait time |
| Staircase S2 (Nescafe) | 15 sec/floor | Fastest stair |
| Fire Exit | 20 sec/floor | Emergency / less-preferred |
| Staircase S1 (Tropical Bistro) | 30 sec/floor | Moderate |
| Staircase S3 (Tea Post) | 35 sec/floor | Slowest, less crowded |

### 2.5 Inter-Block Connections

| Route | Path | Type |
|-------|------|------|
| Route 1 | C_G_ENTRY → C_G_CANTEEN → C_1_ADMISSION → B_1_BLOCK → A_1_ENTRY | Fastest structured |
| Route 2 | C_G_ENTRY → A_G_ENTRY → A_G_NCC → A_G_MECHLAB | Medium outdoor |
| Route 3 | B_G_GATE → B_G_STAIRS → B_B_STATIONARY → C_G_CANTEEN | Basement alternate |

---

## 3. Algorithm: Dijkstra's Shortest Path

### 3.1 Why Dijkstra?

Dijkstra's algorithm is the industry standard for single-source shortest paths on graphs with **non-negative weights**. Since our edge weights are travel times (always ≥ 0), Dijkstra is ideal.

Alternatives considered:
- **BFS**: Only works on unweighted graphs. ❌
- **Bellman-Ford**: Handles negative weights but is slower — O(VE). Unnecessary here. ❌
- **A\***: Excellent for geographic grids; requires a heuristic. Our graph is not purely spatial. ⚠️
- **Dijkstra**: Perfect fit. Fast, correct, well-understood. ✅

### 3.2 Algorithm Steps

```
1. Initialize dist[source] = 0, dist[all others] = ∞
2. Initialize prev[all] = None
3. Push (0, source) into a min-heap priority queue
4. While heap is not empty:
   a. Pop node with smallest distance → (d, u)
   b. If d > dist[u]: skip (stale entry)
   c. For each neighbor v of u with edge weight w:
      - new_dist = dist[u] + w
      - If new_dist < dist[v]:
          dist[v] = new_dist
          prev[v] = u
          Push (new_dist, v) to heap
5. Reconstruct path: trace prev[] from destination back to source
```

### 3.3 Time Complexity

| Component | Complexity |
|-----------|-----------|
| Graph build | O(E) |
| Dijkstra with min-heap | O((V + E) log V) |
| Path reconstruction | O(V) |
| **Total** | **O((V + E) log V)** |

Where:
- **V** = number of nodes (locations) ≈ 200+
- **E** = number of edges (connections) ≈ 400+

Even for the full campus graph, this runs in **milliseconds**.

### 3.4 Space Complexity

- Adjacency list: O(V + E)
- Distance array: O(V)
- Previous array: O(V)
- Heap: O(V)
- **Total: O(V + E)**

---

## 4. Advanced Features

### 4.1 Route Comparison (Lift vs Stairs)

The system generates **three route variants**:

1. **Optimal (Auto)**: Pure Dijkstra — finds mathematically shortest path regardless of route type.
2. **Lift Preferred**: Penalizes stair edges by +50 seconds → forces algorithm to prefer lifts wherever possible.
3. **Stairs Preferred**: Penalizes lift edges by +50 seconds → algorithm routes through stairs.

This lets users choose based on real-world constraints:
- Lift is broken? → Use Stairs Preferred mode.
- Mobility concerns? → Use Lift Preferred mode.
- Fastest possible? → Use Optimal.

### 4.2 Input Validation

```python
if source not in graph:
    print(f"[ERROR] '{source}' is not a valid location.")
    return
```

Handles:
- Invalid node names
- Disconnected components (unreachable destinations)
- Same source and destination

### 4.3 Path Classification

The system auto-detects what kind of vertical movement was used:
```
🛗 Lift, 🔥 Stair S2 (Fastest), 🚶 Stair S1, 🐢 Stair S3, 🚨 Fire Exit
```

---

## 5. Web UI: Flask Integration Guide

### 5.1 Running the System

```bash
# Step 1: Install Flask
pip install flask

# Step 2: Ensure these files are in the same folder:
#   app.py
#   navigator.py
#   campus.txt
#   index.html

# Step 3: Run backend
python app.py

# Step 4: Open browser
# http://localhost:5000
```

### 5.2 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves the HTML frontend |
| `/api/nodes` | GET | Returns all node names (for dropdowns) |
| `/api/shortest-path` | POST | Runs Dijkstra, returns 3 routes |

### 5.3 API Request/Response Example

**Request:**
```json
POST /api/shortest-path
{
  "source": "C_G_ENTRY",
  "destination": "A_8_TINKER"
}
```

**Response:**
```json
{
  "optimal": {
    "path": ["C_G_ENTRY", "C_G_CANTEEN", "C_1_ADMISSION", "B_1_BLOCK",
             "A_1_ENTRY", "A_1_L1", "A_2_L1", "A_3_L1", "A_4_L1",
             "A_5_L1", "A_6_L1", "A_7_L1", "A_8_L1", "A_8_TINKER"],
    "time_seconds": 235,
    "time_formatted": "3 min 55 sec",
    "stops": 14,
    "movement": "Lift"
  },
  "lift_preferred": { ... },
  "stair_preferred": { ... }
}
```

### 5.4 Standalone Demo Mode

The `index.html` file includes a **full JavaScript implementation** of Dijkstra — identical logic to the Python version. This means the web UI works completely offline as a demo, even without Flask running.

---

## 6. File Structure

```
navrachna-navigator/
│
├── campus.txt          ← Graph edge data (all locations + weights)
├── navigator.py        ← Python: graph build + Dijkstra + CLI interface
├── app.py              ← Flask backend API server
├── index.html          ← Web UI (works standalone + connects to Flask)
└── README.md           ← This report
```

---

## 7. Sample Output (CLI)

```
============================================================
  NAVRACHNA UNIVERSITY – CAMPUS NAVIGATOR
============================================================

📍 FROM : C_G_ENTRY
🏁 TO   : A_8_TINKER

🗺️  SHORTEST PATH (14 stops):

   🟢 START → C_G_ENTRY
   ➡️  [30s] C_G_CANTEEN
   ➡️  [20s] C_1_ADMISSION
   ➡️  [20s] B_1_BLOCK
   ➡️  [30s] A_1_ENTRY
   ➡️  [8s] A_1_L1
   ➡️  [5s] A_2_L1
   ➡️  [5s] A_3_L1
   ➡️  [5s] A_4_L1
   ➡️  [5s] A_5_L1
   ➡️  [5s] A_6_L1
   ➡️  [5s] A_7_L1
   ➡️  [5s] A_8_L1
   🔴 END   → A_8_TINKER

⏱️  TOTAL TIME  : 3 min 55 sec  (235 seconds)
🏗️  MOVEMENT    : 🛗 Lift
============================================================
```

---

## 8. Why This is a Real-World Navigation System

| Real System | Our System |
|-------------|------------|
| Google Maps nodes | Rooms, labs, stairs, lifts |
| Road distance | Walking time (seconds) |
| Traffic layers | Stair speed / lift availability |
| Route alternatives | Lift vs Stairs comparison |
| Dijkstra's algorithm | Dijkstra's algorithm ✅ |
| 2D map | 3D campus (Block × Location × Floor) |

The only difference between this project and a production navigation app is:
1. **Scale** (we have ~200 nodes vs millions)
2. **Real-time data** (we don't account for lift wait times dynamically)
3. **UI polish** (a mobile app with actual maps)

The algorithmic core is identical.

---

## 9. Conclusion

This project successfully models Navrachna University's campus as a **3D weighted graph** and applies **Dijkstra's shortest path algorithm** to solve real navigation problems. Key achievements:

- ✅ Complete campus graph with 200+ nodes across 3 blocks, 8 floors
- ✅ Manual Dijkstra implementation (no external libraries)
- ✅ Lift vs Stairs comparison with edge penalization strategy
- ✅ Clean Python CLI with interactive menu
- ✅ Flask REST API backend
- ✅ Modern Web UI with live Dijkstra visualization
- ✅ Proper input validation and error handling

The project demonstrates that **graph theory and DAA concepts are not abstract** — they power the navigation tools billions of people use every day.

---

*Navrachna University | Design and Analysis of Algorithms | End-Semester Project*
