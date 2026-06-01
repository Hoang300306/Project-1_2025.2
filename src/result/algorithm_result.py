from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.result.algorithm_step import AlgorithmStep


@dataclass
class AlgorithmResult:
    algorithm_name: str
    success: bool = True
    message: str = ""

    traversal_order: List[int] = field(default_factory=list)
    path: List[int] = field(default_factory=list)
    result_edges: List[Tuple[int, int]] = field(default_factory=list)

    distance: Dict[int, float] = field(default_factory=dict)
    parent: Dict[int, Optional[int]] = field(default_factory=dict)

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

        if self.distance:
            lines.append(f"Distance: {self.distance}")

        return "\n".join(lines)