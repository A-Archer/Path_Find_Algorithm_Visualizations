# Ford-Fulkerson and Graph Algorithms Visualization

This project provides visualizations for classic graph algorithms including:

- **Ford-Fulkerson Algorithm** (for computing max flow and min s-t cut)
- **Label Correcting Algorithm** (for shortest path trees)
- **Dijkstra's Algorithm** (for shortest paths)
- **Planar Graph Flow-Cut Visualization** (for duality-based max-flow and min-cut)

All visualizations are interactive and allow users to define custom graphs using a GUI tool.

---

## 📂 Project Structure

```
Project Root/
├── Algorithms/
│   ├── analyze_graph.py                  # Loads graph data from JSON and provides adjacency matrix
│   ├── dijkstra's_algorithm.py           # Visualizes Dijkstra's shortest path algorithm
│   ├── ford_fulkerson_algorithm.py       # Visualizes Ford-Fulkerson max flow algorithm
│   ├── label_correcting_algorithm.py     # Visualizes Label Correcting shortest path tree
│   ├── planar_graph_flow_cut_algorithm.py# Visualizes planar graph duality, min-cut, max-flow
│   ├── graph_generating_script.py        # GUI tool to create and save primal graphs
│   ├── dual_graph_overlay.py             # GUI tool to define dual graphs on top of primal
│   ├── graph.json                        # Stores user-created primal graph data
│   ├── dual_graph.json                   # Stores user-defined dual graph overlay data
├── visualizationImages/                  # Frames for video generation
├── visualizationVideos/                  # Generated algorithm videos
└── README.md                             # Documentation (this file)
```

---

## ⚙️ Dependencies

Ensure you have Python 3.x installed.

Install required packages:

```bash
pip install matplotlib networkx pandas numpy
```

For video generation:
- **ffmpeg** must be installed and accessible from the command line.

---

## 🚀 How to Run Visualizations

### 1. Create the Primal Graph

```bash
python Algorithms/graph_generating_script.py undirected
```

- Press **'v'** then click to add vertices.
- Press **'e'** then click two vertices to create **undirected edges** (with weights).
- Press **'s'** to save your primal graph to `Algorithms/graph.json`.

---

### 2. Overlay the Dual Graph (for Planar Flow-Cut)

```bash
python Algorithms/dual_graph_overlay.py
```

- Define the dual graph by placing nodes on faces of the primal graph.
- Link dual nodes to form dual edges intersecting primal edges.
- Press **'s'** to save to `Algorithms/dual_graph.json`.

---

### 3. Run Planar Graph Flow-Cut Visualization

```bash
python Algorithms/planar_graph_flow_cut_algorithm.py
```

- Visualizes:
  - Original graph with capacities.
  - Dual graph with potentials.
  - Min-cut computed from dual shortest path.
  - Max-flow via face potentials and geometric flow direction.
- Generates video: `visualizationVideos/planar_flow_cut_final.mp4`

---

## 📊 Video Outputs

- **visualizationImages/**: Intermediate PNG frames for all visualizations.
- **visualizationVideos/**: Final videos for each algorithm.

### Video Layouts:

- **Planar Flow-Cut (planar_flow_cut_final.mp4)**:
  - **Top-left**: Original graph with edge capacities.
  - **Top-right**: Dual graph showing potentials and min-cut path.
  - **Bottom-left**: Primal graph with min-cut highlighted and face potentials labeled.
  - **Bottom-right**: Flow computed from potentials, arrows showing correct direction and magnitude.

- **Ford-Fulkerson (ford_fulkerson_visualization.mp4)**:
  - Top-left: Original graph with capacities.
  - Top-right: Min-cut coloring after completion.
  - Bottom-left: Residual graph with BFS paths and bottlenecks.
  - Bottom-right: Flow accumulation.

- **Label Correcting (label_correcting_tree.mp4)**:
  - Scan arcs, relaxed edges, current shortest tree.

- **Dijkstra's Algorithm (dijkstra_tree.mp4)**:
  - Step-by-step shortest path tree updates.

---

## ❗ Notes

- **First node** placed in primal GUI = **source (s)**.
- **Last node** placed in primal GUI = **sink (t)**.
- For **Planar Flow-Cut**, both primal and dual graphs are needed.
- Flow directions use geometry-based heuristics for accurate arrow placement.

---

## 🔧 Troubleshooting

- **ffmpeg** required for video creation.
- GUI issues? Ensure **Tkinter** is installed with Python.
- **Flow direction errors**: Ensure dual graph and intersections are properly aligned.

---

## 📞 Contact

Feel free to open issues or reach out for improvements, bugs, or contributions!