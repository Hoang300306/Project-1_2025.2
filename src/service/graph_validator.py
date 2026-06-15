from collections import deque
from dataclasses import dataclass, field
from typing import List, Set

from src.model.graph import Graph


@dataclass
class ValidationResult:
    """
    Kết quả kiểm tra đồ thị hoặc kiểm tra điều kiện thuật toán.
    """

    valid: bool
    message: str = "Đồ thị hợp lệ."
    warnings: List[str] = field(default_factory=list)


class GraphValidator:
    """
    Class dùng để kiểm tra tính hợp lệ của đồ thị
    và điều kiện áp dụng của từng thuật toán.
    """

    @staticmethod
    def validate_graph(graph: Graph) -> ValidationResult:
        """
        Kiểm tra đồ thị cơ bản:
        - Graph không được None
        - Phải có ít nhất một đỉnh
        - Mỗi cạnh phải nối giữa hai đỉnh tồn tại
        """

        if graph is None:
            return ValidationResult(
                valid=False,
                message="Đồ thị chưa được khởi tạo."
            )

        if graph.number_of_vertices() == 0:
            return ValidationResult(
                valid=False,
                message="Đồ thị không có đỉnh nào."
            )

        for edge in graph.get_edges():
            if not graph.has_vertex(edge.source):
                return ValidationResult(
                    valid=False,
                    message=f"Cạnh {edge.source} -> {edge.target} không hợp lệ vì đỉnh {edge.source} không tồn tại."
                )

            if not graph.has_vertex(edge.target):
                return ValidationResult(
                    valid=False,
                    message=f"Cạnh {edge.source} -> {edge.target} không hợp lệ vì đỉnh {edge.target} không tồn tại."
                )

        return ValidationResult(
            valid=True,
            message="Đồ thị hợp lệ."
        )

    @staticmethod
    def validate_for_algorithm(algorithm_name: str, graph: Graph) -> ValidationResult:
        """
        Kiểm tra điều kiện chạy của từng thuật toán.

        Các thuật toán hiện tại:
        - BFS
        - DFS
        - Dijkstra

        Các thuật toán chuẩn bị mở rộng:
        - Prim
        - Kruskal
        - Topological Sort
        """

        base_validation = GraphValidator.validate_graph(graph)

        if not base_validation.valid:
            return base_validation

        key = algorithm_name.lower().strip()

        if key == "bfs":
            return GraphValidator._validate_bfs(graph)

        if key == "dfs":
            return GraphValidator._validate_dfs(graph)

        if key == "dijkstra":
            return GraphValidator._validate_dijkstra(graph)
        if key in ["bellman_ford", "bellman-ford", "bellmanford"]:
            return GraphValidator._validate_bellman_ford(graph)

        if key == "prim":
            return GraphValidator._validate_prim(graph)

        if key == "kruskal":
            return GraphValidator._validate_kruskal(graph)
        
        if key in ["floyd_warshall", "floyd-warshall", "floyd"]:
            return GraphValidator._validate_floyd_warshall(graph)

        if key in ["topological_sort", "topological", "topo", "toposort"]:
            return GraphValidator._validate_topological_sort(graph)

        return ValidationResult(
            valid=False,
            message=f"Chưa có bộ kiểm tra cho thuật toán '{algorithm_name}'."
        )

    @staticmethod
    def _validate_bfs(graph: Graph) -> ValidationResult:
        warnings = []

        if graph.weighted:
            warnings.append(
                "BFS có thể chạy trên đồ thị có trọng số, nhưng chỉ tìm đường đi ngắn nhất theo số cạnh, không xét tổng trọng số."
            )

        return ValidationResult(
            valid=True,
            message="Có thể chạy BFS trên đồ thị hiện tại.",
            warnings=warnings
        )

    @staticmethod
    def _validate_dfs(graph: Graph) -> ValidationResult:
        return ValidationResult(
            valid=True,
            message="Có thể chạy DFS trên đồ thị hiện tại."
        )

    @staticmethod
    def _validate_dijkstra(graph: Graph) -> ValidationResult:
        if graph.has_negative_edge():
            return ValidationResult(
                valid=False,
                message=(
                    "Không thể chạy Dijkstra vì đồ thị có cạnh trọng số âm. "
                    "Hãy dùng Bellman-Ford cho trường hợp này."
                )
            )

        warnings = []

        if not graph.weighted:
            warnings.append(
                "Đồ thị không có trọng số, Dijkstra vẫn chạy được nhưng kết quả tương tự BFS về số cạnh."
            )

        return ValidationResult(
            valid=True,
            message="Có thể chạy Dijkstra trên đồ thị hiện tại.",
            warnings=warnings
        )

    @staticmethod
    def _validate_bellman_ford(graph: Graph) -> ValidationResult:
        warnings = []

        if not graph.weighted:
            warnings.append(
                "Đồ thị không có trọng số, Bellman-Ford vẫn chạy được nhưng thường không cần thiết. Có thể dùng BFS nếu chỉ cần đường đi theo số cạnh."
            )

        if not graph.has_negative_edge():
            warnings.append(
                "Đồ thị không có cạnh âm. Dijkstra thường nhanh hơn Bellman-Ford trong trường hợp này."
            )

        return ValidationResult(
            valid=True,
            message="Có thể chạy Bellman-Ford trên đồ thị hiện tại.",
            warnings=warnings
        )

    @staticmethod
    def _validate_prim(graph: Graph) -> ValidationResult:
        """
        Dùng cho bước sau khi cài Prim.
        Điều kiện Prim:
        - Đồ thị vô hướng
        - Có trọng số
        - Nên liên thông để tìm được cây khung nhỏ nhất toàn đồ thị
        """

        if graph.directed:
            return ValidationResult(
                valid=False,
                message="Prim chỉ áp dụng cho đồ thị vô hướng."
            )

        if not graph.weighted:
            return ValidationResult(
                valid=False,
                message="Prim cần đồ thị có trọng số."
            )

        if not GraphValidator.is_connected_undirected(graph):
            return ValidationResult(
                valid=False,
                message="Prim cần đồ thị vô hướng liên thông để tìm cây khung nhỏ nhất."
            )

        return ValidationResult(
            valid=True,
            message="Có thể chạy Prim trên đồ thị hiện tại."
        )

    @staticmethod
    def _validate_kruskal(graph: Graph) -> ValidationResult:
        """
        Dùng cho bước sau khi cài Kruskal.
        Điều kiện Kruskal:
        - Đồ thị vô hướng
        - Có trọng số
        - Nên liên thông để có cây khung nhỏ nhất
        """

        if graph.directed:
            return ValidationResult(
                valid=False,
                message="Kruskal chỉ áp dụng cho đồ thị vô hướng."
            )

        if not graph.weighted:
            return ValidationResult(
                valid=False,
                message="Kruskal cần đồ thị có trọng số."
            )

        if not GraphValidator.is_connected_undirected(graph):
            return ValidationResult(
                valid=False,
                message="Kruskal cần đồ thị vô hướng liên thông để tìm cây khung nhỏ nhất."
            )

        return ValidationResult(
            valid=True,
            message="Có thể chạy Kruskal trên đồ thị hiện tại."
        )

    @staticmethod
    def _validate_floyd_warshall(graph: Graph) -> ValidationResult:
        warnings = []

        if graph.number_of_vertices() > 100:
            warnings.append(
                "Floyd-Warshall có độ phức tạp O(V^3), nên có thể chậm với đồ thị nhiều đỉnh."
            )

        if not graph.weighted:
            warnings.append(
                "Đồ thị không có trọng số, Floyd-Warshall vẫn chạy được nhưng thường không cần thiết."
            )

        return ValidationResult(
            valid=True,
            message="Có thể chạy Floyd-Warshall trên đồ thị hiện tại.",
            warnings=warnings
        )

    @staticmethod
    def _validate_topological_sort(graph: Graph) -> ValidationResult:
        """
        Dùng cho bước sau khi cài Topological Sort.
        Điều kiện:
        - Đồ thị có hướng
        - Không có chu trình
        """

        if not graph.directed:
            return ValidationResult(
                valid=False,
                message="Topological Sort chỉ áp dụng cho đồ thị có hướng."
            )

        if not GraphValidator.is_dag(graph):
            return ValidationResult(
                valid=False,
                message="Topological Sort chỉ áp dụng cho đồ thị có hướng không chu trình."
            )

        return ValidationResult(
            valid=True,
            message="Có thể chạy Topological Sort trên đồ thị hiện tại."
        )

    @staticmethod
    def is_connected_undirected(graph: Graph) -> bool:
        """
        Kiểm tra đồ thị vô hướng có liên thông không.

        Lưu ý:
        - Hàm này dùng cho đồ thị vô hướng.
        - Nếu đồ thị có hướng, hàm trả về False.
        """

        if graph.directed:
            return False

        vertices = graph.get_vertices()

        if not vertices:
            return False

        start = vertices[0].id
        visited: Set[int] = set()
        queue = deque([start])
        visited.add(start)

        while queue:
            current = queue.popleft()

            for neighbor, _weight in graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return len(visited) == graph.number_of_vertices()

    @staticmethod
    def is_dag(graph: Graph) -> bool:
        """
        Kiểm tra đồ thị có hướng không chu trình bằng thuật toán Kahn.

        DAG = Directed Acyclic Graph
        """

        if not graph.directed:
            return False

        in_degree = {
            vertex.id: 0 for vertex in graph.get_vertices()
        }

        for edge in graph.get_edges():
            in_degree[edge.target] += 1

        queue = deque()

        for vertex_id, degree in in_degree.items():
            if degree == 0:
                queue.append(vertex_id)

        visited_count = 0

        while queue:
            current = queue.popleft()
            visited_count += 1

            for neighbor, _weight in graph.get_neighbors(current):
                in_degree[neighbor] -= 1

                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return visited_count == graph.number_of_vertices()