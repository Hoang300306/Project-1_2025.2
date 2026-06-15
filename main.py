from src.result.algorithm_parameter import AlgorithmParameter
from src.controller.algorithm_controller import AlgorithmController
from src.service.graph_parser import GraphParser
from src.service.graph_file_service import GraphFileService


def get_sample_graph_text() -> str:
    return """
7 6 undirected unweighted
1 2
1 3
2 4
2 5
3 6
5 7
"""


def read_graph_text_from_console() -> str:
    print("===== NHẬP ĐỒ THỊ TỪ BÀN PHÍM =====")
    print("Format:")
    print("n m directed/undirected weighted/unweighted")
    print("u v [w]")
    print("u v [w]")
    print("...")
    print("Nhập END để kết thúc.\n")

    lines = []

    while True:
        line = input()

        if line.strip().upper() == "END":
            break

        lines.append(line)

    return "\n".join(lines)


def load_graph_from_user_choice():
    print("===== CHỌN CÁCH NHẬP ĐỒ THỊ =====")
    print("1. Dùng đồ thị mẫu trong code")
    print("2. Nhập đồ thị từ bàn phím")
    print("3. Đọc đồ thị từ file .txt")

    choice = input("Chọn 1/2/3: ").strip()

    if choice == "1":
        graph_text = get_sample_graph_text()
        return GraphParser.parse_from_text(graph_text)

    if choice == "2":
        graph_text = read_graph_text_from_console()
        return GraphParser.parse_from_text(graph_text)

    if choice == "3":
        file_path = input("Nhập đường dẫn file .txt: ").strip()
        return GraphFileService.read_from_file(file_path)

    raise ValueError("Lựa chọn không hợp lệ. Chỉ được chọn 1, 2 hoặc 3.")


def print_graph_info(graph) -> None:
    print("\n===== THÔNG TIN ĐỒ THỊ =====")
    print(graph)

    print("\n===== DANH SÁCH KỀ =====")
    for vertex in graph.get_vertices():
        print(f"{vertex.id}: {graph.get_neighbors(vertex.id)}")


def print_result(result) -> None:
    print("\n===== KẾT QUẢ THUẬT TOÁN =====")
    print(result.get_summary())

    if not result.success:
        return

    print("\n===== CÁC BƯỚC CHẠY THUẬT TOÁN =====")
    for step in result.steps:
        print(step)
        print("-" * 50)


def input_integer(prompt: str) -> int:
    while True:
        value = input(prompt).strip()

        try:
            return int(value)
        except ValueError:
            print("Giá trị không hợp lệ. Vui lòng nhập một số nguyên.")


def input_optional_integer(prompt: str) -> int | None:
    value = input(prompt).strip()

    if value == "":
        return None

    try:
        return int(value)
    except ValueError:
        print("Giá trị không hợp lệ, hệ thống sẽ coi như không nhập.")
        return None


def input_algorithm_parameters(algorithm_name: str) -> AlgorithmParameter:
    """
    Nhập tham số riêng cho từng thuật toán.

    BFS/DFS/Dijkstra:
        cần start_vertex, có thể có target_vertex

    Prim:
        cần start_vertex nhưng có thể bỏ trống,
        nếu bỏ trống thì Prim tự chọn đỉnh đầu tiên.

    Kruskal:
        không cần start_vertex, không cần target_vertex
    """

    key = algorithm_name.lower().strip()

    if key in ["bfs", "dfs", "dijkstra", "bellman_ford"]:
        start_vertex = input_integer("\nNhập đỉnh bắt đầu: ")

        target_vertex = input_optional_integer(
            "Nhập đỉnh đích, bỏ trống nếu không cần: "
        )

        return AlgorithmParameter(
            start_vertex=start_vertex,
            target_vertex=target_vertex
        )

    if key == "prim":
        start_vertex = input_optional_integer(
            "\nNhập đỉnh bắt đầu cho Prim, bỏ trống để tự chọn đỉnh đầu tiên: "
        )

        return AlgorithmParameter(
            start_vertex=start_vertex,
            target_vertex=None
        )

    if key in ["floyd_warshall", "floyd-warshall", "floyd"]:
        print("\nFloyd-Warshall mặc định sẽ tính đường đi ngắn nhất giữa mọi cặp đỉnh.")
        print("Nếu muốn xem đường đi cụ thể, hãy nhập cả đỉnh nguồn và đỉnh đích.")
        print("Nếu không cần xem đường đi cụ thể, hãy bỏ trống cả hai.")

        start_vertex = input_optional_integer("Nhập đỉnh nguồn, bỏ trống nếu không cần: ")
        target_vertex = input_optional_integer("Nhập đỉnh đích, bỏ trống nếu không cần: ")

        return AlgorithmParameter(
            start_vertex=start_vertex,
            target_vertex=target_vertex
        )


    if key in ["topological_sort", "topological", "topo", "toposort"]:
        print("\nTopological Sort không cần nhập đỉnh bắt đầu hoặc đỉnh đích.")
        return AlgorithmParameter()

    if key == "kruskal":
        print("\nKruskal không cần nhập đỉnh bắt đầu hoặc đỉnh đích.")
        return AlgorithmParameter()

    print("\nThuật toán này chưa có phần nhập tham số riêng.")
    return AlgorithmParameter()


def run_algorithm_menu(graph) -> None:
    controller = AlgorithmController()

    print("\n===== DANH SÁCH THUẬT TOÁN HIỆN CÓ =====")
    available_algorithms = controller.get_available_algorithms()
    print(", ".join(available_algorithms))

    algorithm_name = input("\nNhập thuật toán cần chạy: ").strip().lower()

    algorithm = controller.get_algorithm(algorithm_name)

    if algorithm is None:
        print(f"Thuật toán '{algorithm_name}' chưa được hỗ trợ.")
        return

    print("\n===== MÔ TẢ THUẬT TOÁN =====")
    print(controller.get_algorithm_description(algorithm_name))

    params = input_algorithm_parameters(algorithm_name)

    result = controller.run_algorithm(
        algorithm_name,
        graph,
        params
    )

    print_result(result)


def main():
    try:
        graph = load_graph_from_user_choice()
    except FileNotFoundError as error:
        print(f"Lỗi file: {error}")
        return
    except ValueError as error:
        print(f"Lỗi dữ liệu: {error}")
        return

    print_graph_info(graph)

    run_algorithm_menu(graph)


if __name__ == "__main__":
    main()