import os
import shutil
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import sys
from analyze_graph import load_graph

IMG_DIR = "../visualizationImages"
VID_DIR = "../visualizationVideos"
VIDEO_NAME = "label_correcting_tree.mp4"

def setup_directories():
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(VID_DIR, exist_ok=True)
    for f in os.listdir(IMG_DIR):
        os.remove(os.path.join(IMG_DIR, f))

def run_gui_and_load_graph():
    print("Launching graph GUI... Close it after pressing 's' to save.")
    subprocess.run(["python", "graph_generating_script.py", "directed"])
    time.sleep(1)
    return load_graph(directed=True)

def draw_frame(graph, Pr, dd, current_edge, frame_number, relax_happened):
    coords = graph["vertices"]
    edges = graph["edges"]

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    for i, (x, y) in enumerate(coords):
        axs[0, 0].scatter(x, y, color='black')
        axs[0, 0].text(x, y - 10, f"v{i}", ha='center', fontsize=9)

    for v1, v2, w in edges:
        x1, y1 = coords[v1]
        x2, y2 = coords[v2]
        edge_color = 'green' if (v1, v2) == current_edge and relax_happened else (
                      'red' if (v1, v2) == current_edge else 'blue')
        axs[0, 0].annotate("",
                          xy=(x2, y2), xycoords='data',
                          xytext=(x1, y1), textcoords='data',
                          arrowprops=dict(arrowstyle="->", color=edge_color, lw=2))
        axs[0, 0].text((x1 + x2)/2, (y1 + y2)/2, str(w), color='red', fontsize=8)

    axs[0, 0].set_title("Original Graph - Scan Arc")
    axs[0, 0].invert_yaxis()
    axs[0, 0].axis("equal")

    for i, (x, y) in enumerate(coords):
        axs[1, 0].scatter(x, y, color='black')
        axs[1, 0].text(x, y - 10, f"v{i}", ha='center', fontsize=9)

    for v, u in Pr.items():
        if u is not None:
            x1, y1 = coords[u]
            x2, y2 = coords[v]
            w = graph["adj_matrix"][u][v]
            axs[1, 0].annotate("",
                              xy=(x2, y2), xycoords='data',
                              xytext=(x1, y1), textcoords='data',
                              arrowprops=dict(arrowstyle="->", color='green', lw=2))
            axs[1, 0].text((x1 + x2)/2, (y1 + y2)/2, str(w), color='red', fontsize=8)

    axs[1, 0].set_title("Current Tree")
    axs[1, 0].invert_yaxis()
    axs[1, 0].axis("equal")

    axs[0, 1].axis("off")
    axs[0, 1].set_title("Distance Estimates")
    for i, d in dd.items():
        display = f"v{i}: {'inf' if d == float('inf') else round(d, 2)}"
        axs[0, 1].text(0.1, 1 - i * 0.05, display, fontsize=12)

    axs[1, 1].axis("off")

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

def label_correcting_scan(graph):
    coords = graph["vertices"]
    adj = graph["adj_matrix"]
    n = len(coords)

    dd = {i: float("inf") for i in range(n)}
    Pr = {i: None for i in range(n)}
    visit_count = {i: 0 for i in range(n)}
    dd[0] = 0
    frame_number = 0
    draw_frame(graph, Pr, dd, None, frame_number, False)
    frame_number += 1

    arcs = [(u, v) for u in range(n) for v in range(n) if adj[u][v] != 0]

    for _ in range(n - 1):
        changed = False
        for u, v in arcs:
            relax_happened = False
            if dd[u] + adj[u][v] < dd[v]:
                dd[v] = dd[u] + adj[u][v]
                Pr[v] = u
                relax_happened = True
                changed = True
            draw_frame(graph, Pr, dd, (u, v), frame_number, relax_happened)
            frame_number += 1
        if not changed:
            break

    for u, v in arcs:
        if dd[u] + adj[u][v] < dd[v]:
            print("❌ Negative-weight cycle detected. Aborting.")
            return None, None

    draw_frame(graph, Pr, dd, None, frame_number, False)
    return dd, Pr

def main():
    print("The first node placed will be considered node s")
    setup_directories()
    graph = run_gui_and_load_graph()

    dd, Pr = label_correcting_scan(graph)

    if dd is None:
        sys.exit(1)

    print("\n📊 Shortest distances from v0:")
    for i in range(len(graph["vertices"])):
        d = dd[i]
        status = f"{d}" if d != float("inf") else "unreachable"
        print(f"v{i}: {status}")

    save_video()

if __name__ == "__main__":
    main()