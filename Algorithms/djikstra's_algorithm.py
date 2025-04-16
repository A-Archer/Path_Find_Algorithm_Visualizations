import subprocess
import time
from analyze_graph import load_graph

def run_gui_and_load_graph():
    print("Launching graph GUI... Close it after pressing 's' to save.")
    subprocess.run(["python", "graph_generating_script.py"])
    time.sleep(1)
    return load_graph()

def main():
    graph = run_gui_and_load_graph()

    print("\nLoaded Graph Info")
    print("------------------")
    print("Vertices:")
    for i in range(len(graph["vertices"])):
        print(f"v{i}")
    print("\nEdge List:")
    print(graph["edge_df"])

    print("\nAdjacency Matrix:")
    print(graph["adj_matrix"])

if __name__ == "__main__":
    main()
