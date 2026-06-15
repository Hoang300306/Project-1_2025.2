from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class AlgorithmStep:
    """
    Class biểu diễn một bước trong quá trình chạy thuật toán.
    Dùng để lưu trạng thái thuật toán tại từng bước, phục vụ debug và visualization.
    """

    step_number: int
    description: str

    current_vertex: Optional[int] = None

    visited_vertices: List[int] = field(default_factory=list)
    highlighted_vertices: List[int] = field(default_factory=list)
    highlighted_edges: List[Tuple[int, int]] = field(default_factory=list)

    queue_state: List[int] = field(default_factory=list)
    stack_state: List[int] = field(default_factory=list)

    # Dùng cho Dijkstra/Prim.
    priority_queue_state: List[tuple] = field(default_factory=list)

    # Dùng cho BFS/DFS/Dijkstra/Bellman-Ford.
    distance: Dict[int, float] = field(default_factory=dict)
    parent: Dict[int, Optional[int]] = field(default_factory=dict)

    # Dùng cho Floyd-Warshall.
    distance_matrix: Dict[int, Dict[int, float]] = field(default_factory=dict)
    next_matrix: Dict[int, Dict[int, Optional[int]]] = field(default_factory=dict)

    # Dự phòng cho các thuật toán sau.
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = [
            f"Step {self.step_number}: {self.description}",
            f"  Current vertex: {self.current_vertex}",
            f"  Visited: {self.visited_vertices}",
            f"  Highlight vertices: {self.highlighted_vertices}",
            f"  Highlight edges: {self.highlighted_edges}",
            f"  Queue: {self.queue_state}",
            f"  Stack: {self.stack_state}",
            f"  Priority queue: {self.priority_queue_state}",
            f"  Distance: {self.distance}",
            f"  Parent: {self.parent}",
        ]

        if self.distance_matrix:
            lines.append("  Distance matrix:")
            lines.append(self._format_matrix(self.distance_matrix))

        if self.extra_data:
            lines.append(f"  Extra data: {self.extra_data}")

        return "\n".join(lines)

    def _format_matrix(self, matrix: Dict[int, Dict[int, float]]) -> str:
        vertices = sorted(matrix.keys())

        result = []

        header = "      " + " ".join(f"{v:>6}" for v in vertices)
        result.append(header)

        for i in vertices:
            row = [f"{i:>4}:"]

            for j in vertices:
                value = matrix[i][j]

                if value == float("inf"):
                    row.append(f"{'∞':>6}")
                elif float(value).is_integer():
                    row.append(f"{int(value):>6}")
                else:
                    row.append(f"{value:>6}")

            result.append(" ".join(row))

        return "\n".join(result)