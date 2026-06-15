import heapq
from typing import List, Set, Tuple

from src.algorithms.base_algorithm import GraphAlgorithm
from src.model.graph import Graph
from src.result.algorithm_parameter import AlgorithmParameter
from src.result.algorithm_result import AlgorithmResult
from src.result.algorithm_step import AlgorithmStep


class PrimAlgorithm(GraphAlgorithm):
    """
    Thuật toán Prim.

    Dùng để tìm cây khung nhỏ nhất - Minimum Spanning Tree.

    Điều kiện:
    - Đồ thị vô hướng
    - Có trọng số
    - Liên thông
    """

    def get_name(self) -> str:
        return "Prim"

    def get_description(self) -> str:
        return (
            "Prim là thuật toán tìm cây khung nhỏ nhất của đồ thị vô hướng, có trọng số, liên thông. "
            "Thuật toán bắt đầu từ một đỉnh, sau đó liên tục chọn cạnh có trọng số nhỏ nhất "
            "nối từ tập đỉnh đã chọn sang một đỉnh chưa được chọn."
        )

    def can_run(self, graph: Graph) -> bool:
        return graph.number_of_vertices() > 0

    def run(self, graph: Graph, params: AlgorithmParameter) -> AlgorithmResult:
        start = params.start_vertex

        if start is None:
            vertices = graph.get_vertices()
            if not vertices:
                return AlgorithmResult(
                    algorithm_name=self.get_name(),
                    success=False,
                    message="Prim cần đồ thị có ít nhất một đỉnh."
                )
            start = vertices[0].id

        if not graph.has_vertex(start):
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message=f"Đỉnh bắt đầu {start} không tồn tại trong đồ thị."
            )

        visited: Set[int] = set()
        mst_edges: List[Tuple[int, int]] = []
        traversal_order: List[int] = []
        steps: List[AlgorithmStep] = []

        total_cost = 0.0
        priority_queue: List[Tuple[float, int, int]] = []

        step_number = 1

        visited.add(start)
        traversal_order.append(start)

        steps.append(
            AlgorithmStep(
                step_number=step_number,
                description=f"Bắt đầu Prim từ đỉnh {start}. Đưa {start} vào cây khung.",
                current_vertex=start,
                visited_vertices=sorted(visited),
                highlighted_vertices=[start],
                priority_queue_state=priority_queue.copy()
            )
        )

        step_number += 1

        # Đưa toàn bộ cạnh đi ra từ start vào priority queue.
        for neighbor, weight in graph.get_neighbors(start):
            heapq.heappush(priority_queue, (weight, start, neighbor))

            steps.append(
                AlgorithmStep(
                    step_number=step_number,
                    description=(
                        f"Đưa cạnh {start} - {neighbor} có trọng số {self._format_weight(weight)} "
                        f"vào priority queue."
                    ),
                    current_vertex=start,
                    visited_vertices=sorted(visited),
                    highlighted_vertices=[start, neighbor],
                    highlighted_edges=[(start, neighbor)],
                    priority_queue_state=priority_queue.copy()
                )
            )

            step_number += 1

        while priority_queue and len(visited) < graph.number_of_vertices():
            weight, source, target = heapq.heappop(priority_queue)

            steps.append(
                AlgorithmStep(
                    step_number=step_number,
                    description=(
                        f"Lấy cạnh nhỏ nhất hiện tại khỏi priority queue: "
                        f"{source} - {target}, trọng số = {self._format_weight(weight)}."
                    ),
                    current_vertex=target,
                    visited_vertices=sorted(visited),
                    highlighted_vertices=[source, target],
                    highlighted_edges=[(source, target)],
                    priority_queue_state=priority_queue.copy()
                )
            )

            step_number += 1

            if target in visited:
                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=(
                            f"Bỏ qua cạnh {source} - {target} vì đỉnh {target} đã nằm trong cây khung."
                        ),
                        current_vertex=target,
                        visited_vertices=sorted(visited),
                        highlighted_vertices=[source, target],
                        highlighted_edges=[(source, target)],
                        priority_queue_state=priority_queue.copy()
                    )
                )

                step_number += 1
                continue

            # Chọn cạnh vào MST.
            visited.add(target)
            mst_edges.append((source, target))
            traversal_order.append(target)
            total_cost += weight

            steps.append(
                AlgorithmStep(
                    step_number=step_number,
                    description=(
                        f"Chọn cạnh {source} - {target} vào cây khung. "
                        f"Tổng trọng số hiện tại = {self._format_weight(total_cost)}."
                    ),
                    current_vertex=target,
                    visited_vertices=sorted(visited),
                    highlighted_vertices=[source, target],
                    highlighted_edges=mst_edges.copy(),
                    priority_queue_state=priority_queue.copy()
                )
            )

            step_number += 1

            # Thêm các cạnh mới đi ra từ target.
            for neighbor, edge_weight in graph.get_neighbors(target):
                if neighbor not in visited:
                    heapq.heappush(priority_queue, (edge_weight, target, neighbor))

                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"Đưa cạnh {target} - {neighbor} có trọng số "
                                f"{self._format_weight(edge_weight)} vào priority queue."
                            ),
                            current_vertex=target,
                            visited_vertices=sorted(visited),
                            highlighted_vertices=[target, neighbor],
                            highlighted_edges=[(target, neighbor)],
                            priority_queue_state=priority_queue.copy()
                        )
                    )

                    step_number += 1

        if len(visited) != graph.number_of_vertices():
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message=(
                    "Không thể tạo cây khung nhỏ nhất vì đồ thị không liên thông."
                ),
                traversal_order=traversal_order,
                result_edges=mst_edges,
                total_cost=total_cost,
                steps=steps
            )

        message = (
            f"Tìm được cây khung nhỏ nhất bằng Prim. "
            f"Tổng trọng số = {self._format_weight(total_cost)}."
        )

        return AlgorithmResult(
            algorithm_name=self.get_name(),
            success=True,
            message=message,
            traversal_order=traversal_order,
            result_edges=mst_edges,
            total_cost=total_cost,
            steps=steps
        )

    def _format_weight(self, value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return str(value)