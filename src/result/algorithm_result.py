from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.result.algorithm_step import AlgorithmStep


@dataclass
class AlgorithmResult:
    """
    Class lưu kết quả sau khi chạy thuật toán.
    """

    algorithm_name: str
    success: bool = True
    message: str = ""

    traversal_order: List[int] = field(default_factory=list)
    path: List[int] = field(default_factory=list)
    result_edges: List[Tuple[int, int]] = field(default_factory=list)

    distance: Dict[int, float] = field(default_factory=dict)
    parent: Dict[int, Optional[int]] = field(default_factory=dict)

    distance_matrix: Dict[int, Dict[int, float]] = field(default_factory=dict)
    next_matrix: Dict[int, Dict[int, Optional[int]]] = field(default_factory=dict)

    total_cost: Optional[float] = None

    steps: List[AlgorithmStep] = field(default_factory=list)

    def get_summary(self) -> str:
        lines = [
            f"Algorithm: {self.algorithm_name}",
            f"Success: {self.success}",
            f"Message: {self.message}",
        ]

        if self.traversal_order:
            lines.append(f"Traversal order: {' -> '.join(map(str, self.traversal_order))}")

        if self.path:
            lines.append(f"Path: {' -> '.join(map(str, self.path))}")

        if self.result_edges:
            edge_text = ", ".join([f"{u}-{v}" for u, v in self.result_edges])
            lines.append(f"Result edges: {edge_text}")

        if self.total_cost is not None:
            if float(self.total_cost).is_integer():
                lines.append(f"Total cost: {int(self.total_cost)}")
            else:
                lines.append(f"Total cost: {self.total_cost}")

        if self.distance:
            lines.append(f"Distance: {self.distance}")

        if self.distance_matrix:
            lines.append("Distance matrix:")
            lines.append(self._format_matrix(self.distance_matrix))

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