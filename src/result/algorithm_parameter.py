from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class AlgorithmParameter:
    start_vertex: Optional[int] = None
    target_vertex: Optional[int] = None
    heuristic: Dict[int, float] = field(default_factory=dict)


