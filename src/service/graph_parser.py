from src.model.graph import Graph

class GraphParser:
    @staticmethod
    def parse_from_text(text: str) -> Graph:

        lines = GraphParser._clean_lines(text)
        if not lines:
            raise ValueError("Dữ liệu đồ thị đang rỗng.")

        n, m, directed, weighted = GraphParser._parse_header(lines[0])

        if len(lines) - 1 < m: #check số dòng cạnh có đủ không
            raise ValueError(f"Số dòng cạnh không đủ. Cần {m} cạnh nhưng chỉ có {len(lines) - 1} dòng.")

        graph = Graph(directed=directed, weighted=weighted)

        # Thêm trước các đỉnh từ 1 đến n.
        # Việc này giúp giữ cả những đỉnh cô lập không có cạnh.
        for vertex_id in range(1, n + 1):
            graph.add_vertex(vertex_id)

        edge_lines = lines[1:1 + m]

        for index, line in enumerate(edge_lines, start=1):
            parts = line.split()

            if weighted:
                if len(parts) < 3:
                    raise ValueError(
                        f"Dòng cạnh thứ {index} không hợp lệ. "
                        f"Đồ thị có trọng số nên cần dạng: u v w."
                    )

                source = GraphParser._parse_int(parts[0], f"source ở dòng cạnh {index}")
                target = GraphParser._parse_int(parts[1], f"target ở dòng cạnh {index}")
                weight = GraphParser._parse_float(parts[2], f"weight ở dòng cạnh {index}")

            else:
                if len(parts) < 2:
                    raise ValueError(
                        f"Dòng cạnh thứ {index} không hợp lệ. "
                        f"Đồ thị không trọng số nên cần dạng: u v."
                    )

                source = GraphParser._parse_int(parts[0], f"source ở dòng cạnh {index}")
                target = GraphParser._parse_int(parts[1], f"target ở dòng cạnh {index}")
                weight = 1.0

            if source < 1 or source > n:
                raise ValueError(f"Đỉnh {source} không nằm trong khoảng 1 đến {n}.")

            if target < 1 or target > n:
                raise ValueError(f"Đỉnh {target} không nằm trong khoảng 1 đến {n}.")

            graph.add_edge(source, target, weight)

        return graph

    @staticmethod
    def _clean_lines(text: str) -> list[str]:# Loại bỏ các dòng trống và dòng bắt đầu bằng # (chú thích)
        clean_lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue
            if line.startswith("#"):
                continue
            clean_lines.append(line)
        return clean_lines

    @staticmethod
    def _parse_header(header_line: str) -> tuple[int, int, bool, bool]:
        parts = header_line.split()
        if len(parts) < 4:
            raise ValueError(
                "Dòng đầu tiên không hợp lệ. "
                "Cần dạng: n m directed/undirected weighted/unweighted."
            )

        n = GraphParser._parse_int(parts[0], "số đỉnh n")
        m = GraphParser._parse_int(parts[1], "số cạnh m")

        if n <= 0:
            raise ValueError("Số đỉnh n phải lớn hơn 0.")

        if m < 0:
            raise ValueError("Số cạnh m không được âm.")

        graph_type = parts[2].lower()
        weight_type = parts[3].lower()

        if graph_type in ["directed", "d", "cohuong", "cóhướng"]:
            directed = True
        elif graph_type in ["undirected", "u", "vohuong", "vôhướng"]:
            directed = False
        else:
            raise ValueError(
                "Loại đồ thị không hợp lệ. "
                "Chỉ dùng directed hoặc undirected."
            )

        if weight_type in ["weighted", "w", "cotrongsố", "cótrọngsố"]:
            weighted = True
        elif weight_type in ["unweighted", "uw", "khongtrongso", "khôngtrọngsố"]:
            weighted = False
        else:
            raise ValueError(
                "Loại trọng số không hợp lệ. "
                "Chỉ dùng weighted hoặc unweighted."
            )

        return n, m, directed, weighted

    @staticmethod
    def _parse_int(value: str, field_name: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Giá trị {field_name} phải là số nguyên: {value}")

    @staticmethod
    def _parse_float(value: str, field_name: str) -> float:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Giá trị {field_name} phải là số: {value}")