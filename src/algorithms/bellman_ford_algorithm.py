from typing import Dict, List, Optional, Tuple

from src.algorithms.base_algorithm import GraphAlgorithm
from src.model.graph import Graph
from src.result.algorithm_parameter import AlgorithmParameter
from src.result.algorithm_result import AlgorithmResult
from src.result.algorithm_step import AlgorithmStep


class BellmanFordAlgorithm(GraphAlgorithm):
    """
    Thuật toán Bellman-Ford.

    Dùng để tìm đường đi ngắn nhất từ một đỉnh nguồn đến các đỉnh còn lại.

    Ưu điểm:
    - Chạy được với cạnh trọng số âm.
    - Phát hiện được chu trình âm.

    Nhược điểm:
    - Chậm hơn Dijkstra.
    - Độ phức tạp O(V * E).
    """

    def get_name(self) -> str:
        return "Bellman-Ford"

    def get_description(self) -> str:
        return (
            "Bellman-Ford là thuật toán tìm đường đi ngắn nhất từ một đỉnh nguồn "
            "đến các đỉnh còn lại. Khác với Dijkstra, Bellman-Ford có thể xử lý "
            "cạnh có trọng số âm và có khả năng phát hiện chu trình âm."
        )

    def can_run(self, graph: Graph) -> bool:
        return graph.number_of_vertices() > 0

    def run(self, graph: Graph, params: AlgorithmParameter) -> AlgorithmResult:
        start = params.start_vertex
        target = params.target_vertex

        if start is None:
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message="Bellman-Ford cần đỉnh bắt đầu."
            )

        if not graph.has_vertex(start):
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message=f"Đỉnh bắt đầu {start} không tồn tại trong đồ thị."
            )

        if target is not None and not graph.has_vertex(target):
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message=f"Đỉnh đích {target} không tồn tại trong đồ thị."
            )

        infinity = float("inf")

        vertices = [vertex.id for vertex in graph.get_vertices()]
        relaxation_edges = self._get_relaxation_edges(graph)

        distance: Dict[int, float] = {
            vertex_id: infinity for vertex_id in vertices
        }

        parent: Dict[int, Optional[int]] = {
            vertex_id: None for vertex_id in vertices
        }

        distance[start] = 0

        steps: List[AlgorithmStep] = []
        traversal_order: List[int] = []

        step_number = 1

        steps.append(
            AlgorithmStep(
                step_number=step_number,
                description=(
                    f"Khởi tạo Bellman-Ford từ đỉnh {start}. "
                    f"Đặt distance[{start}] = 0, các đỉnh còn lại = ∞."
                ),
                current_vertex=start,
                highlighted_vertices=[start],
                distance=distance.copy(),
                parent=parent.copy()
            )
        )

        step_number += 1

        number_of_vertices = graph.number_of_vertices()

        for iteration in range(1, number_of_vertices):
            updated = False

            steps.append(
                AlgorithmStep(
                    step_number=step_number,
                    description=(
                        f"Bắt đầu vòng lặp thứ {iteration}. "
                        f"Thử relax tất cả các cạnh."
                    ),
                    distance=distance.copy(),
                    parent=parent.copy()
                )
            )

            step_number += 1

            for source, target_vertex, weight in relaxation_edges:
                if distance[source] == infinity:
                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"Bỏ qua cạnh {source} -> {target_vertex} vì "
                                f"distance[{source}] hiện là ∞."
                            ),
                            current_vertex=source,
                            highlighted_vertices=[source, target_vertex],
                            highlighted_edges=[(source, target_vertex)],
                            distance=distance.copy(),
                            parent=parent.copy()
                        )
                    )

                    step_number += 1
                    continue

                new_distance = distance[source] + weight

                if new_distance < distance[target_vertex]:
                    old_distance = distance[target_vertex]

                    distance[target_vertex] = new_distance
                    parent[target_vertex] = source
                    updated = True

                    if target_vertex not in traversal_order:
                        traversal_order.append(target_vertex)

                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"Relax cạnh {source} -> {target_vertex}: "
                                f"distance[{target_vertex}] được cập nhật từ "
                                f"{self._format_distance(old_distance)} thành "
                                f"{self._format_distance(new_distance)}."
                            ),
                            current_vertex=source,
                            visited_vertices=traversal_order.copy(),
                            highlighted_vertices=[source, target_vertex],
                            highlighted_edges=[(source, target_vertex)],
                            distance=distance.copy(),
                            parent=parent.copy()
                        )
                    )
                else:
                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"Không cập nhật cạnh {source} -> {target_vertex} vì "
                                f"khoảng cách mới {self._format_distance(new_distance)} "
                                f"không nhỏ hơn khoảng cách hiện tại "
                                f"{self._format_distance(distance[target_vertex])}."
                            ),
                            current_vertex=source,
                            visited_vertices=traversal_order.copy(),
                            highlighted_vertices=[source, target_vertex],
                            highlighted_edges=[(source, target_vertex)],
                            distance=distance.copy(),
                            parent=parent.copy()
                        )
                    )

                step_number += 1

            if not updated:
                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=(
                            f"Không có cập nhật nào ở vòng lặp thứ {iteration}. "
                            f"Thuật toán có thể dừng sớm."
                        ),
                        distance=distance.copy(),
                        parent=parent.copy()
                    )
                )

                step_number += 1
                break

        # Kiểm tra chu trình âm
        for source, target_vertex, weight in relaxation_edges:
            if distance[source] != infinity and distance[source] + weight < distance[target_vertex]:
                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=(
                            f"Phát hiện chu trình âm qua cạnh {source} -> {target_vertex}. "
                            f"Vẫn còn có thể relax sau V-1 vòng lặp."
                        ),
                        current_vertex=source,
                        highlighted_vertices=[source, target_vertex],
                        highlighted_edges=[(source, target_vertex)],
                        distance=distance.copy(),
                        parent=parent.copy()
                    )
                )

                return AlgorithmResult(
                    algorithm_name=self.get_name(),
                    success=False,
                    message=(
                        "Đồ thị có chu trình âm có thể đi tới từ đỉnh bắt đầu. "
                        "Không tồn tại đường đi ngắn nhất xác định."
                    ),
                    traversal_order=traversal_order,
                    distance=distance,
                    parent=parent,
                    steps=steps
                )

        path = []
        result_edges = []

        if target is not None:
            if distance[target] == infinity:
                message = f"Không tồn tại đường đi từ {start} đến {target}."
            else:
                path = self._reconstruct_path(parent, start, target)

                for i in range(len(path) - 1):
                    result_edges.append((path[i], path[i + 1]))

                message = (
                    f"Tìm thấy đường đi ngắn nhất từ {start} đến {target}. "
                    f"Chi phí = {self._format_distance(distance[target])}."
                )
        else:
            message = (
                f"Đã tìm khoảng cách ngắn nhất từ {start} đến các đỉnh còn lại "
                f"bằng Bellman-Ford."
            )

        return AlgorithmResult(
            algorithm_name=self.get_name(),
            success=True,
            message=message,
            traversal_order=traversal_order,
            path=path,
            result_edges=result_edges,
            distance=distance,
            parent=parent,
            steps=steps
        )

    def _get_relaxation_edges(self, graph: Graph) -> List[Tuple[int, int, float]]:
        """
        Tạo danh sách cạnh dùng để relax.

        Nếu đồ thị có hướng:
            dùng cạnh u -> v.

        Nếu đồ thị vô hướng:
            thêm cả hai chiều u -> v và v -> u.
        """

        result = []

        for edge in graph.get_edges():
            result.append((edge.source, edge.target, edge.weight))

            if not graph.directed:
                result.append((edge.target, edge.source, edge.weight))

        return result

    def _reconstruct_path(
        self,
        parent: Dict[int, Optional[int]],
        start: int,
        target: int
    ) -> List[int]:
        path = []
        current = target
        seen = set()

        while current is not None:
            if current in seen:
                return []

            seen.add(current)
            path.append(current)
            current = parent.get(current)

        path.reverse()

        if path and path[0] == start:
            return path

        return []

    def _format_distance(self, value: float) -> str:
        if value == float("inf"):
            return "∞"

        if float(value).is_integer():
            return str(int(value))

        return str(value)