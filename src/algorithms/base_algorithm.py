from abc import ABC, abstractmethod

from src.model.graph import Graph
from src.result.algorithm_result import AlgorithmResult
from src.result.algorithm_parameter import AlgorithmParameter

class GraphAlgorithm(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def can_run(self, graph: Graph) -> bool:
        pass

    @abstractmethod
    def run(self, graph: Graph, parameters: AlgorithmParameter) -> AlgorithmResult:
        pass
    