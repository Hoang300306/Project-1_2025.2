import heapq
from typing import Dict, List, Optional, Set
from src.algorithms.base_algorithm import GraphAlgorithm
from src.model.graph import Graph
from src.result.algorithm_step import AlgorithmStep
from src.result.algorithm_result import AlgorithmResult
from src.result.algorithm_parameter import AlgorithmParameter

class DijkstraAlgorithm(GraphAlgorithm):
    def get_name(self) -> str:
        return "Dijkstra"
    def get_description(self) -> str:
        return (
            "Dijkstra là thuật toán tìm đường đi ngắn nhất từ một đỉnh nguồn đến tất cả các đỉnh khác trong đồ thị có trọng số không âm. "
            "Thuật toán sử dụng hàng đợi ưu tiên để luôn mở rộng đỉnh có khoảng cách nhỏ nhất trước."
        )
    def can_run(self, graph:Graph) -> bool:
        return graph.number_of_vertices() > 0
    def run(self, graph:Graph, params: AlgorithmParameter) -> AlgorithmResult:
        start = params.start_vertex
        target = params.target_vertex

        if start is None:
            return AlgorithmResult( algorithm_name = self.get_name(), success=False, message='Dijkstra cần đỉnh bắt đầu.' )
        
        if not graph.has_vertex(start):
            return AlgorithmResult( algorithm_name = self.get_name(), success=False, message=f"Đỉnh bắt đầu {start} không tồn tại trong đồ thị.")
        
        if target is not None and not graph.has_vertex(target):
            return AlgorithmResult( algorithm_name = self.get_name(), success=False, message=f'Dinh dich {target} khong ton tai trong do thi')
        
        if graph.has_negative_edge():
            return AlgorithmResult( algorithm_name = self.get_name(), success=False, message=f'Khong chay duoc Dijkstra vi canh co trong so am. Hay dung Bellman-Ford.' )
        
        infinity = float('inf')
        distance: Dict[int, float] = {vertex.id: infinity for vertex in graph.get_vertices()}
        parent: Dict[int, Optional[int]] = {vertex.id: None for vertex in graph.get_vertices()}
        visited: Set[int] = set()
        traversal_order: List[int] = []
        steps: list[AlgorithmStep] = []
        priority_queue: List[tuple[float, int]] = []
        distance[start] = 0
        heapq.heappush(priority_queue, (0, start))
        step_number = 1
        steps.append( AlgorithmStep(step_number=step_number,
                                    description=( f'Khoi tao Dijkstra tu dinh {start}.'
                                                 f'Dat distance{start}=0 va dua vao priority queue.'
                                                 ),
                                                 current_vertex=start, highlighted_vertices=[start], priority_queue_state=priority_queue.copy(), distance=distance.copy(), parent=parent.copy()))
        step_number += 1

        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)
            if current_vertex in visited:
                steps.append(
                    Algorithm(
                        step_number=step_number,
                        description=(f'Bo qua {current_vertex} vi da duoc xu li.'),
                        current_vertex=current_vertex,
                        visited_vertices=sorted[visited],
                        highlighted_vertices=[current_vertex],
                        priority_queue_state=priority_queue.copy(),
                        distance=distance.copy(),
                        parent=parent.copy()
                    )
                )
                step_number += 1
                continue
            
            if target is not None and current_vertex == target:
                steps.append(
                    AlgorithmStep(
                        step_number=step_number,
                        description=(
                            f"Đã chọn đến đỉnh đích {target}. "
                            f"Khoảng cách ngắn nhất đã được xác định."
                        ),
                        current_vertex=current_vertex,
                        visited_vertices=sorted(visited),
                        highlighted_vertices=[current_vertex],
                        priority_queue_state=priority_queue.copy(),
                        distance=distance.copy(),
                        parent=parent.copy()
                    )
                )
                step_number += 1
                break

            for neighbor, weight in graph.get_neighbors(current_vertex):
                if neighbor in visited:
                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"Bỏ qua cạnh {current_vertex} -> {neighbor} "
                                f"vì đỉnh {neighbor} đã được xử lý."
                            ),
                            current_vertex=current_vertex,
                            visited_vertices=sorted(visited),
                            highlighted_vertices=[current_vertex, neighbor],
                            highlighted_edges=[(current_vertex, neighbor)],
                            priority_queue_state=priority_queue.copy(),
                            distance=distance.copy(),
                            parent=parent.copy()
                        )
                    )
                    step_number += 1
                    continue

                new_distance = distance[current_vertex] + weight

                if new_distance < distance[neighbor]:
                    old_distance = distance[neighbor]

                    distance[neighbor] = new_distance
                    parent[neighbor] = current_vertex

                    heapq.heappush(priority_queue, (new_distance, neighbor))

                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"Cập nhật khoảng cách của đỉnh {neighbor}: "
                                f"{self._format_distance(old_distance)} -> "
                                f"{self._format_distance(new_distance)} "
                                f"thông qua đỉnh {current_vertex}."
                            ),
                            current_vertex=current_vertex,
                            visited_vertices=sorted(visited),
                            highlighted_vertices=[current_vertex, neighbor],
                            highlighted_edges=[(current_vertex, neighbor)],
                            priority_queue_state=priority_queue.copy(),
                            distance=distance.copy(),
                            parent=parent.copy()
                        )
                    )
                else:
                    steps.append(
                        AlgorithmStep(
                            step_number=step_number,
                            description=(
                                f"Không cập nhật đỉnh {neighbor} vì khoảng cách mới "
                                f"{self._format_distance(new_distance)} không nhỏ hơn "
                                f"khoảng cách hiện tại {self._format_distance(distance[neighbor])}."
                            ),
                            current_vertex=current_vertex,
                            visited_vertices=sorted(visited),
                            highlighted_vertices=[current_vertex, neighbor],
                            highlighted_edges=[(current_vertex, neighbor)],
                            priority_queue_state=priority_queue.copy(),
                            distance=distance.copy(),
                            parent=parent.copy()
                        )
                    )

                step_number += 1

        path = []
        result_edges = []

        if target is not None:
            if distance[target] != infinity:
                path = self._reconstruct_path(parent, start, target)

                for i in range(len(path) - 1):
                    result_edges.append((path[i], path[i + 1]))

                message = (
                    f"Tìm thấy đường đi ngắn nhất từ {start} đến {target}. "
                    f"Chi phí = {self._format_distance(distance[target])}."
                )
            else:
                message = f"Không tồn tại đường đi từ {start} đến {target}."
        else:
            message = f"Đã tìm khoảng cách ngắn nhất từ {start} đến các đỉnh còn lại."

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
        path = []
        current = target

        while current is not None:
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