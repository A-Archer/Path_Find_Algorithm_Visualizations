import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import subprocess
from analyze_graph import load_graph
from collections import deque

IMG_DIR = "../visualizationImages"
VID_DIR = "../visualizationVideos"
VIDEO_NAME = "ford_fulkerson_visualization.mp4"

# Ensure frame and video directories are clean
def setup_directories():
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(VID_DIR, exist_ok=True)
    for f in os.listdir(IMG_DIR):
        os.remove(os.path.join(IMG_DIR, f))

# Launch GUI and load directed graph
def run_gui_and_load_graph():
    print("Launching graph GUI... Close it after pressing 's' to save.")
    subprocess.run(["python", "graph_generating_script.py", "directed"])
    time.sleep(1)
    return load_graph(directed=True)

# BFS to find path from source to sink, returns parent map and path as a list
def bfs(capacity, flow, source, sink):
    n = len(capacity)
    parent = [-1] * n
    visited = [False] * n
    queue = deque([source])
    visited[source] = True
    discovered_edges = set()
    while queue:
        u = queue.popleft()
        for v in range(n):
            if not visited[v] and capacity[u][v] - flow[u][v] > 0:
                parent[v] = u
                visited[v] = True
                discovered_edges.add((u, v))
                queue.append(v)
                if v == sink:
                    path = []
                    while v != source:
                        path.append(v)
                        v = parent[v]
                    path.append(source)
                    return list(reversed(path)), discovered_edges
    return None, discovered_edges

# Compute reachable set from source in residual graph
def get_reachable(capacity, flow, source):
    n = len(capacity)
    visited = [False] * n
    queue = deque([source])
    visited[source] = True
    while queue:
        u = queue.popleft()
        for v in range(n):
            if not visited[v] and capacity[u][v] - flow[u][v] > 0:
                visited[v] = True
                queue.append(v)
    return visited

# Draw frame with all four subplots
def draw_frame(pos, capacity, flow, original_edges, path, bottleneck, reachable, discovered_edges, frame_idx, total_flow, source, sink, final_frame_idx):
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    # Top Left - Original Graph with Capacities
    ax_orig = axs[0, 0]
    G_orig = nx.DiGraph()
    G_orig.add_nodes_from(range(len(pos)))
    for u, v, w in original_edges:
        G_orig.add_edge(u, v, capacity=w)
    edge_labels = {(u, v): f"{capacity[u][v]:.0f}" for u, v, _ in original_edges}
    nx.draw(G_orig, pos, ax=ax_orig, node_color='lightblue', with_labels=True, arrows=True)
    nx.draw_networkx_edge_labels(G_orig, pos, edge_labels=edge_labels, ax=ax_orig, font_color='red')
    ax_orig.set_title("Original Graph with Capacities")

    # Top Right - Min Cut Coloring
    ax_cut = axs[0, 1]
    G_cut = nx.DiGraph()
    G_cut.add_nodes_from(range(len(pos)))
    for u, v, _ in original_edges:
        G_cut.add_edge(u, v)
    node_colors = []
    for i in range(len(pos)):
        if frame_idx == final_frame_idx:
            node_colors.append('green' if reachable[i] else 'red')
        else:
            if i == source:
                node_colors.append('blue')
            elif i == sink:
                node_colors.append('red')
            else:
                node_colors.append('gray')
    nx.draw(G_cut, pos, ax=ax_cut, node_color=node_colors, with_labels=True, arrows=True)
    ax_cut.set_title("Min s-t Cut Coloring")

    # Bottom Left - Residual Graph with BFS
    ax_res = axs[1, 0]
    G_res = nx.DiGraph()
    G_res.add_nodes_from(range(len(pos)))
    labels = {}
    for u in range(len(capacity)):
        for v in range(len(capacity)):
            res_cap = capacity[u][v] - flow[u][v]
            if res_cap > 0:
                G_res.add_edge(u, v)
                labels[(u, v)] = f"{res_cap:.0f}"
    colors = []
    for u, v in G_res.edges():
        if path and (u, v) in zip(path, path[1:]):
            if bottleneck and (u, v) == bottleneck:
                colors.append('red')
            else:
                colors.append('lime')
        elif (u, v) in discovered_edges:
            colors.append('cyan')
        else:
            colors.append('blue')
    nx.draw(G_res, pos, ax=ax_res, edge_color=colors, with_labels=True, node_color='skyblue', arrows=True)
    nx.draw_networkx_edge_labels(G_res, pos, edge_labels=labels, ax=ax_res, font_color='magenta')
    ax_res.set_title("Residual Graph with BFS")

    # Bottom Right - Flow Graph
    ax_flow = axs[1, 1]
    G_flow = nx.DiGraph()
    G_flow.add_nodes_from(range(len(pos)))
    labels = {}
    for u, v, _ in original_edges:
        if flow[u][v] > 0:
            G_flow.add_edge(u, v)
            labels[(u, v)] = f"{flow[u][v]:.0f}"
    nx.draw(G_flow, pos, ax=ax_flow, node_color='black', with_labels=True, arrows=True, edge_color='green')
    nx.draw_networkx_edge_labels(G_flow, pos, edge_labels=labels, ax=ax_flow, font_color='green')
    ax_flow.set_title(f"Flow Graph -> Max Flow = {total_flow:.1f}")

    plt.tight_layout()
    path = os.path.join(IMG_DIR, f"frame_{frame_idx:03d}.png")
    plt.savefig(path)
    plt.close()

# Compile images into video using ffmpeg
def save_video():
    output_path = os.path.join(VID_DIR, VIDEO_NAME)
    subprocess.run([
        "ffmpeg", "-y", "-framerate", "0.5",
        "-i", os.path.join(IMG_DIR, "frame_%03d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path
    ])
    print(f"🎞️  Video saved to: {output_path}")

# Main driver
if __name__ == "__main__":
    setup_directories()
    graph = run_gui_and_load_graph()
    pos = graph["vertices"]
    edges = graph["edges"]
    original_edges = [(u, v, w) for u, v, w in edges]
    n = len(pos)
    capacity = [[0]*n for _ in range(n)]
    flow = [[0]*n for _ in range(n)]
    for u, v, w in edges:
        capacity[u][v] = w

    source = 0
    sink = len(pos) - 1
    print("Vertex positions and IDs:")
    for i, (x, y) in enumerate(pos):
        print(f"v{i}: ({x}, {y})")
    print(f"Source (s): v{source}, Sink (t): v{sink}")

    frame = 0
    total_flow = 0

    reach = get_reachable(capacity, flow, source)
    final_frame_idx = -1
    draw_frame(pos, capacity, flow, original_edges, None, None, reach, set(), frame, total_flow, source, sink, final_frame_idx)
    frame += 1

    while True:
        path, discovered = bfs(capacity, flow, source, sink)
        if not path:
            break

        reach = get_reachable(capacity, flow, source)
        draw_frame(pos, capacity, flow, original_edges, None, None, reach, discovered, frame, total_flow, source, sink, -1)
        frame += 1

        draw_frame(pos, capacity, flow, original_edges, path, None, reach, discovered, frame, total_flow, source, sink, -1)
        frame += 1

        bottleneck_val = float('inf')
        bottleneck = None
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            if capacity[u][v] - flow[u][v] < bottleneck_val:
                bottleneck_val = capacity[u][v] - flow[u][v]
                bottleneck = (u, v)

        draw_frame(pos, capacity, flow, original_edges, path, bottleneck, reach, discovered, frame, total_flow, source, sink, -1)
        frame += 1

        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            flow[u][v] += bottleneck_val

        total_flow += bottleneck_val
        reach = get_reachable(capacity, flow, source)
        draw_frame(pos, capacity, flow, original_edges, path, None, reach, discovered, frame, total_flow, source, sink, -1)
        frame += 1

    final_frame_idx = frame
    reach = get_reachable(capacity, flow, source)
    draw_frame(pos, capacity, flow, original_edges, None, None, reach, set(), frame, total_flow, source, sink, final_frame_idx)
    save_video()