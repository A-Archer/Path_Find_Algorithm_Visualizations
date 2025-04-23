import tkinter as tk
from tkinter import simpledialog
import json
import os
import sys
from analyze_graph import load_graph

PRIMAL_GRAPH_PATH = "graph.json"
DUAL_GRAPH_PATH = "dual_graph.json"

class DualGraphOverlay:
    def __init__(self, root, primal_graph):
        self.root = root
        self.primal_graph = primal_graph
        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack()

        self.dual_vertices = []
        self.dual_edges = []
        self.dual_to_primal_map = {}
        self.edge_selection = []
        self.s_hat = None
        self.t_hat = None

        self.draw_primal_graph()

        self.print_instructions()

        self.canvas.bind("<Button-1>", self.on_click)
        for widget in [self.root, self.canvas]:
            widget.bind("<Key>", self.key_handler)
            widget.focus_set()

    def print_instructions(self):
        print("=== Dual Graph Overlay Tool ===")
        print("Instructions:")
        print("  Press 'd' then click to add a dual vertex (face center).")
        print("  Press 'e' then click two dual vertices to connect them (assign length).")
        print("  Press 's' then click a dual vertex to mark as s_hat.")
        print("  Press 't' then click a dual vertex to mark as t_hat.")
        print("  Press 'w' to save dual graph as 'dual_graph.json'.")
        print("  Press 'q' to quit without saving.")
        print("==========================================\n")

    def key_handler(self, event):
        if event.char == 'd':
            self.mode = 'dual_vertex'
        elif event.char == 'e':
            self.mode = 'dual_edge'
            self.edge_selection.clear()
        elif event.char == 's':
            self.mode = 's_hat'
        elif event.char == 't':
            self.mode = 't_hat'
        elif event.char == 'w':
            self.save_dual_graph()
        elif event.char == 'q':
            print("❌ Quit without saving.")
            self.root.quit()

    def draw_primal_graph(self):
        coords = self.primal_graph["vertices"]
        edges = self.primal_graph["edges"]
        for i, (x, y) in enumerate(coords):
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='gray')
            self.canvas.create_text(x, y - 10, text=f"v{i}", fill='black')
        for v1, v2, w in edges:
            x1, y1 = coords[v1]
            x2, y2 = coords[v2]
            self.canvas.create_line(x1, y1, x2, y2, fill='lightblue')
            self.canvas.create_text((x1 + x2)//2, (y1 + y2)//2, text=f"{w}", fill='red')

    def on_click(self, event):
        if self.mode == 'dual_vertex':
            self.add_dual_vertex(event.x, event.y)
        elif self.mode == 'dual_edge':
            self.select_for_dual_edge(event.x, event.y)
        elif self.mode == 's_hat':
            idx = self.get_dual_vertex_near(event.x, event.y)
            if idx is not None:
                self.s_hat = idx
                x, y = self.dual_vertices[idx]
                self.canvas.create_text(x, y + 15, text="s_hat", fill='green', font=('Arial', 10, 'bold'))
                print(f"✔️ s_hat set to dual vertex {idx}")
        elif self.mode == 't_hat':
            idx = self.get_dual_vertex_near(event.x, event.y)
            if idx is not None:
                self.t_hat = idx
                x, y = self.dual_vertices[idx]
                self.canvas.create_text(x, y + 15, text="t_hat", fill='red', font=('Arial', 10, 'bold'))
                print(f"✔️ t_hat set to dual vertex {idx}")

    def add_dual_vertex(self, x, y):
        idx = len(self.dual_vertices)
        self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='purple')
        self.canvas.create_text(x, y - 10, text=f"d{idx}", fill='purple')
        self.dual_vertices.append((x, y))

    def select_for_dual_edge(self, x, y):
        idx = self.get_dual_vertex_near(x, y)
        if idx is not None:
            self.edge_selection.append(idx)
            if len(self.edge_selection) == 2:
                v1, v2 = self.edge_selection
                length = self.prompt_for_length()
                x1, y1 = self.dual_vertices[v1]
                x2, y2 = self.dual_vertices[v2]
                self.canvas.create_line(x1, y1, x2, y2, fill='purple')
                self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(length), fill='purple')
                self.dual_edges.append((v1, v2, length))

                # Map to primal edge
                mapped_edge = self.prompt_for_primal_edge()
                if mapped_edge:
                    key = f"{v1},{v2}"
                    self.dual_to_primal_map[key] = mapped_edge

                self.edge_selection.clear()

    def get_dual_vertex_near(self, x, y, radius=10):
        for idx, (vx, vy) in enumerate(self.dual_vertices):
            if (vx - x) ** 2 + (vy - y) ** 2 <= radius ** 2:
                return idx
        return None

    def prompt_for_length(self):
        weight_str = simpledialog.askstring("Dual Edge Length", "Enter length (default 0):")
        try:
            return float(weight_str) if weight_str else 0
        except ValueError:
            return 0

    def prompt_for_primal_edge(self):
        edges = self.primal_graph["edges"]
        seen = set()
        edge_display = []
        edge_map = {}

        for u, v, w in edges:
            e = tuple(sorted((u, v)))
            if e not in seen:
                idx = len(edge_display)
                edge_display.append(f"{idx}: v{e[0]} — v{e[1]} (weight {w})")
                edge_map[str(idx)] = f"{e[0]},{e[1]}"
                seen.add(e)

        choice = simpledialog.askstring("Map Dual Edge", "Which primal edge does this dual edge intersect?\n\n" +
                                        "\n".join(edge_display) + "\n\nEnter index number:")
        if choice in edge_map:
            return edge_map[choice]
        else:
            print("❌ Invalid primal edge selection.")
            return None
        
    def save_dual_graph(self):
        data = {
            "dual_vertices": self.dual_vertices,
            "dual_edges": self.dual_edges,
            "dual_to_primal_map": self.dual_to_primal_map,
            "s_hat": self.s_hat,
            "t_hat": self.t_hat
        }
        with open(DUAL_GRAPH_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Dual graph saved to {DUAL_GRAPH_PATH}")
        self.root.quit()
    


if __name__ == "__main__":
    print("Loading primal graph for dual overlay...")
    primal_graph = load_graph(PRIMAL_GRAPH_PATH, directed=False)
    root = tk.Tk()
    app = DualGraphOverlay(root, primal_graph)
    root.mainloop()
