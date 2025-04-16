import tkinter as tk
from tkinter import simpledialog

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Drawer with Weights")
        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack()

        self.vertices = []  # list of (x, y)
        self.edges = []     # list of (v1_index, v2_index, weight)
        self.mode = None    # 'v' or 'e'
        self.edge_selection = []

        self.print_instructions()

        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("v", lambda _: self.set_mode("v"))
        self.root.bind("e", lambda _: self.set_mode("e"))

    def print_instructions(self):
        print("=== Graph Drawing Tool ===")
        print("Usage:")
        print("  Press 'v' then click to add a vertex.")
        print("  Press 'e' then click two existing vertices to connect them with an edge.")
        print("     You will be prompted to enter an optional edge weight (default is 0).")
        print("Notes:")
        print("  - Vertices are added in order and indexed starting from 0.")
        print("  - Edge weights are shown in red on the canvas.")
        print("===========================\n")

    def set_mode(self, mode):
        self.mode = mode
        if mode == 'e':
            self.edge_selection.clear()
        print(f"Mode set to: {mode}")

    def on_click(self, event):
        if self.mode == 'v':
            self.add_vertex(event.x, event.y)
        elif self.mode == 'e':
            self.select_for_edge(event.x, event.y)

    def add_vertex(self, x, y):
        radius = 5
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill='black')
        self.vertices.append((x, y))
        print(f"Added vertex {len(self.vertices)-1} at ({x}, {y})")

    def select_for_edge(self, x, y):
        v = self.get_vertex_near(x, y)
        if v is not None:
            self.edge_selection.append(v)
            print(f"Selected vertex {v} for edge")
            if len(self.edge_selection) == 2:
                v1, v2 = self.edge_selection
                weight = self.prompt_for_weight()
                self.draw_edge(v1, v2, weight)
                self.edges.append((v1, v2, weight))
                self.edge_selection.clear()

    def draw_edge(self, v1_idx, v2_idx, weight):
        x1, y1 = self.vertices[v1_idx]
        x2, y2 = self.vertices[v2_idx]
        self.canvas.create_line(x1, y1, x2, y2, fill='blue')
        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(weight), fill='red')
        print(f"Edge created between {v1_idx} and {v2_idx} with weight {weight}")

    def get_vertex_near(self, x, y, radius=10):
        for idx, (vx, vy) in enumerate(self.vertices):
            if (vx - x) ** 2 + (vy - y) ** 2 <= radius ** 2:
                return idx
        return None

    def prompt_for_weight(self):
        weight_str = simpledialog.askstring("Edge Weight", "Enter weight for the edge (default 0):")
        try:
            return float(weight_str) if weight_str else 0
        except ValueError:
            print("Invalid input. Using weight = 0.")
            return 0

   

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphGUI(root)
    root.mainloop()
