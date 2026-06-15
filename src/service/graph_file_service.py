from pathlib import Path

from src.model.graph import Graph
from src.service.graph_parser import GraphParser


class GraphFileService:
    """
    Service dùng để đọc/ghi đồ thị từ file.

    Hiện tại hỗ trợ file .txt theo format:

        n m directed/undirected weighted/unweighted
        u v [w]
        u v [w]
        ...
    """

    @staticmethod
    def read_from_file(file_path: str) -> Graph:
        """
        Đọc đồ thị từ file .txt và trả về object Graph.

        Args:
            file_path: đường dẫn tới file đồ thị.

        Returns:
            Graph object.

        Raises:
            FileNotFoundError nếu file không tồn tại.
            ValueError nếu nội dung file sai format.
        """

        path = GraphFileService._normalize_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")

        if not path.is_file():
            raise ValueError(f"Đường dẫn không phải là file: {path}")

        text = path.read_text(encoding="utf-8")

        return GraphParser.parse_from_text(text)

    @staticmethod
    def save_to_file(graph: Graph, file_path: str) -> None:
        """
        Ghi đồ thị hiện tại ra file .txt.

        Args:
            graph: object Graph cần lưu.
            file_path: đường dẫn file muốn lưu.
        """

        path = GraphFileService._normalize_path(file_path)

        if path.parent:
            path.parent.mkdir(parents=True, exist_ok=True)

        text = GraphFileService._graph_to_text(graph)

        path.write_text(text, encoding="utf-8")

    @staticmethod
    def _graph_to_text(graph: Graph) -> str:
        """
        Chuyển object Graph thành chuỗi text đúng format.
        """

        n = graph.number_of_vertices()
        m = graph.number_of_edges()

        graph_type = "directed" if graph.directed else "undirected"
        weight_type = "weighted" if graph.weighted else "unweighted"

        lines = [
            f"{n} {m} {graph_type} {weight_type}"
        ]

        for edge in graph.get_edges():
            if graph.weighted:
                weight = GraphFileService._format_weight(edge.weight)
                lines.append(f"{edge.source} {edge.target} {weight}")
            else:
                lines.append(f"{edge.source} {edge.target}")

        return "\n".join(lines)

    @staticmethod
    def _format_weight(weight: float) -> str:
        if float(weight).is_integer():
            return str(int(weight))
        return str(weight)

    @staticmethod
    def _normalize_path(file_path: str) -> Path:
        cleaned_path = file_path.strip().strip('"').strip("'")
        return Path(cleaned_path)