import os
import shutil
import json
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import sys
from analyze_graph import load_graph

# Set directories
IMG_DIR = "../visualizationImages"
VID_DIR = "../visualizationVideos"
VIDEO_NAME = "dijkstra_tree.mp4"

def setup_directories():
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(VID_DIR, exist_ok=True)
    for f in os.listdir(IMG_DIR):
        os.remove(os.path.join(IMG_DIR, f))

def run_gui_and_load_graph():
    print("Launching graph GUI... Close it after pressing 's' to save.")
    subprocess.run(["python", "graph_generating_script.py", "undirected"])
    time.sleep(1)
    return load_graph(directed=False)

def draw_frame(graph, F, Pr, current_edge, frame_number):
    coords = graph["vertices"]
    edges = graph["edges"]

    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # Left plot: original graph + progress
    for i, (x, y) in enumerate(coords):
        color = 'green' if i in F else 'gray'
        axs[0].scatter(x, y, color=color)
        axs[0].text(x, y - 10, f"v{i}", ha='center', fontsize=9)

    for v1, v2, w in edges:
        x1, y1 = coords[v1]
        x2, y2 = coords[v2]
        edge_color = 'blue'
        if current_edge == (v1, v2) or current_edge == (v2, v1):
            edge_color = 'red'
        axs[0].plot([x1, x2], [y1, y2], color=edge_color)
        axs[0].text((x1 + x2)/2, (y1 + y2)/2, str(w), color='red', fontsize=8)

    axs[0].set_title("Original Graph - Progress")
    axs[0].invert_yaxis()
    axs[0].axis("equal")

    # Right plot: current tree
    for i, (x, y) in enumerate(coords):
        axs[1].scatter(x, y, color='black')
        axs[1].text(x, y - 10, f"v{i}", ha='center', fontsize=9)

    for child, parent in Pr.items():
        if parent is not None:
            x1, y1 = coords[parent]
            x2, y2 = coords[child]
            w = graph["adj_matrix"][parent][child]
            axs[1].plot([x1, x2], [y1, y2], color='green')
            axs[1].text((x1 + x2)/2, (y1 + y2)/2, str(w), color='red', fontsize=8)

    axs[1].set_title("Shortest Path Tree (F)")
    axs[1].invert_yaxis()
    axs[1].axis("equal")

    plt.tight_layout()
    plt.savefig(os.path.join(IMG_DIR, f"frame_{frame_number:03d}.png"))
    plt.close()

def save_video():
    output_path = os.path.join(VID_DIR, VIDEO_NAME)
    subprocess.run([
        "ffmpeg", "-y", "-framerate", "0.5",
        "-i", os.path.join(IMG_DIR, "frame_%03d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path
    ])
    print(f"🎞️  Video saved to: {output_path}")

def dijkstra_with_visualization(graph):
    F = []
    dd = {i: (0 if i == 0 else float("inf")) for i in range(len(graph["vertices"]))}
    Pr = {i: None for i in range(len(graph["vertices"]))}

    frame_number = 0
    draw_frame(graph, F, Pr, None, frame_number)
    frame_number += 1

    while any(v not in F and dd[v] < float("inf") for v in range(len(graph["vertices"]))):
        unvisited = [v for v in range(len(graph["vertices"])) if v not in F]
        v = min(unvisited, key=lambda x: dd[x])
        F.append(v)

        for w in range(len(graph["vertices"])):
            if w not in F and graph["adj_matrix"][v][w] > 0:
                current_edge = (v, w)
                if dd[v] + graph["adj_matrix"][v][w] < dd[w]:
                    dd[w] = dd[v] + graph["adj_matrix"][v][w]
                    Pr[w] = v
                draw_frame(graph, F, Pr, current_edge, frame_number)
                frame_number += 1

    draw_frame(graph, F, Pr, None, frame_number)
    return dd, Pr

def main():
    print("The first node placed will be considered node s")
    setup_directories()
    graph = run_gui_and_load_graph()

    if any(w < 0 for _, _, w in graph["edges"]):
        print("❌ Error: All edge weights must be non-negative for Dijkstra's algorithm.")
        sys.exit(1)

    print("✅ All edge weights are non-negative.")
    dd, Pr = dijkstra_with_visualization(graph)

    print("\n📊 Shortest distances from v0:")
    for i in range(len(graph["vertices"])):
        d = dd[i]
        status = f"{d}" if d != float("inf") else "unreachable"
        print(f"v{i}: {status}")

    save_video()

if __name__ == "__main__":
    main()