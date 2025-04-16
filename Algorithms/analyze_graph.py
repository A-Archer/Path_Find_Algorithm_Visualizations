import json
import pandas as pd
import numpy as np

def load_graph(path="graph.json"):
    """Load graph from file and return structured data."""
    with open(path, "r") as f:
        graph = json.load(f)

    vertices = graph["vertices"]  # list of (x, y)
    edges = graph["edges"]        # list of (v1, v2, weight)

    df_edges = pd.DataFrame(edges, columns=["v1", "v2", "weight"])

    n = len(vertices)
    adj_matrix = np.zeros((n, n))
    for v1, v2, w in edges:
        adj_matrix[v1][v2] = w
        adj_matrix[v2][v1] = w  # remove if directed

    return {
        "vertices": vertices,
        "edges": edges,
        "edge_df": df_edges,
        "adj_matrix": adj_matrix
    }
