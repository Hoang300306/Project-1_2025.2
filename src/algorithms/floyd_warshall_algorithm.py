from typing import Dict, List, Optional, Tuple

from src.algorithms.base_algorithm import GraphAlgorithm
from src.model.graph import Graph
from src.result.algorithm_parameter import AlgorithmParameter
from src.result.algorithm_result import AlgorithmResult
from src.result.algorithm_step import AlgorithmStep


class FloydWarshallAlgorithm(GraphAlgorithm):
    """
    Thuật toán Floyd-Warshall.

    Dùng để tìm đường đi ngắn nhất giữa mọi cặp đỉnh.

    Đặc điểm:
    - Chạy được với cạnh âm.
    - Phát hiện được chu trình âm.
    - Độ phức tạp O(V^3).
    """

    def get_name(self) -> str:
        return "Floyd-Warshall"

    def get_description(self) -> str:
        return (
            "Floyd-Warshall là thuật toán tìm đường đi ngắn nhất giữa mọi cặp đỉnh. "
            "Thuật toán sử dụng quy hoạch động, lần lượt cho phép từng đỉnh làm đỉnh trung gian "
            "để cải thiện khoảng cách giữa các cặp đỉnh."
        )

    def can_run(self, graph: Graph) -> bool:
        return graph.number_of_vertices() > 0

    def run(self, graph: Graph, params: AlgorithmParameter) -> AlgorithmResult:
        source = params.start_vertex
        target = params.target_vertex

        if source is not None and not graph.has_vertex(source):
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message=f"Đỉnh nguồn {source} không tồn tại trong đồ thị."
            )

        if target is not None and not graph.has_vertex(target):
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message=f"Đỉnh đích {target} không tồn tại trong đồ thị."
            )

        if (source is None and target is not None) or (source is not None and target is None):
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message="Nếu muốn xem đường đi cụ thể, cần nhập cả đỉnh nguồn và đỉnh đích."
            )

        vertices = sorted([vertex.id for vertex in graph.get_vertices()])
        infinity = float("inf")

        distance: Dict[int, Dict[int, float]] = {}
        next_node: Dict[int, Dict[int, Optional[int]]] = {}

        for i in vertices:
            distance[i] = {}
            next_node[i] = {}

            for j in vertices:
                if i == j:
                    distance[i][j] = 0
                else:
                    distance[i][j] = infinity

                next_node[i][j] = None

        # Khởi tạo ma trận từ danh sách cạnh.
        for edge in graph.get_edges():
            u = edge.source
            v = edge.target
            w = edge.weight

            if w < distance[u][v]:
                distance[u][v] = w
                next_node[u][v] = v

            if not graph.directed:
                if w < distance[v][u]:
                    distance[v][u] = w
                    next_node[v][u] = u

        steps: List[AlgorithmStep] = []
        step_number = 1

        steps.append(
            AlgorithmStep(
                step_number=step_number,
                description=(
                    "Khởi tạo ma trận khoảng cách. "
                    "distance[i][i] = 0, distance[u][v] = trọng số cạnh, "
                    "các cặp không có cạnh trực tiếp = ∞."
                ),
                distance_matrix=self._copy_matrix(distance),
                next_matrix=self._copy_next_matrix(next_node)
            )
        )

        step_number += 1

        # Floyd-Warshall chính.
        for k in vertices:
            steps.append(
                AlgorithmStep(
                    step_number=step_number,
                    description=f"Chọn đỉnh trung gian k = {k}.",
                    current_vertex=k,
                    highlighted_vertices=[k],
                    distance_matrix=self._copy_matrix(distance),
                    next_matrix=self._copy_next_matrix(next_node)
                )
            )

            step_number += 1

            for i in vertices:
                for j in vertices:
                    if distance[i][k] == infinity or distance[k][j] == infinity:
                        continue

                    new_distance = distance[i][k] + distance[k][j]

                    if new_distance < distance[i][j]:
                        old_distance = distance[i][j]

                        distance[i][j] = new_distance
                        next_node[i][j] = next_node[i][k]

                        steps.append(
                            AlgorithmStep(
                                step_number=step_number,
                                description=(
                                    f"Cập nhật distance[{i}][{j}] qua đỉnh trung gian {k}: "
                                    f"{self._format_distance(old_distance)} -> "
                                    f"{self._format_distance(new_distance)}."
                                ),
                                current_vertex=k,
                                highlighted_vertices=[i, k, j],
                                highlighted_edges=[(i, k), (k, j)],
                                distance_matrix=self._copy_matrix(distance),
                                next_matrix=self._copy_next_matrix(next_node),
                                extra_data={
                                    "i": i,
                                    "j": j,
                                    "k": k,
                                    "old_distance": self._format_distance(old_distance),
                                    "new_distance": self._format_distance(new_distance)
                                }
                            )
                        )

                        step_number += 1

        # Kiểm tra chu trình âm.
        for v in vertices:
            if distance[v][v] < 0:
                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=(
                            f"Phát hiện chu trình âm vì distance[{v}][{v}] < 0."
                        ),
                        current_vertex=v,
                        highlighted_vertices=[v],
                        distance_matrix=self._copy_matrix(distance),
                        next_matrix=self._copy_next_matrix(next_node)
                    )
                )

                return AlgorithmResult(
                    algorithm_name=self.get_name(),
                    success=False,
                    message=(
                        "Đồ thị có chu trình âm. "
                        "Không tồn tại đường đi ngắn nhất xác định giữa một số cặp đỉnh."
                    ),
                    distance_matrix=distance,
                    next_matrix=next_node,
                    steps=steps
                )

        path = []
        result_edges = []

        if source is not None and target is not None:
            path = self._reconstruct_path(next_node, source, target)

            if not path:
                message = f"Không tồn tại đường đi từ {source} đến {target}."
            else:
                for index in range(len(path) - 1):
                    result_edges.append((path[index], path[index + 1]))

                message = (
                    f"Tìm thấy đường đi ngắn nhất từ {source} đến {target}. "
                    f"Chi phí = {self._format_distance(distance[source][target])}."
                )
        else:
            message = "Đã tìm đường đi ngắn nhất giữa mọi cặp đỉnh bằng Floyd-Warshall."

        return AlgorithmResult(
            algorithm_name=self.get_name(),
            success=True,
            message=message,
            path=path,
            result_edges=result_edges,
            distance_matrix=distance,
            next_matrix=next_node,
            steps=steps
        )

    def _reconstruct_path(
        self,
        next_node: Dict[int, Dict[int, Optional[int]]],
        source: int,
        target: int
    ) -> List[int]:
        """
        Truy vết đường đi từ source đến target dựa trên next_node.
        """

        if next_node[source][target] is None:
            return []

        path = [source]
        current = source
        seen = set()

        while current != target:
            if current in seen:
                return []

            seen.add(current)
            current = next_node[current][target]

            if current is None:
                return []

            path.append(current)

        return path

    def _copy_matrix(
        self,
        matrix: Dict[int, Dict[int, float]]
    ) -> Dict[int, Dict[int, float]]:
        return {
            i: row.copy()
            for i, row in matrix.items()
        }

    def _copy_next_matrix(
        self,
        matrix: Dict[int, Dict[int, Optional[int]]]
    ) -> Dict[int, Dict[int, Optional[int]]]:
        return {
            i: row.copy()
            for i, row in matrix.items()
        }

    def _format_distance(self, value: float) -> str:
        if value == float("inf"):
            return "∞"

        if float(value).is_integer():
            return str(int(value))

        return str(value)