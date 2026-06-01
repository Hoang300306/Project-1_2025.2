from dataclasses import dataclass

@dataclass

class Edge:
    source: int
    target: int
    weight: float = 1.0

    def __str__(self) -> str:
        return f"Edge({self.source} -> {self.target}, weight={self.weight})"
    
    def as_tuple(self) -> tuple[int, int, float]:
        return self.source, self.target, self.weight
    


