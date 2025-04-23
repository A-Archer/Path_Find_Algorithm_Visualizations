import os
import time
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import json
from analyze_graph import load_graph

IMG_DIR = "../visualizationImages"
VID_DIR = "../visualizationVideos"
VIDEO_NAME = "planar_flow_cut_final.mp4"

def setup_directories():
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(VID_DIR, exist_ok=True)
    for f in os.listdir(IMG_DIR):
        os.remove(os.path.join(IMG_DIR, f))

def run_primal_graph_gui():
    subprocess.run(["python", "graph_generating_script.py", "undirected"])
    time.sleep(1)

def run_dual_graph_overlay():
    subprocess.run(["python", "dual_graph_overlay.py"])
    time.sleep(1)

def load_dual_graph(path="dual_graph.json"):
    with open(path, "r") as f:
        return json.load(f)

def dijkstra_dual_with_path(dual_vertices, dual_edges, s_hat, t_hat):
    distances = {i: float('inf') for i in range(len(dual_vertices))}
    parents = {i: None for i in range(len(dual_vertices))}
    distances[s_hat] = 0
    visited = set()
    frames = []

    while len(visited) < len(dual_vertices):
        unvisited = [v for v in distances if v not in visited]
        if not unvisited:
            break
        v = min(unvisited, key=lambda x: distances[x])
        visited.add(v)
        for u1, u2, length in dual_edges:
            for u, w in [(u1, u2), (u2, u1)]:
                if u == v and w not in visited:
                    if distances[v] + length < distances[w]:
                        distances[w] = distances[v] + length
                        parents[w] = v
                        frames.append((w, dict(distances)))

    min_cut_dual_edges = []
    curr = t_hat
    while parents[curr] is not None:
        prev = parents[curr]
        min_cut_dual_edges.append((prev, curr))
        curr = prev
    min_cut_dual_edges.reverse()

    return distances, frames, min_cut_dual_edges

def get_primal_cut_edges(dual_to_primal_map, min_cut_dual_edges):
    cut_edges = set()
    for u, v in min_cut_dual_edges:
        key1 = f"{u},{v}"
        key2 = f"{v},{u}"
        edge_str = dual_to_primal_map.get(key1) or dual_to_primal_map.get(key2)
        if edge_str:
            e = tuple(sorted(map(int, edge_str.split(','))))
            cut_edges.add(e)
    return cut_edges

def compute_flow_with_geometry(primal_graph, dual_graph, potentials):
    flow = {}
    pos = primal_graph["vertices"]
    dual_pos = dual_graph["dual_vertices"]

    for dual_key, primal_edge_str in dual_graph["dual_to_primal_map"].items():
        dual_u, dual_v = map(int, dual_key.split(','))
        u, v = map(int, primal_edge_str.split(','))

        phi_left = potentials[dual_u]
        phi_right = potentials[dual_v]
        flow_value = phi_right - phi_left

        # Geometry: Determine which face is on which side
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        xd, yd = dual_pos[dual_u]
        xc, yc = (x1 + x2) / 2, (y1 + y2) / 2  # center of primal edge

        # Normal vector to edge (perpendicular, left-hand rule)
        nx, ny = -(y2 - y1), (x2 - x1)

        # Vector from edge center to dual face
        vx, vy = xd - xc, yd - yc
        dot_product = nx * vx + ny * vy

        if dot_product > 0:
            # dual_u (phi_left) is to the left of (u,v)
            if flow_value > 0:
                flow[(u, v)] = flow_value
            elif flow_value < 0:
                flow[(v, u)] = -flow_value
        else:
            # dual_u is to the right, flip
            if flow_value > 0:
                flow[(v, u)] = flow_value
            elif flow_value < 0:
                flow[(u, v)] = -flow_value

    return flow


def draw_frame(primal_graph, dual_graph, flows, frame_idx, potentials=None,
               highlight_dual=None, min_cut_dual_edges=None, cut_edges=None):
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    pos = primal_graph["vertices"]
    edges = primal_graph["edges"]
    dual_vertices = dual_graph["dual_vertices"]
    dual_edges = dual_graph["dual_edges"]

    # Top Left: Primal Graph with Capacities Only
    ax1 = axs[0, 0]
    for i, (x, y) in enumerate(pos):
        label = 's' if i == 0 else ('t' if i == len(pos)-1 else f"v{i}")
        ax1.scatter(x, y, color='black')
        ax1.text(x, y - 10, label, ha='center', fontsize=9)
    for v1, v2, w in edges:
        x1, y1 = pos[v1]
        x2, y2 = pos[v2]
        ax1.plot([x1, x2], [y1, y2], color='blue')
        ax1.text((x1 + x2)/2, (y1 + y2)/2, f"{w}", color='red')
    ax1.set_title("Original Graph (Capacities)")
    ax1.invert_yaxis()
    ax1.axis("equal")

    # Top Right: Dual Graph with Potentials
    ax2 = axs[0, 1]
    for i, (x, y) in enumerate(dual_vertices):
        color = 'green' if i == dual_graph["s_hat"] else ('red' if i == dual_graph["t_hat"] else 'purple')
        ax2.scatter(x, y, color=color)
        label = 's_hat' if i == dual_graph["s_hat"] else ('t_hat' if i == dual_graph["t_hat"] else f"f{i}")
        if potentials:
            label += f"\n{round(potentials[i], 2) if potentials[i] != float('inf') else '∞'}"
        ax2.text(x, y - 10, label, ha='center', fontsize=9)
    for u, v, length in dual_edges:
        x1, y1 = dual_vertices[u]
        x2, y2 = dual_vertices[v]
        edge_color = 'orange' if highlight_dual == v else 'gray'
        ax2.plot([x1, x2], [y1, y2], color=edge_color)
        ax2.text((x1 + x2)//2, (y1 + y2)//2, f"{length}", color='black')
    if min_cut_dual_edges:
        for u, v in min_cut_dual_edges:
            x1, y1 = dual_vertices[u]
            x2, y2 = dual_vertices[v]
            ax2.plot([x1, x2], [y1, y2], color='red', linewidth=2)
    ax2.set_title("Dual Graph (Potentials)")
    ax2.invert_yaxis()
    ax2.axis("equal")

    # Bottom Left: Primal Graph with Cut Edges Highlighted & Face Potentials
    ax3 = axs[1, 0]
    for i, (x, y) in enumerate(pos):
        label = 's' if i == 0 else ('t' if i == len(pos)-1 else f"v{i}")
        ax3.scatter(x, y, color='black')
        ax3.text(x, y - 10, label, ha='center', fontsize=9)
    for v1, v2, _ in edges:
        e = tuple(sorted((v1, v2)))
        x1, y1 = pos[v1]
        x2, y2 = pos[v2]
        edge_color = 'red' if cut_edges and e in cut_edges else 'blue'
        ax3.plot([x1, x2], [y1, y2], color=edge_color)
    if potentials:
        for i, (x, y) in enumerate(dual_vertices):
            label = f"φ(f{i}) = {round(potentials[i], 2)}" if potentials[i] != float('inf') else f"φ(f{i}) = ∞"
            ax3.text(x, y, label, ha='center', fontsize=9, color='purple')
    ax3.set_title("Primal Graph Highlighted Min-Cut + Face Potentials")
    ax3.invert_yaxis()
    ax3.axis("equal")

    # Bottom Right: Flow via Potentials (Single Direction Arrows)
    ax4 = axs[1, 1]
    for i, (x, y) in enumerate(pos):
        label = 's' if i == 0 else ('t' if i == len(pos)-1 else f"v{i}")
        ax4.scatter(x, y, color='black')
        ax4.text(x, y - 10, label, ha='center', fontsize=9)

    for (u, v), flow_val in flows.items():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax4.annotate("",
                     xy=(x2, y2), xycoords='data',
                     xytext=(x1, y1), textcoords='data',
                     arrowprops=dict(arrowstyle="->", color='green', lw=2))
        ax4.text((x1 + x2) / 2, (y1 + y2) / 2, f"{flow_val:.1f}",
                 color='black', fontsize=9, ha='center', va='center',
                 bbox=dict(facecolor='white', edgecolor='none', pad=1.0))

    ax4.set_title("Flow via Potentials (Direction & Magnitude)")
    ax4.invert_yaxis()
    ax4.axis("equal")

    frame_path = os.path.join(IMG_DIR, f"frame_{frame_idx:03d}.png")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(frame_path)
    plt.close()

def save_video():
    output_path = os.path.join(VID_DIR, VIDEO_NAME)
    input_path = os.path.join(IMG_DIR, "frame_%03d.png").replace("\\", "/")
    output_path = output_path.replace("\\", "/")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", "0.5",
        "-i", input_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path
    ])
    print(f"🎞️  Video saved to: {output_path}")

def main():
    setup_directories()
    run_primal_graph_gui()
    run_dual_graph_overlay()

    primal_graph = load_graph(directed=False)
    dual_graph = load_dual_graph()

    draw_frame(primal_graph, dual_graph, {}, 0)

    distances, dijkstra_frames, min_cut_dual_edges = dijkstra_dual_with_path(
        dual_graph["dual_vertices"], dual_graph["dual_edges"], dual_graph["s_hat"], dual_graph["t_hat"])

    frame_idx = 1
    for highlight_node, dist_snapshot in dijkstra_frames:
        draw_frame(primal_graph, dual_graph, {}, frame_idx, potentials=dist_snapshot, highlight_dual=highlight_node)
        frame_idx += 1

    cut_edges = get_primal_cut_edges(dual_graph["dual_to_primal_map"], min_cut_dual_edges)

    flows = compute_flow_with_geometry(primal_graph, dual_graph, distances)

    draw_frame(primal_graph, dual_graph, flows, frame_idx, potentials=distances,
               min_cut_dual_edges=min_cut_dual_edges, cut_edges=cut_edges)

    save_video()


if __name__ == "__main__":
    main()
