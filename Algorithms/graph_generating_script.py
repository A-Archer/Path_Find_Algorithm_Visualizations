import tkinter as tk
from tkinter import simpledialog
import json
import sys

# Default mode
MODE = "undirected"
if len(sys.argv) > 1 and sys.argv[1] in ["directed", "undirected"]:
    MODE = sys.argv[1]

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Graph Drawer ({MODE.title()})")
        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack()

        self.vertices = []
        self.edges = []
        self.mode = None
        self.edge_selection = []

        self.print_instructions()

        self.canvas.bind("<Button-1>", self.on_click)
        for widget in [self.root, self.canvas]:
            widget.bind("<Key>", self.key_handler)
            widget.focus_set()

    def print_instructions(self):
        print(f"=== Graph Drawing Tool ({MODE.title()} Mode) ===")
        print("Instructions:")
        print("  Press 'v' then click to add a vertex.")
        print("  Press 'e' then click two vertices to connect them.")
        print("    → First click = tail, Second click = head")
        print("  Press 's' to save the graph as 'graph.json'.")
        print("  Press 'g' to print current vertices and edges.")
        print("==========================================\n")

    def key_handler(self, event):
        if event.char == 'v':
            self.set_mode("v")
        elif event.char == 'e':
            self.set_mode("e")
        elif event.char == 'g':
            self.output_graph()
        elif event.char == 's':
            self.save_graph_to_file()

    def set_mode(self, mode):
        self.mode = mode
        if mode == 'e':
            self.edge_selection.clear()

    def on_click(self, event):
        if self.mode == 'v':
            self.add_vertex(event.x, event.y)
        elif self.mode == 'e':
            self.select_for_edge(event.x, event.y)

    def add_vertex(self, x, y):
        radius = 5
        idx = len(self.vertices)
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill='black')
        self.canvas.create_text(x, y - 10, text=f"v{idx}", fill='black')
        self.vertices.append((x, y))

    def select_for_edge(self, x, y):
        v = self.get_vertex_near(x, y)
        if v is not None:
            self.edge_selection.append(v)
            if len(self.edge_selection) == 2:
                v1, v2 = self.edge_selection
                weight = self.prompt_for_weight()
                self.draw_edge(v1, v2, weight)
                self.edges.append((v1, v2, weight))
                if MODE == "undirected":
                    self.edges.append((v2, v1, weight))
                self.edge_selection.clear()

    def draw_edge(self, v1_idx, v2_idx, weight):
        x1, y1 = self.vertices[v1_idx]
        x2, y2 = self.vertices[v2_idx]
        self.canvas.create_line(x1, y1, x2, y2, fill='blue')
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(weight), fill='red')

    def get_vertex_near(self, x, y, radius=10):
        for idx, (vx, vy) in enumerate(self.vertices):
            if (vx - x) ** 2 + (vy - y) ** 2 <= radius ** 2:
                return idx
        return None

    def prompt_for_weight(self):
        weight_str = simpledialog.askstring("Edge Weight", "Enter weight (default 0):")
        try:
            return float(weight_str) if weight_str else 0
        except ValueError:
            return 0

    def output_graph(self):
        print("\nGraph:")
        print("Vertices:")
        for i in range(len(self.vertices)):
            print(f"v{i}")
        print("Edges (v1, v2, weight):")
        for v1, v2, w in self.edges:
            print(f"v{v1} → v{v2} : weight {w}")

    def save_graph_to_file(self):
        with open("graph.json", "w") as f:
            json.dump({
                "vertices": self.vertices,
                "edges": self.edges
            }, f, indent=2)
        print("Graph saved to graph.json")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphGUI(root)
    root.mainloop()
