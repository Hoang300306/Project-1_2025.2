from typing import Dict, List

from src.algorithms.base_algorithm import GraphAlgorithm
from src.algorithms.bfs_algorithm import bfs_algorithm
from src.algorithms.dfs_algorithm import dfs_algorithm
from src.model.graph import Graph
from src.result.algorithm_parameter import AlgorithmParameter
from src.result.algorithm_result import AlgorithmResult

class AlgorithmController:
    def __init__(self):
        self.algorithms: Dict[str, GraphAlgorithm] = {}
        self._register_default_algorithms()

    def _register_default_algorithms(self) -> None:
        """
        Đăng ký các thuật toán mặc định của hệ thống.
        Sau này muốn thêm Dijkstra, Prim, Kruskal thì thêm tại đây.
        """
        self.register_algorithm("bfs", bfs_algorithm())
        self.register_algorithm("dfs", dfs_algorithm())

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
        """
        Chạy thuật toán theo tên.

        Ví dụ:
            run_algorithm("bfs", graph, params)
            run_algorithm("dfs", graph, params)
        """
        algorithm = self.get_algorithm(name)

        if algorithm is None:
            return AlgorithmResult(
                algorithm_name=name,
                success=False,
                message=f"Thuật toán '{name}' chưa được hỗ trợ."
            )

        if not algorithm.can_run(graph):
            return AlgorithmResult(
                algorithm_name=algorithm.get_name(),
                success=False,
                message=f"Thuật toán {algorithm.get_name()} không thể chạy trên đồ thị hiện tại."
            )

        return algorithm.run(graph, params)