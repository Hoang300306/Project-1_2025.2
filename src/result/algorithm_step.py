from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class AlgorithmStep:

    step_number: int
    description: str

    current_vertex: Optional[int] = None

    visited_vertices: List[int] = field(default_factory=list)
    highlighted_vertices: List[int] = field(default_factory=list)
    highlighted_edges: List[Tuple[int, int]] = field(default_factory=list)

    queue_state: List[int] = field(default_factory=list)
    stack_state: List[int] = field(default_factory=list)

    distance: Dict[int, float] = field(default_factory=dict)
    parent: Dict[int, Optional[int]] = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"Step {self.step_number}: {self.description}\n"
            f"  Current vertex: {self.current_vertex}\n"
            f"  Visited: {self.visited_vertices}\n"
            f"  Highlight vertices: {self.highlighted_vertices}\n"
            f"  Highlight edges: {self.highlighted_edges}\n"
            f"  Queue: {self.queue_state}\n"
            f"  Stack: {self.stack_state}\n"
            f"  Distance: {self.distance}\n"
            f"  Parent: {self.parent}"
        )