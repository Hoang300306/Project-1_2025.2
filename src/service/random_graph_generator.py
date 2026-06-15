import random


class RandomGraphGenerator:
    """
    Sinh đồ thị ngẫu nhiên theo format text:

        n m directed/undirected weighted/unweighted
        u v [w]
        u v [w]
        ...
    """

    @staticmethod
    def generate_as_text(
        number_of_vertices: int,
        number_of_edges: int,
        directed: bool = False,
        weighted: bool = False,
        min_weight: int = 1,
        max_weight: int = 10,
        allow_negative_weight: bool = False
    ) -> str:
        if number_of_vertices <= 0:
            raise ValueError("Số đỉnh phải lớn hơn 0.")

        max_edges = RandomGraphGenerator._max_edges(
            number_of_vertices,
            directed
        )

        if number_of_edges < 0:
            raise ValueError("Số cạnh không được âm.")

        if number_of_edges > max_edges:
            raise ValueError(
                f"Số cạnh quá lớn. Với {number_of_vertices} đỉnh, "
                f"đồ thị {'có hướng' if directed else 'vô hướng'} tối đa có {max_edges} cạnh."
            )

        if weighted:
            if min_weight > max_weight:
                raise ValueError("Min weight không được lớn hơn Max weight.")

            if not allow_negative_weight and min_weight < 0:
                min_weight = 1

        graph_type = "directed" if directed else "undirected"
        weight_type = "weighted" if weighted else "unweighted"

        lines = [
            f"{number_of_vertices} {number_of_edges} {graph_type} {weight_type}"
        ]

        possible_edges = RandomGraphGenerator._generate_possible_edges(
            number_of_vertices,
            directed
        )

        selected_edges = random.sample(possible_edges, number_of_edges)

        for source, target in selected_edges:
            if weighted:
                weight = random.randint(min_weight, max_weight)

                if allow_negative_weight:
                    # Nếu người dùng cho phép cạnh âm nhưng min_weight vẫn dương,
                    # ta tạo khả năng xuất hiện cạnh âm bằng cách ngẫu nhiên đổi dấu.
                    if min_weight >= 0 and random.random() < 0.3:
                        weight = -weight

                lines.append(f"{source} {target} {weight}")
            else:
                lines.append(f"{source} {target}")

        return "\n".join(lines)

    @staticmethod
    def _max_edges(number_of_vertices: int, directed: bool) -> int:
        if directed:
            return number_of_vertices * (number_of_vertices - 1)

        return number_of_vertices * (number_of_vertices - 1) // 2

    @staticmethod
    def _generate_possible_edges(
        number_of_vertices: int,
        directed: bool
    ) -> list[tuple[int, int]]:
        edges = []

        if directed:
            for source in range(1, number_of_vertices + 1):
                for target in range(1, number_of_vertices + 1):
                    if source != target:
                        edges.append((source, target))
        else:
            for source in range(1, number_of_vertices + 1):
                for target in range(source + 1, number_of_vertices + 1):
                    edges.append((source, target))

        return edges