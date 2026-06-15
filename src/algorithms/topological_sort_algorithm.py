from collections import deque
from typing import Dict, List

from src.algorithms.base_algorithm import GraphAlgorithm
from src.model.graph import Graph
from src.result.algorithm_parameter import AlgorithmParameter
from src.result.algorithm_result import AlgorithmResult
from src.result.algorithm_step import AlgorithmStep


class TopologicalSortAlgorithm(GraphAlgorithm):
    """
    Thuật toán Topological Sort.

    Điều kiện:
    - Đồ thị phải có hướng.
    - Đồ thị không được có chu trình.

    Cách cài đặt:
    - Dùng thuật toán Kahn.
    - Tính in-degree của từng đỉnh.
    - Đưa các đỉnh có in-degree = 0 vào queue.
    - Mỗi lần lấy một đỉnh ra khỏi queue, thêm vào kết quả.
    - Giảm in-degree của các đỉnh kề.
    - Nếu in-degree của một đỉnh về 0 thì đưa vào queue.
    """

    def get_name(self) -> str:
        return "Topological Sort"

    def get_description(self) -> str:
        return (
            "Topological Sort là thuật toán sắp xếp các đỉnh của đồ thị có hướng không chu trình. "
            "Nếu có cạnh u -> v thì u sẽ đứng trước v trong thứ tự topo. "
            "Phiên bản này sử dụng thuật toán Kahn dựa trên bậc vào in-degree."
        )

    def can_run(self, graph: Graph) -> bool:
        return graph.number_of_vertices() > 0

    def run(self, graph: Graph, params: AlgorithmParameter) -> AlgorithmResult:
        vertices = sorted([vertex.id for vertex in graph.get_vertices()])

        in_degree: Dict[int, int] = {
            vertex_id: 0 for vertex_id in vertices
        }

        # Tính bậc vào cho từng đỉnh.
        for edge in graph.get_edges():
            in_degree[edge.target] += 1

        queue = deque()

        for vertex_id in vertices:
            if in_degree[vertex_id] == 0:
                queue.append(vertex_id)

        topo_order: List[int] = []
        steps: List[AlgorithmStep] = []

        step_number = 1

        steps.append(
            AlgorithmStep(
                step_number=step_number,
                description=(
                    "Khởi tạo Topological Sort. "
                    "Tính in-degree cho từng đỉnh và đưa các đỉnh có in-degree = 0 vào queue."
                ),
                visited_vertices=topo_order.copy(),
                highlighted_vertices=list(queue),
                queue_state=list(queue),
                distance=in_degree.copy()
            )
        )

        step_number += 1

        while queue:
            current = queue.popleft()
            topo_order.append(current)

            steps.append(
                AlgorithmStep(
                    step_number=step_number,
                    description=(
                        f"Lấy đỉnh {current} ra khỏi queue và thêm vào thứ tự topo."
                    ),
                    current_vertex=current,
                    visited_vertices=topo_order.copy(),
                    highlighted_vertices=[current],
                    queue_state=list(queue),
                    distance=in_degree.copy()
                )
            )

            step_number += 1

            for neighbor, _weight in graph.get_neighbors(current):
                old_degree = in_degree[neighbor]
                in_degree[neighbor] -= 1

                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=(
                            f"Xét cạnh {current} -> {neighbor}. "
                            f"Giảm in-degree[{neighbor}] từ {old_degree} xuống {in_degree[neighbor]}."
                        ),
                        current_vertex=current,
                        visited_vertices=topo_order.copy(),
                        highlighted_vertices=[current, neighbor],
                        highlighted_edges=[(current, neighbor)],
                        queue_state=list(queue),
                        distance=in_degree.copy()
                    )
                )

                step_number += 1

                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"in-degree[{neighbor}] = 0 nên đưa đỉnh {neighbor} vào queue."
                            ),
                            current_vertex=neighbor,
                            visited_vertices=topo_order.copy(),
                            highlighted_vertices=[neighbor],
                            queue_state=list(queue),
                            distance=in_degree.copy()
                        )
                    )

                    step_number += 1

        if len(topo_order) != graph.number_of_vertices():
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message=(
                    "Không thể sắp xếp topo vì đồ thị có chu trình. "
                    "Topological Sort chỉ áp dụng cho DAG."
                ),
                traversal_order=topo_order,
                steps=steps
            )

        return AlgorithmResult(
            algorithm_name=self.get_name(),
            success=True,
            message="Sắp xếp topo thành công.",
            traversal_order=topo_order,
            steps=steps
        )