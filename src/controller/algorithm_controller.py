from typing import Dict, List

from src.algorithms.base_algorithm import GraphAlgorithm
from src.algorithms.bfs_algorithm import BFSAlgorithm
from src.algorithms.dfs_algorithm import DFSAlgorithm
from src.algorithms.dijkstra_algorithm import DijkstraAlgorithm
from src.algorithms.prim_algorithm import PrimAlgorithm
from src.algorithms.kruskal_algorithm import KruskalAlgorithm
from src.algorithms.bellman_ford_algorithm import BellmanFordAlgorithm
from src.algorithms.floyd_warshall_algorithm import FloydWarshallAlgorithm
from src.algorithms.topological_sort_algorithm import TopologicalSortAlgorithm

from src.model.graph import Graph
from src.result.algorithm_parameter import AlgorithmParameter
from src.result.algorithm_result import AlgorithmResult
from src.service.graph_validator import GraphValidator

class AlgorithmController:
    def __init__(self):
        self.algorithms: Dict[str, GraphAlgorithm] = {}
        self._register_default_algorithms()

    def _register_default_algorithms(self) -> None:
        """
        Đăng ký các thuật toán mặc định của hệ thống.
        Sau này muốn thêm Dijkstra, Prim, Kruskal thì thêm tại đây.
        """
        self.register_algorithm("bfs", BFSAlgorithm())
        self.register_algorithm("dfs", DFSAlgorithm())
        self.register_algorithm('dijkstra', DFSAlgorithm())
        self.register_algorithm('prim', PrimAlgorithm())
        self.register_algorithm('kruskal', KruskalAlgorithm())
        
        self.register_algorithm("bellman_ford", BellmanFordAlgorithm())
        self.register_algorithm("bellman-ford", BellmanFordAlgorithm())

        self.register_algorithm("floyd_warshall", FloydWarshallAlgorithm())
        self.register_algorithm("floyd-warshall", FloydWarshallAlgorithm())
        self.register_algorithm("floyd", FloydWarshallAlgorithm())

        self.register_algorithm("topological_sort", TopologicalSortAlgorithm())
        self.register_algorithm("topological", TopologicalSortAlgorithm())
        self.register_algorithm("topo", TopologicalSortAlgorithm())
        self.register_algorithm("toposort", TopologicalSortAlgorithm())

    def register_algorithm(self, name: str, algorithm: GraphAlgorithm) -> None:
        """
        Đăng ký một thuật toán mới vào controller.
        """
        key = name.lower().strip()
        self.algorithms[key] = algorithm

    def get_available_algorithms(self) -> List[str]:
        """
        Trả về danh sách tên các thuật toán hiện có.
        """
        return list(self.algorithms.keys())
    
    def get_algorithm(self, name: str) -> GraphAlgorithm | None:
        """
        Lấy thuật toán theo tên.
        """
        key = name.lower().strip()
        return self.algorithms.get(key)

    def get_algorithm_description(self, name: str) -> str:
        """
        Lấy mô tả thuật toán theo tên.
        """
        algorithm = self.get_algorithm(name)

        if algorithm is None:
            return f"Không tìm thấy thuật toán: {name}"

        return algorithm.get_description()
    
    def run_algorithm(
        self,
        name: str,
        graph: Graph,
        params: AlgorithmParameter
    ) -> AlgorithmResult:
        algorithm = self.get_algorithm(name)

        if algorithm is None:
            return AlgorithmResult(
                algorithm_name=name,
                success=False,
                message=f"Thuật toán '{name}' chưa được hỗ trợ."
            )
        validation = GraphValidator.validate_for_algorithm(name, graph)
        if not validation.valid:
            return AlgorithmResult(
                algorithm_name=algorithm.get_name(),
                success=False,
                message=validation.message
            )
        if not algorithm.can_run(graph):
            return AlgorithmResult(
                algorithm_name=algorithm.get_name(),
                success=False,
                message=f"Thuật toán {algorithm.get_name()} không thể chạy trên đồ thị hiện tại."
            )
        return algorithm.run(graph, params)
    
        if validation.warnings and result.success:
            warning_text = " ".join(validation.warnings)
            result.message = result.message + f"\nCảnh báo: {warning_text}"

        return result