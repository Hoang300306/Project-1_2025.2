from collections import defaultdict
from typing import List, Dict, Set, Tuple

from src.model.edge import Edge
from src.model.vertex import Vertex

class Graph:
    def __init__(self, directed: bool = False, weighted: bool = False):
        self.directed = directed
        self.weighted = weighted
        self.vertices: Dict[int, Vertex] = {}
        self.edges: List[Edge] = []
        #adjacency[u] cach canh di ra tu u
        self.adjacency: Dict[int, List[Edge]] = defaultdict(list)

    def add_vertex(self, vertex_id: int, label: str = "") -> None:
        if vertex_id not in self.vertices:#check xem ton tai chua de them
            self.vertices[vertex_id] = Vertex(vertex_id, label)
    
    def add_edge(self, source: int, target: int, weight: float = 1.0) -> None:
        self.add_vertex(source)
        self.add_vertex(target)
        edge = Edge(source, target, weight)

        if not self.weighted:    #ko weight thi auto = 1
            weight = 1.0

        self.edges.append(edge)
        self.adjacency[source].append(edge)

        if not self.directed:
            reverse_edge = Edge(target, source, weight)
            self.adjacency[target].append(reverse_edge)


    def get_vertex(self, vertex_id: int) -> Vertex:
        return self.vertices.get(vertex_id)
    
    def get_vertices(self) -> List[Vertex]:
        return list(self.vertices.values())
    
    def get_edges(self) -> List[Edge]:
        return self.edges
    
    def get_out_edges(self, vertex_id: int) -> List[Edge]:
        return self.adjacency.get(vertex_id, [])
    
    def get_neighbors(self, vertex_id: int) -> List[Tuple[int, float]]:
        neighbors = []
        for edge in self.get_out_edges(vertex_id):
            neighbors.append((edge.target, edge.weight))
        return neighbors
    
    def has_vertex(self, vertex_id: int) -> bool:
        return vertex_id in self.vertices
    
    def has_negative_edge(self) -> bool:
        return any(edge.weight < 0 for edge in self.edges)
    
    def number_of_vertices(self) -> int:
        return len(self.vertices)
    
    def number_of_edges(self) -> int:
        return len(self.edges)
    
    def clear(self) -> None:
        self.vertices.clear()
        self.edges.clear()
        self.adjacency.clear()

    def __str__(self) -> str:
        graph_type = "Directed" if self.directed else "Undirected"
        weight_type = "Weighted" if self.weighted else "Unweighted"

        lines = [
            f"Graph type: {graph_type}, {weight_type}",
            f"Number of vertices: {self.number_of_vertices()}",
            f"Number of edges: {self.number_of_edges()}",
            "Edges:"
        ]

        for edge in self.edges:
            lines.append(f"{edge.source} -> {edge.target} (weight={edge.weight})")
        
        return "\n".join(lines)




