import json
import pandas as pd
import numpy as np

def load_graph(path="graph.json", directed=False):
    """Load graph from file and return structured data.

    Args:
        path (str): Path to graph.json file
        directed (bool): Whether to treat edges as directed

    Returns:
        dict: {
            "vertices": List of (x, y),
            "edges": List of (v1, v2, weight),
            "edge_df": Pandas DataFrame,
            "adj_matrix": NumPy adjacency matrix
        }
    """
    with open(path, "r") as f:
        graph = json.load(f)

    vertices = graph["vertices"]
    edges = graph["edges"]

    df_edges = pd.DataFrame(edges, columns=["v1", "v2", "weight"])

    n = len(vertices)
    adj_matrix = np.zeros((n, n))

    for v1, v2, w in edges:
        adj_matrix[v1][v2] = w
        if not directed:
            adj_matrix[v2][v1] = w

    return {
        "vertices": vertices,
        "edges": edges,
        "edge_df": df_edges,
        "adj_matrix": adj_matrix
    }
