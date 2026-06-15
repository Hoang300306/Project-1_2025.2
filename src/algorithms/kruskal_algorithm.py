from typing import Dict, List, Tuple

from src.algorithms.base_algorithm import GraphAlgorithm
from src.model.graph import Graph
from src.model.edge import Edge
from src.result.algorithm_parameter import AlgorithmParameter
from src.result.algorithm_result import AlgorithmResult
from src.result.algorithm_step import AlgorithmStep


class DisjointSet:
    """
    Cấu trúc Union-Find dùng để kiểm tra chu trình trong Kruskal.

    Mỗi đỉnh ban đầu nằm trong một tập riêng.
    Nếu hai đỉnh thuộc hai tập khác nhau, ta có thể nối chúng lại.
    Nếu hai đỉnh đã cùng một tập, thêm cạnh giữa chúng sẽ tạo chu trình.
    """

    def __init__(self, vertices: List[int]):
        self.parent: Dict[int, int] = {}
        self.rank: Dict[int, int] = {}

        for vertex in vertices:
            self.parent[vertex] = vertex
            self.rank[vertex] = 0

    def find(self, vertex: int) -> int:
        """
        Tìm đại diện của tập chứa vertex.
        Có dùng path compression để tối ưu.
        """
        if self.parent[vertex] != vertex:
            self.parent[vertex] = self.find(self.parent[vertex])

        return self.parent[vertex]

    def union(self, u: int, v: int) -> bool:
        """
        Gộp hai tập chứa u và v.

        Returns:
            True nếu gộp thành công, tức là u và v trước đó khác tập.
            False nếu u và v đã cùng tập, tức thêm cạnh sẽ tạo chu trình.
        """
        root_u = self.find(u)
        root_v = self.find(v)

        if root_u == root_v:
            return False

        if self.rank[root_u] < self.rank[root_v]:
            self.parent[root_u] = root_v
        elif self.rank[root_u] > self.rank[root_v]:
            self.parent[root_v] = root_u
        else:
            self.parent[root_v] = root_u
            self.rank[root_u] += 1

        return True

    def get_parent_state(self) -> Dict[int, int]:
        """
        Trả về trạng thái parent hiện tại để lưu vào AlgorithmStep.
        """
        return self.parent.copy()


class KruskalAlgorithm(GraphAlgorithm):
    """
    Thuật toán Kruskal.

    Dùng để tìm cây khung nhỏ nhất - Minimum Spanning Tree.

    Điều kiện:
    - Đồ thị vô hướng
    - Có trọng số
    - Liên thông
    """

    def get_name(self) -> str:
        return "Kruskal"

    def get_description(self) -> str:
        return (
            "Kruskal là thuật toán tìm cây khung nhỏ nhất của đồ thị vô hướng, có trọng số, liên thông. "
            "Thuật toán sắp xếp các cạnh theo trọng số tăng dần, sau đó lần lượt chọn cạnh nhỏ nhất "
            "nếu cạnh đó không tạo chu trình. Để kiểm tra chu trình, thuật toán sử dụng Union-Find."
        )

    def can_run(self, graph: Graph) -> bool:
        return graph.number_of_vertices() > 0

    def run(self, graph: Graph, params: AlgorithmParameter) -> AlgorithmResult:
        vertices = [vertex.id for vertex in graph.get_vertices()]

        if not vertices:
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message="Kruskal cần đồ thị có ít nhất một đỉnh."
            )

        steps: List[AlgorithmStep] = []
        mst_edges: List[Tuple[int, int]] = []
        traversal_order: List[int] = []

        total_cost = 0.0
        step_number = 1

        # Lấy danh sách cạnh và sắp xếp theo trọng số tăng dần.
        sorted_edges = sorted(graph.get_edges(), key=lambda edge: edge.weight)

        disjoint_set = DisjointSet(vertices)

        steps.append(
            AlgorithmStep(
                step_number=step_number,
                description=(
                    "Khởi tạo Kruskal. Mỗi đỉnh ban đầu là một tập riêng. "
                    "Sắp xếp tất cả các cạnh theo trọng số tăng dần."
                ),
                visited_vertices=[],
                highlighted_vertices=[],
                highlighted_edges=[],
                parent=disjoint_set.get_parent_state()
            )
        )

        step_number += 1

        sorted_edges_text = self._format_edge_list(sorted_edges)

        steps.append(
            AlgorithmStep(
                step_number=step_number,
                description=f"Danh sách cạnh sau khi sắp xếp: {sorted_edges_text}",
                visited_vertices=[],
                highlighted_vertices=[],
                highlighted_edges=[],
                parent=disjoint_set.get_parent_state()
            )
        )

        step_number += 1

        for edge in sorted_edges:
            source = edge.source
            target = edge.target
            weight = edge.weight

            steps.append(
                AlgorithmStep(
                    step_number=step_number,
                    description=(
                        f"Xét cạnh {source} - {target} có trọng số {self._format_weight(weight)}."
                    ),
                    current_vertex=source,
                    visited_vertices=traversal_order.copy(),
                    highlighted_vertices=[source, target],
                    highlighted_edges=[(source, target)],
                    parent=disjoint_set.get_parent_state()
                )
            )

            step_number += 1

            root_source = disjoint_set.find(source)
            root_target = disjoint_set.find(target)

            if root_source != root_target:
                disjoint_set.union(source, target)

                mst_edges.append((source, target))
                total_cost += weight

                if source not in traversal_order:
                    traversal_order.append(source)

                if target not in traversal_order:
                    traversal_order.append(target)

                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=(
                            f"Chọn cạnh {source} - {target} vào cây khung vì hai đỉnh thuộc hai tập khác nhau. "
                            f"Tổng trọng số hiện tại = {self._format_weight(total_cost)}."
                        ),
                        current_vertex=target,
                        visited_vertices=traversal_order.copy(),
                        highlighted_vertices=[source, target],
                        highlighted_edges=mst_edges.copy(),
                        parent=disjoint_set.get_parent_state()
                    )
                )

                step_number += 1

                if len(mst_edges) == graph.number_of_vertices() - 1:
                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                "Đã chọn đủ n - 1 cạnh. Thuật toán Kruskal kết thúc."
                            ),
                            visited_vertices=traversal_order.copy(),
                            highlighted_vertices=[],
                            highlighted_edges=mst_edges.copy(),
                            parent=disjoint_set.get_parent_state()
                        )
                    )

                    step_number += 1
                    break

            else:
                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=(
                            f"Bỏ qua cạnh {source} - {target} vì hai đỉnh đã thuộc cùng một tập. "
                            f"Nếu thêm cạnh này sẽ tạo chu trình."
                        ),
                        current_vertex=target,
                        visited_vertices=traversal_order.copy(),
                        highlighted_vertices=[source, target],
                        highlighted_edges=[(source, target)],
                        parent=disjoint_set.get_parent_state()
                    )
                )

                step_number += 1

        if len(mst_edges) != graph.number_of_vertices() - 1:
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message="Không thể tạo cây khung nhỏ nhất vì đồ thị không liên thông.",
                traversal_order=traversal_order,
                result_edges=mst_edges,
                total_cost=total_cost,
                steps=steps
            )

        message = (
            f"Tìm được cây khung nhỏ nhất bằng Kruskal. "
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

    def _format_edge_list(self, edges: List[Edge]) -> str:
        parts = []

        for edge in edges:
            parts.append(
                f"({edge.source}-{edge.target}, w={self._format_weight(edge.weight)})"
            )

        return ", ".join(parts)