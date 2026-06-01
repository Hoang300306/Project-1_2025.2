from typing import Dict, List, Optional

from src.algorithms.base_algorithm import GraphAlgorithm
from src.model.graph import Graph
from src.result.algorithm_parameter import AlgorithmParameter
from src.result.algorithm_result import AlgorithmResult
from src.result.algorithm_step import AlgorithmStep


class dfs_algorithm(GraphAlgorithm):

    def get_name(self) -> str:
        return "DFS"

    def get_description(self) -> str:
        return (
            "Depth First Search duyệt đồ thị theo chiều sâu. "
            "Thuật toán sử dụng ngăn xếp để ưu tiên đi sâu vào một nhánh "
            "trước khi quay lại duyệt các nhánh khác."
        )

    def can_run(self, graph: Graph) -> bool:
        """
        DFS có thể chạy trên:
        - đồ thị có hướng
        - đồ thị vô hướng
        - đồ thị có trọng số
        - đồ thị không trọng số
        """
        return graph.number_of_vertices() > 0

    def run(self, graph: Graph, params: AlgorithmParameter) -> AlgorithmResult:
        start = params.start_vertex
        target = params.target_vertex

        if start is None:
            return AlgorithmResult(
                algorithm_name=self.get_name(),
                success=False,
                message="DFS cần đỉnh bắt đầu."
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

        visited = set()
        stack: List[int] = []

        parent: Dict[int, Optional[int]] = {}
        distance: Dict[int, float] = {}

        traversal_order: List[int] = []
        steps: List[AlgorithmStep] = []

        step_number = 1

        stack.append(start)
        visited.add(start)
        parent[start] = None
        distance[start] = 0

        steps.append(
            AlgorithmStep(
                step_number=step_number,
                description=f"Bắt đầu DFS từ đỉnh {start}. Đưa {start} vào ngăn xếp.",
                current_vertex=start,
                visited_vertices=sorted(visited),
                highlighted_vertices=[start],
                stack_state=stack.copy(),
                distance=distance.copy(),
                parent=parent.copy()
            )
        )

        step_number += 1

        while stack:
            current = stack.pop()
            traversal_order.append(current)

            steps.append(
                AlgorithmStep(
                    step_number=step_number,
                    description=f"Lấy đỉnh {current} ra khỏi ngăn xếp để xử lý.",
                    current_vertex=current,
                    visited_vertices=sorted(visited),
                    highlighted_vertices=[current],
                    stack_state=stack.copy(),
                    distance=distance.copy(),
                    parent=parent.copy()
                )
            )

            step_number += 1

            if target is not None and current == target:
                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=f"Đã gặp đỉnh đích {target}. Dừng DFS.",
                        current_vertex=current,
                        visited_vertices=sorted(visited),
                        highlighted_vertices=[current],
                        stack_state=stack.copy(),
                        distance=distance.copy(),
                        parent=parent.copy()
                    )
                )
                break

            neighbors = graph.get_neighbors(current)

            # Vì stack là LIFO, ta duyệt ngược danh sách kề
            # để đỉnh xuất hiện trước trong danh sách kề được xử lý trước.
            for neighbor, _weight in reversed(neighbors):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

                    parent[neighbor] = current
                    distance[neighbor] = distance[current] + 1

                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"Phát hiện đỉnh {neighbor} từ đỉnh {current}. "
                                f"Đánh dấu {neighbor} đã thăm và đưa vào ngăn xếp."
                            ),
                            current_vertex=current,
                            visited_vertices=sorted(visited),
                            highlighted_vertices=[current, neighbor],
                            highlighted_edges=[(current, neighbor)],
                            stack_state=stack.copy(),
                            distance=distance.copy(),
                            parent=parent.copy()
                        )
                    )

                    step_number += 1

        path = []
        result_edges = []

        if target is not None:
            path = self._reconstruct_path(parent, start, target)

            if path:
                for i in range(len(path) - 1):
                    result_edges.append((path[i], path[i + 1]))

                message = f"Tìm thấy đường đi từ {start} đến {target}."
            else:
                message = f"Không tồn tại đường đi từ {start} đến {target}."
        else:
            message = f"Duyệt DFS từ đỉnh {start} hoàn tất."

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

    def _reconstruct_path(
        self,
        parent: Dict[int, Optional[int]],
        start: int,
        target: int
    ) -> List[int]:
        """
        Truy vết đường đi từ start đến target dựa vào parent.
        """
        if target not in parent:
            return []

        path = []
        current = target

        while current is not None:
            path.append(current)
            current = parent.get(current)

        path.reverse()

        if path and path[0] == start:
            return path

        return []