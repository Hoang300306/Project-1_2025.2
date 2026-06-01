from dataclasses import dataclass

@dataclass
class Vertex:
    id: int
    label: str = ""
    x: float = 0.0
    y: float = 0.0

    def __post_init__(self):
        if not self.label:
            self.label = str(self.id)

    def __str__(self) -> str:
        return f"Vertex(id={self.id}, label='{self.label}')"


