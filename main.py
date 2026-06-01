from src.model.graph import Graph
from src.result.algorithm_parameter import AlgorithmParameter
from src.controller.algorithm_controller import AlgorithmController


def build_sample_graph() -> Graph:
    """
    Tạo một đồ thị mẫu để test BFS và DFS.
    """
    graph = Graph(directed=False, weighted=False)

    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(2, 4)
    graph.add_edge(2, 5)
    graph.add_edge(3, 6)
    graph.add_edge(5, 7)

    return graph


def print_graph_info(graph: Graph) -> None:
    """
    In thông tin đồ thị và danh sách kề.
    """
    print("===== THÔNG TIN ĐỒ THỊ =====")
    print(graph)

    print("\n===== DANH SÁCH KỀ =====")
    for vertex in graph.get_vertices():
        print(f"{vertex.id}: {graph.get_neighbors(vertex.id)}")


def print_result(result) -> None:
    """
    In kết quả thuật toán.
    """
    print("\n===== KẾT QUẢ THUẬT TOÁN =====")
    print(result.get_summary())

    print("\n===== CÁC BƯỚC CHẠY THUẬT TOÁN =====")
    for step in result.steps:
        print(step)
        print("-" * 50)


def main():
    graph = build_sample_graph()
    print_graph_info(graph)

    controller = AlgorithmController()

    print("\n===== DANH SÁCH THUẬT TOÁN HIỆN CÓ =====")
    print(controller.get_available_algorithms())

    algorithm_name = input("\nNhập thuật toán cần chạy (bfs/dfs): ").strip()

    start_vertex = int(input("Nhập đỉnh bắt đầu: "))

    target_text = input("Nhập đỉnh đích, bỏ trống nếu không cần: ").strip()

    if target_text:
        target_vertex = int(target_text)
    else:
        target_vertex = None

    params = AlgorithmParameter(
        start_vertex=start_vertex,
        target_vertex=target_vertex
    )

    result = controller.run_algorithm(
        algorithm_name,
        graph,
        params
    )

    print_result(result)


if __name__ == "__main__":
    main()