from pathlib import Path
import time
from PySide6.QtGui import QAction, QKeySequence, QScreen
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QToolBar,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
    QCheckBox,
    QApplication,
    QScrollArea
)
from src.model.graph import Graph
from src.service.random_graph_generator import RandomGraphGenerator
from src.controller.algorithm_controller import AlgorithmController
from src.result.algorithm_parameter import AlgorithmParameter
from src.service.graph_parser import GraphParser
from src.ui.control_panel import ControlPanel
from src.ui.graph_view import GraphView
from src.service.graph_validator import GraphValidator
from src.ui.app_styles import get_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Graph Algorithm Visualizer")
        #self.resize(1200, 750)
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        width = int(screen_size.width() * 0.85)
        height = int(screen_size.height() * 0.85)
        self.resize(width, height)
        self.move(
            (screen_size.width() - width) // 2,
            (screen_size.height() - height) // 2
        )

        self.settings = QSettings(
            "HoangProjects",
            "GraphAlgorithmVisualizer"
        )

        self.last_open_dir = ""
        self.last_save_dir = ""
        self.last_export_dir = ""

        self.algorithm_controller = AlgorithmController()

        self.current_graph = None
        self.current_result = None
        self.current_step_index = -1
        # xu ly time
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self._auto_next_step)

        self.control_panel = ControlPanel()
        self.control_panel.set_algorithm_items(
            self.algorithm_controller.get_available_algorithms()
        )
        self.graph_view = GraphView()

        self.graph_info_text = QTextEdit()
        self.graph_info_text.setReadOnly(True)
        self.graph_info_text.setMaximumHeight(180)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(180)

        self.steps_text = QTextEdit()
        self.steps_text.setReadOnly(True)

        self.status_label = QLabel("Ready")
        self.status_label.setMinimumWidth(300)

        self._setup_status_bar()

        self._setup_ui()
        self._setup_menu_bar()
        self._setup_tool_bar()
        self._connect_signals()
        self._load_settings()
        self._load_sample_graph()

    def _setup_ui(self) -> None:
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        width = int(screen_size.width() * 0.85)
        height = int(screen_size.height() * 0.85)

        # Splitter ngang chính
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = self.control_panel

        # Phần trên cột phải: Graph Visualization
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(QLabel("Graph Visualization"))
        top_layout.addWidget(self.graph_view)

        # Phần dưới cột phải: 3 ô dùng chung QScrollArea
        bottom_content = QWidget()
        bottom_layout = QVBoxLayout(bottom_content)
        bottom_layout.setContentsMargins(4, 4, 4, 4)
        bottom_layout.setSpacing(4)

        self.graph_info_text.setMinimumHeight(200)
        self.result_text.setMinimumHeight(120)
        self.steps_text.setMinimumHeight(200)
        self.graph_info_text.setMaximumHeight(16777215)
        self.result_text.setMaximumHeight(16777215)

        bottom_layout.addWidget(QLabel("Graph Information"))
        bottom_layout.addWidget(self.graph_info_text)
        bottom_layout.addWidget(QLabel("Result"))
        bottom_layout.addWidget(self.result_text)
        bottom_layout.addWidget(QLabel("Current Algorithm Step"))
        bottom_layout.addWidget(self.steps_text)

        bottom_scroll = QScrollArea()
        bottom_scroll.setWidget(bottom_content)
        bottom_scroll.setWidgetResizable(True)
        bottom_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        bottom_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        bottom_scroll.setMinimumHeight(150)

        # Splitter dọc cho cột phải
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        vertical_splitter.addWidget(top_widget)
        vertical_splitter.addWidget(bottom_scroll)
        vertical_splitter.setCollapsible(0, False)
        vertical_splitter.setCollapsible(1, False)
        vertical_splitter.setSizes([int(height * 0.65), int(height * 0.35)])
        vertical_splitter.setStretchFactor(0, 65)
        vertical_splitter.setStretchFactor(1, 35)

        # Cột phải chứa vertical_splitter
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        right_layout.addWidget(vertical_splitter)

        # Splitter ngang
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        left_widget.setMinimumWidth(320)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([int(width * 0.22), int(width * 0.78)])
        splitter.setStretchFactor(0, 22)
        splitter.setStretchFactor(1, 78)

        self.setCentralWidget(splitter)

    
    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._adjust_splitter_sizes()

    def _adjust_splitter_sizes(self) -> None:
        w = self.width()
        h = self.height()
        
        # Tìm splitter ngang
        splitter = self.centralWidget()
        if isinstance(splitter, QSplitter):
            splitter.setSizes([int(w * 0.30), int(w * 0.70)])
            
            # Tìm splitter dọc trong cột phải
            right_widget = splitter.widget(1)
            if right_widget:
                for i in range(right_widget.layout().count()):
                    item = right_widget.layout().itemAt(i)
                    if item and isinstance(item.widget(), QSplitter):
                        vertical_splitter = item.widget()
                        vertical_splitter.setSizes([int(h * 0.65), int(h * 0.35)])
                        break

    def _connect_signals(self) -> None:
        self.control_panel.run_requested.connect(self._run_algorithm)
        self.control_panel.load_sample_requested.connect(self._load_sample_graph)
        self.control_panel.load_file_requested.connect(self._load_graph_from_file)
        self.control_panel.save_file_requested.connect(self._save_graph_to_file)
        self.control_panel.generate_random_requested.connect(self._generate_random_graph)
        self.control_panel.clear_requested.connect(self._clear_ui)
        self.control_panel.reset_layout_requested.connect(self._reset_layout)
        #self.control_panel.export_result_requested.connect(self._export_result_to_file)
        #self.control_panel.export_image_requested.connect(self._export_graph_image)

        self.control_panel.algorithm_changed.connect(self._update_algorithm_info)
        self.control_panel.theme_changed.connect(self._apply_theme)
        self.control_panel.zoom_in_requested.connect(self.graph_view.zoom_in)
        self.control_panel.zoom_out_requested.connect(self.graph_view.zoom_out)
        self.control_panel.reset_zoom_requested.connect(self.graph_view.reset_zoom)
        self.control_panel.fit_view_requested.connect(self.graph_view.fit_graph)
        self.control_panel.apply_layout_requested.connect(self._apply_graph_layout)

        self.control_panel.add_vertex_requested.connect(self._add_vertex)
        self.control_panel.remove_vertex_requested.connect(self._remove_vertex_from_input)
        self.control_panel.add_edge_requested.connect(self._add_edge)
        self.control_panel.remove_edge_requested.connect(self._remove_edge)

        self.graph_view.vertex_clicked.connect(self._handle_vertex_clicked)
        self.graph_view.set_start_requested.connect(self._set_start_vertex_from_graph)
        self.graph_view.set_target_requested.connect(self._set_target_vertex_from_graph)
        self.graph_view.remove_vertex_requested.connect(self._remove_vertex_by_id)

        self.control_panel.previous_step_requested.connect(self._previous_step)
        self.control_panel.next_step_requested.connect(self._next_step)
        self.control_panel.reset_step_requested.connect(self._reset_step)
        self.control_panel.show_result_requested.connect(self._show_final_result)
        
        self.control_panel.auto_run_requested.connect(self._start_auto_run)
        self.control_panel.pause_requested.connect(self._pause_auto_run)

    def _load_sample_graph(self) -> None:
        sample_text = """7 6 undirected unweighted
1 2
1 3
2 4
2 5
3 6
5 7
"""
        self.control_panel.set_graph_text(sample_text)
        self._parse_and_draw_graph()
        self._clear_algorithm_state()
        self._show_success("Sample graph loaded.")

    def _load_graph_from_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open graph file",
            "",
            "Text files (*.txt);;All files (*)"
        )

        if not file_path:
            return

        try:
            text = Path(file_path).read_text(encoding="utf-8")
            self.last_open_dir = str(Path(file_path).parent)

            self.control_panel.set_graph_text(text)
            self._parse_and_draw_graph()
            self._clear_algorithm_state()
            self._show_success("Graph file loaded successfully.")
        except Exception as error:
            self._show_error("Lỗi đọc file", str(error))
# sinh dothi ngau nhien
    def _generate_random_graph(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Random Graph")
        dialog.setMinimumWidth(300)

        layout = QFormLayout(dialog)

        vertex_input = QSpinBox()
        vertex_input.setRange(1, 100)
        vertex_input.setValue(self.control_panel.get_random_vertex_count())

        edge_input = QSpinBox()
        edge_input.setRange(0, 1000)
        edge_input.setValue(self.control_panel.get_random_edge_count())

        directed_cb = QCheckBox("Directed")
        directed_cb.setChecked(self.control_panel.is_random_directed())

        weighted_cb = QCheckBox("Weighted")
        weighted_cb.setChecked(self.control_panel.is_random_weighted())

        min_weight = QSpinBox()
        min_weight.setRange(-100, 100)
        min_weight.setValue(self.control_panel.get_random_min_weight())

        max_weight = QSpinBox()
        max_weight.setRange(-100, 100)
        max_weight.setValue(self.control_panel.get_random_max_weight())

        allow_negative_cb = QCheckBox("Allow negative weight")
        allow_negative_cb.setChecked(self.control_panel.is_random_negative_allowed())

        layout.addRow("Number of vertices:", vertex_input)
        layout.addRow("Number of edges:", edge_input)
        layout.addRow("", directed_cb)
        layout.addRow("", weighted_cb)
        layout.addRow("Min weight:", min_weight)
        layout.addRow("Max weight:", max_weight)
        layout.addRow("", allow_negative_cb)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            graph_text = RandomGraphGenerator.generate_as_text(
                number_of_vertices=vertex_input.value(),
                number_of_edges=edge_input.value(),
                directed=directed_cb.isChecked(),
                weighted=weighted_cb.isChecked(),
                min_weight=min_weight.value(),
                max_weight=max_weight.value(),
                allow_negative_weight=allow_negative_cb.isChecked()
            )

            self.control_panel.set_graph_text(graph_text)
            self.graph_view.vertex_positions.clear()
            self._parse_and_draw_graph()
            self._clear_algorithm_state()
            self._show_success("Random graph generated successfully.")

        except Exception as error:
            self._show_error("Lỗi sinh đồ thị ngẫu nhiên", str(error))

    def _clear_ui(self) -> None:
        self.current_graph = None
        self._clear_algorithm_state()

        self.control_panel.clear_all()
        self.graph_view.scene.clear()
        self.graph_info_text.clear()
        self.result_text.clear()
        self.steps_text.clear()

        self.graph_view.clear_runtime()

        self._update_algorithm_info()
        self._show_success('Workspace cleared.')

    def _clear_algorithm_state(self) -> None:
        self.auto_timer.stop() # de dung do thi
        
        self.current_result = None
        self.current_step_index = -1
        self.control_panel.set_step_info(0, 0)
        self.result_text.clear()
        self.steps_text.clear()

        self.graph_view.clear_runtime()

    def _parse_and_draw_graph(self) -> bool:
        graph_text = self.control_panel.get_graph_text()

        try:
            self.current_graph = GraphParser.parse_from_text(graph_text)
            self.graph_view.draw_graph(self.current_graph)
            self._show_graph_info()
            self._update_algorithm_info()
            return True
        except Exception as error:
            self.current_graph = None
            self.graph_info_text.clear()
            self._update_algorithm_info()
            self._show_error("Lỗi dữ liệu đồ thị", str(error))
            return False

    def _run_algorithm(self) -> None:
        self.auto_timer.stop() # de dung dothi
        self._set_status("Running algorithm...", "info")

        if not self._parse_and_draw_graph():
            return

        algorithm_name = self.control_panel.get_algorithm_name()

        try:
            start_vertex = self.control_panel.get_start_vertex()
            target_vertex = self.control_panel.get_target_vertex()
        except ValueError:
            self._show_error(
                "Lỗi tham số",
                "Start vertex và Target vertex phải là số nguyên hoặc để trống."
            )
            return

        params = AlgorithmParameter(
            start_vertex=start_vertex,
            target_vertex=target_vertex
        )

        start_time = time.perf_counter()

        result = self.algorithm_controller.run_algorithm(
            algorithm_name,
            self.current_graph,
            params
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self.graph_view.set_runtime(elapsed_ms)
        # ---- ĐO THỜI GIAN KẾT THÚC ----

    
        self.current_result = result
        if result.success:
            self._show_success(f"Algorithm {result.algorithm_name} finished successfully.")
        else:
            self._show_warning(result.message)

        self._show_result_summary(result)

        if result.steps:
            self.current_step_index = 0
            self._show_current_step()
        else:
            self.current_step_index = -1
            self.control_panel.set_step_info(0, 0)
            self.steps_text.setPlainText("Thuật toán không có step để debug.")
            self._highlight_result(result)

    def _show_result_summary(self, result) -> None:
        self.result_text.setPlainText(result.get_summary())

    def _show_current_step(self) -> None:
        if self.current_result is None:
            self._show_error("Debug error", "Chưa có thuật toán nào được chạy.")
            return

        steps = self.current_result.steps

        if not steps:
            self.steps_text.setPlainText("Không có step để hiển thị.")
            self.control_panel.set_step_info(0, 0)
            return

        if self.current_step_index < 0:
            self.current_step_index = 0

        if self.current_step_index >= len(steps):
            self.current_step_index = len(steps) - 1

        step = steps[self.current_step_index]

        self.control_panel.set_step_info(
            self.current_step_index + 1,
            len(steps)
        )
        self._set_status(
            f"Showing step {self.current_step_index + 1}/{len(steps)}.",
            "info",
            timeout_ms=2000
        )
        self.steps_text.setPlainText(str(step))

        self.graph_view.draw_graph(
            self.current_graph,
            highlighted_vertices=step.highlighted_vertices,
            highlighted_edges=step.highlighted_edges
        )

    def _next_step(self) -> None:
        if self.current_result is None or not self.current_result.steps:
            self._show_error("Debug error", "Chưa có bước chạy thuật toán.")
            return

        if self.current_step_index < len(self.current_result.steps) - 1:
            self.current_step_index += 1
            self._show_current_step()
        else:
            QMessageBox.information(
                self,
                "Debug",
                "Đã ở bước cuối cùng."
            )

    def _previous_step(self) -> None:
        if self.current_result is None or not self.current_result.steps:
            self._show_error("Debug error", "Chưa có bước chạy thuật toán.")
            return

        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._show_current_step()
        else:
            QMessageBox.information(
                self,
                "Debug",
                "Đã ở bước đầu tiên."
            )

    def _reset_step(self) -> None:
        if self.current_result is None or not self.current_result.steps:
            self._show_error("Debug error", "Chưa có bước chạy thuật toán.")
            return

        self.current_step_index = 0
        self._show_current_step()

    def _show_final_result(self) -> None:
        self.auto_timer.stop() # de dung time do thi

        if self.current_result is None:
            self._show_error("Result error", "Chưa có thuật toán nào được chạy.")
            return

        self._show_result_summary(self.current_result)
        self._highlight_result(self.current_result)

        total_steps = len(self.current_result.steps)
        if total_steps > 0:
            self.control_panel.set_step_info(total_steps, total_steps)

        self.steps_text.setPlainText(
            "Đang hiển thị kết quả cuối cùng.\n\n"
            "Bấm Reset Step để quay lại bước đầu tiên hoặc Previous/Next để debug từng bước."
        )
        self._show_success("Final result is displayed.")

    def _highlight_result(self, result) -> None:
        highlighted_vertices = []

        if result.path:
            highlighted_vertices = result.path
        elif result.traversal_order:
            highlighted_vertices = result.traversal_order

        highlighted_edges = result.result_edges

        self.graph_view.draw_graph(
            self.current_graph,
            highlighted_vertices=highlighted_vertices,
            highlighted_edges=highlighted_edges
        )

    def _start_auto_run(self) -> None:
        if self.current_result is None or not self.current_result.steps:
            self._show_error("Auto Run error", " Chua co buoc chay thuat toan.")
            return
        
        speed_ms = self.control_panel.get_speed_ms()
        if self.current_step_index < 0:
            self.current_step_index = 0
            self._show_current_step()

        self.auto_timer.start(speed_ms)
        self._show_success("Auto run started.")

    def _pause_auto_run(self) -> None:
        if self.auto_timer.isActive():
            self.auto_timer.stop()
            self._show_warning("Auto run paused.")
        else:
            self._show_warning("Auto run is not active.")
    
    def _auto_next_step(self) -> None:
        if self.current_result is None or not self.current_result.steps:
            self.auto_timer.stop()
            return

        if self.current_step_index < len(self.current_result.steps) - 1:
            self.current_step_index += 1
            self._show_current_step()
        else:
            self.auto_timer.stop()
            self._show_success("Auto run finished.")
    
    def _reset_layout(self) -> None:
        if self.current_graph is None:
            self._show_warning("No graph available to reset layout.")
            return

        self.graph_view.reset_layout()
        self._show_success("Graph layout reset to Circle.")

    def _show_graph_info(self) -> None:
        if self.current_graph is None:
            self.graph_info_text.clear()
            return

        text = self._format_graph_info(self.current_graph)
        self.graph_info_text.setPlainText(text)

    def _format_graph_info(self, graph) -> str:
        graph_type = "Directed" if graph.directed else "Undirected"
        weight_type = "Weighted" if graph.weighted else "Unweighted"

        lines = [
            f"Graph type: {graph_type}, {weight_type}",
            f"Number of vertices: {graph.number_of_vertices()}",
            f"Number of edges: {graph.number_of_edges()}",
            "",
            "Edges:"
        ]

        for edge in graph.get_edges():
            if graph.directed:
                connector = "->"
            else:
                connector = "-"

            if graph.weighted:
                lines.append(
                    f"{edge.source} {connector} {edge.target}, weight = {self._format_weight(edge.weight)}"
                )
            else:
                lines.append(
                    f"{edge.source} {connector} {edge.target}"
                )

        lines.append("")
        lines.append("Adjacency list:")

        for vertex in graph.get_vertices():
            neighbors = graph.get_neighbors(vertex.id)

            if graph.weighted:
                neighbor_text = [
                 f"({neighbor}, {self._format_weight(weight)})"
                    for neighbor, weight in neighbors
                ]
            else:
                neighbor_text = [
                    str(neighbor)
                    for neighbor, _weight in neighbors
                ]

            lines.append(f"{vertex.id}: [{', '.join(neighbor_text)}]")

        return "\n".join(lines)


    def _format_weight(self, value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return str(value)
    
    def _update_algorithm_info(self, algorithm_name: str | None = None) -> None:
        if algorithm_name is None:
            algorithm_name = self.control_panel.get_algorithm_name()

        info_text = self._build_algorithm_info_text(algorithm_name)
        self.control_panel.set_algorithm_info(info_text)


    def _build_algorithm_info_text(self, algorithm_name: str) -> str:
        key = algorithm_name.lower().strip()

        algorithm = self.algorithm_controller.get_algorithm(key)

        if algorithm is None:
            return f"Không tìm thấy thuật toán: {algorithm_name}"

        lines = []

        lines.append(f"Algorithm: {algorithm.get_name()}")
        lines.append("")

        lines.append("Description:")
        lines.append(algorithm.get_description())
        lines.append("")

        lines.append("Required parameters:")
        lines.extend(self._get_algorithm_parameter_info(key))
        lines.append("")

        lines.append("Conditions:")
        lines.extend(self._get_algorithm_condition_info(key))
        lines.append("")

        lines.append("Current graph validation:")

        if self.current_graph is None:
            lines.append("Chưa có đồ thị hợp lệ để kiểm tra.")
        else:
            validation = GraphValidator.validate_for_algorithm(key, self.current_graph)
            lines.append(validation.message)

            if validation.warnings:
                lines.append("")
                lines.append("Warnings:")
                for warning in validation.warnings:
                    lines.append(f"- {warning}")

        return "\n".join(lines)


    def _get_algorithm_parameter_info(self, key: str) -> list[str]:
        if key in ["bfs", "dfs", "dijkstra", "bellman_ford", "bellman-ford", "bellmanford"]:
            return [
                "- Start vertex: bắt buộc",
                "- Target vertex: tùy chọn"
            ]

        if key in ["floyd_warshall", "floyd-warshall", "floyd"]:
            return [
                "- Start vertex: tùy chọn",
                "- Target vertex: tùy chọn",
                "- Nếu muốn xem đường đi cụ thể, cần nhập cả Start và Target",
                "- Nếu bỏ trống cả hai, thuật toán sẽ tính mọi cặp đỉnh"
            ]

        if key == "prim":
            return [
                "- Start vertex: tùy chọn",
                "- Target vertex: không cần"
            ]

        if key == "kruskal":
            return [
                "- Start vertex: không cần",
                "- Target vertex: không cần"
            ]

        if key in ["topological_sort", "topological", "topo", "toposort"]:
            return [
                "- Start vertex: không cần",
                "- Target vertex: không cần"
            ]

        return [
            "- Chưa có mô tả tham số cho thuật toán này"
        ]


    def _get_algorithm_condition_info(self, key: str) -> list[str]:
        if key == "bfs":
            return [
                "- Chạy được trên đồ thị có hướng hoặc vô hướng",
                "- Chạy được trên đồ thị có trọng số hoặc không trọng số",
                "- Nếu đồ thị có trọng số, BFS chỉ tìm đường theo số cạnh, không tối ưu tổng trọng số"
            ]

        if key == "dfs":
            return [
                "- Chạy được trên đồ thị có hướng hoặc vô hướng",
                "- Chạy được trên đồ thị có trọng số hoặc không trọng số",
                "- DFS dùng để duyệt hoặc tìm đường, không đảm bảo đường đi ngắn nhất"
            ]

        if key == "dijkstra":
            return [
                "- Chạy được trên đồ thị có hướng hoặc vô hướng",
                "- Không được có cạnh trọng số âm",
                "- Phù hợp để tìm đường đi ngắn nhất từ một nguồn"
            ]

        if key in ["bellman_ford", "bellman-ford", "bellmanford"]:
            return [
                "- Chạy được trên đồ thị có hướng hoặc vô hướng",
                "- Cho phép cạnh trọng số âm",
                "- Có thể phát hiện chu trình âm",
                "- Phù hợp khi đồ thị có cạnh âm"
            ]

        if key in ["floyd_warshall", "floyd-warshall", "floyd"]:
            return [
                "- Chạy được trên đồ thị có hướng hoặc vô hướng",
                "- Cho phép cạnh trọng số âm",
                "- Có thể phát hiện chu trình âm",
                "- Tìm đường đi ngắn nhất giữa mọi cặp đỉnh",
                "- Độ phức tạp O(V^3), nên không phù hợp với đồ thị quá lớn"
            ]

        if key == "prim":
            return [
                "- Chỉ áp dụng cho đồ thị vô hướng",
                "- Đồ thị phải có trọng số",
                "- Đồ thị phải liên thông",
                "- Dùng để tìm cây khung nhỏ nhất"
            ]

        if key == "kruskal":
            return [
                "- Chỉ áp dụng cho đồ thị vô hướng",
                "- Đồ thị phải có trọng số",
                "- Đồ thị phải liên thông",
                "- Dùng để tìm cây khung nhỏ nhất"
            ]

        if key in ["topological_sort", "topological", "topo", "toposort"]:
            return [
                "- Chỉ áp dụng cho đồ thị có hướng",
                "- Đồ thị không được có chu trình",
                "- Dùng cho DAG",
                "- Phù hợp với bài toán thứ tự công việc hoặc môn học tiên quyết"
            ]

        return [
            "- Chưa có mô tả điều kiện cho thuật toán này"
        ]   
    
    def _setup_status_bar(self) -> None:
        status_bar = self.statusBar()
        status_bar.addPermanentWidget(self.status_label)

        self._set_status("Ready", "info")

    def _set_status(
        self,
        message: str,
        level: str = "info",
        timeout_ms: int = 5000
    ) -> None:
        styles = {
            "info": "color: #2c3e50;",
            "success": "color: #1e8449; font-weight: bold;",
            "warning": "color: #b9770e; font-weight: bold;",
            "error": "color: #c0392b; font-weight: bold;",
        }

        prefixes = {
            "info": "Info",
            "success": "Success",
            "warning": "Warning",
            "error": "Error",
        }

        style = styles.get(level, styles["info"])
        prefix = prefixes.get(level, "Info")

        self.status_label.setStyleSheet(style)
        self.status_label.setText(f"{prefix}: {message}")
        self.statusBar().showMessage(message, timeout_ms)


    def _show_success(self, message: str) -> None:
        self._set_status(message, "success")


    def _show_warning(self, message: str) -> None:
        self._set_status(message, "warning")


    def _show_error(self, title: str, message: str) -> None:
        self._set_status(message, "error", timeout_ms=8000)
        QMessageBox.critical(self, title, message)

    def _save_graph_to_file(self) -> None:
        graph_text = self.control_panel.get_graph_text().strip()

        if not graph_text:
            self._show_error(
                "Lỗi lưu file",
                "Chưa có dữ liệu đồ thị để lưu."
            )
            return

        try:
            # Kiểm tra dữ liệu đồ thị trước khi lưu.
            graph = GraphParser.parse_from_text(graph_text)
            self.current_graph = graph
            self.graph_view.draw_graph(self.current_graph)
            self._show_graph_info()
        except Exception as error:
            self._show_error(
                "Lỗi dữ liệu đồ thị",
                f"Dữ liệu đồ thị chưa hợp lệ nên không thể lưu.\n\n{error}"
            )
            return

        default_path = "graph.txt"

        if self.last_save_dir:
            default_path = str(Path(self.last_save_dir) / "graph.txt")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save graph file",
            default_path,
            "Text files (*.txt);;All files (*)"
        )

        if not file_path:
            self._show_warning("Save file cancelled.")
            return

        if not file_path.lower().endswith(".txt"):
            file_path += ".txt"

        self.last_save_dir = str(Path(file_path).parent)
        try:
            Path(file_path).write_text(
                graph_text + "\n",
                encoding="utf-8"
            )

            QMessageBox.information(
                self,
                "Lưu file thành công",
                f"Đã lưu đồ thị vào file:\n{file_path}"
            )

        except Exception as error:
            self._show_error(
                "Lỗi lưu file",
                str(error)
            )
    
    def _export_result_to_file(self) -> None:
        if self.current_graph is None:
            self._show_error(
                "Lỗi export",
                "Chưa có đồ thị để export kết quả."
            )
            return

        if self.current_result is None:
            self._show_error(
                "Lỗi export",
                "Chưa có kết quả thuật toán. Hãy bấm Run Algorithm trước."
            )
            return

        default_path = "algorithm_result.txt"

        if self.last_export_dir:
            default_path = str(Path(self.last_export_dir) / "algorithm_result.txt")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export algorithm result",
            default_path,
            "Text files (*.txt);;All files (*)"
        )

        if not file_path:
            self._show_warning("Export result cancelled.")
            return

        if not file_path.lower().endswith(".txt"):
            file_path += ".txt"

        self.last_export_dir = str(Path(file_path).parent)

        try:
            export_text = self._build_export_result_text()

            Path(file_path).write_text(
                export_text,
                encoding="utf-8"
            )

            QMessageBox.information(
                self,
                "Export thành công",
                f"Đã export kết quả thuật toán vào file:\n{file_path}"
            )

        except Exception as error:
            self._show_error(
                "Lỗi export",
                str(error)
            )

    def _build_export_result_text(self) -> str:
        graph_text = self.control_panel.get_graph_text().strip()

        lines = []

        lines.append("=" * 70)
        lines.append("GRAPH ALGORITHM VISUALIZER - EXPORT RESULT")
        lines.append("=" * 70)

        lines.append("")
        lines.append("[1] GRAPH INPUT")
        lines.append("-" * 70)
        lines.append(graph_text)

        lines.append("")
        lines.append("[2] GRAPH INFORMATION")
        lines.append("-" * 70)

        if self.current_graph is not None:
            lines.append(self._format_graph_info(self.current_graph))
        else:
            lines.append("No graph information.")

        lines.append("")
        lines.append("[3] ALGORITHM RESULT")
        lines.append("-" * 70)

        if self.current_result is not None:
            lines.append(self.current_result.get_summary())
        else:
            lines.append("No algorithm result.")

        lines.append("")
        lines.append("[4] ALGORITHM STEPS")
        lines.append("-" * 70)

        if self.current_result is not None and self.current_result.steps:
            for step in self.current_result.steps:
                lines.append(str(step))
                lines.append("")
                lines.append("-" * 70)
        else:
            lines.append("No algorithm steps.")

        lines.append("")
        lines.append("=" * 70)
        lines.append("END OF EXPORT")
        lines.append("=" * 70)

        return "\n".join(lines)
    
    def _export_graph_image(self) -> None:
        if self.current_graph is None:
            graph_text = self.control_panel.get_graph_text().strip()

            if not graph_text:
                self._show_error(
                    "Lỗi export ảnh",
                    "Chưa có đồ thị để export ảnh."
                )
                return

            if not self._parse_and_draw_graph():
                return

        default_path = "graph_visualization.png"

        if self.last_export_dir:
            default_path = str(Path(self.last_export_dir) / "graph_visualization.png")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export graph image",
            default_path,
            "PNG images (*.png);;All files (*)"
        )

        if not file_path:
            self._show_warning("Export image cancelled.")
            return

        if not file_path.lower().endswith(".png"):
            file_path += ".png"

        self.last_export_dir = str(Path(file_path).parent)

        try:
            self.graph_view.export_to_png(file_path)

            QMessageBox.information(
                self,
                "Export ảnh thành công",
                f"Đã export hình ảnh đồ thị vào file:\n{file_path}"
            )

        except Exception as error:
            self._show_error(
                "Lỗi export ảnh",
                str(error)
            )
    
    def _apply_theme(self, theme_name: str) -> None:
        self.setStyleSheet(get_stylesheet(theme_name))
        self._set_status(f"{theme_name} theme applied.", "success")

    def _load_settings(self) -> None:
        theme_name = self.settings.value("theme_name", "Light")
        speed_ms = int(self.settings.value("speed_ms", 800))

        self.last_open_dir = self.settings.value("last_open_dir", "")
        self.last_save_dir = self.settings.value("last_save_dir", "")
        self.last_export_dir = self.settings.value("last_export_dir", "")

        self.control_panel.set_theme_name(theme_name)
        self.control_panel.set_speed_ms(speed_ms)

        self._apply_theme(theme_name)

        geometry = self.settings.value("window_geometry")

        if geometry is not None:
            self.restoreGeometry(geometry)

        self._set_status("Settings loaded.", "success")
    
    def _save_settings(self) -> None:
        self.settings.setValue(
            "theme_name",
            self.control_panel.get_theme_name()
        )

        self.settings.setValue(
            "speed_ms",
            self.control_panel.get_speed_ms()
        )

        self.settings.setValue(
            "last_open_dir",
            self.last_open_dir
        )

        self.settings.setValue(
            "last_save_dir",
            self.last_save_dir
        )

        self.settings.setValue(
            "last_export_dir",
            self.last_export_dir
        )

        self.settings.setValue(
            "window_geometry",
            self.saveGeometry()
        )
    #tat nhung van luu lai cau hinh
    def closeEvent(self, event) -> None:
        self._save_settings()
        super().closeEvent(event)
    #set  thanh menu
    def _setup_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New Graph", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self._clear_ui)

        load_action = QAction("Load Graph", self)
        load_action.setShortcut(QKeySequence("Ctrl+O"))
        load_action.triggered.connect(self._load_graph_from_file)

        save_action = QAction("Save Graph", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._save_graph_to_file)

        export_result_action = QAction("Export Result", self)
        export_result_action.triggered.connect(self._export_result_to_file)

        export_image_action = QAction("Export Image", self)
        export_image_action.triggered.connect(self._export_graph_image)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(load_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(export_result_action)
        file_menu.addAction(export_image_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("View")

        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(
            lambda: self._set_theme_from_menu("Light")
        )

        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(
            lambda: self._set_theme_from_menu("Dark")
        )

        reset_layout_action = QAction("Reset Layout", self)
        reset_layout_action.triggered.connect(self._reset_layout)

        fit_view_action = QAction("Fit View", self)
        fit_view_action.triggered.connect(self.graph_view.fit_graph)

        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.triggered.connect(self.graph_view.reset_zoom)

        view_menu.addAction(light_theme_action)
        view_menu.addAction(dark_theme_action)
        view_menu.addSeparator()
        view_menu.addAction(reset_layout_action)
        view_menu.addAction(fit_view_action)
        view_menu.addAction(reset_zoom_action)

        algorithm_menu = menu_bar.addMenu("Debug")

        run_action = QAction("Run Algorithm", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self._run_algorithm)

        previous_action = QAction("Previous Step", self)
        previous_action.triggered.connect(self._previous_step)

        next_action = QAction("Next Step", self)
        next_action.triggered.connect(self._next_step)

        auto_run_action = QAction("Auto Run", self)
        auto_run_action.triggered.connect(self._start_auto_run)

        pause_action = QAction("Pause", self)
        pause_action.triggered.connect(self._pause_auto_run)

        show_result_action = QAction("Show Final Result", self)
        show_result_action.triggered.connect(self._show_final_result)

        algorithm_menu.addAction(run_action)
        algorithm_menu.addSeparator()
        algorithm_menu.addAction(previous_action)
        algorithm_menu.addAction(next_action)
        algorithm_menu.addSeparator()
        algorithm_menu.addAction(auto_run_action)
        algorithm_menu.addAction(pause_action)
        algorithm_menu.addSeparator()
        algorithm_menu.addAction(show_result_action)

        help_menu = menu_bar.addMenu("Help")

        user_guide_action = QAction("User Guide", self)
        user_guide_action.triggered.connect(self._show_user_guide)

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)

        help_menu.addAction(user_guide_action)
        help_menu.addAction(about_action)

    def _set_theme_from_menu(self, theme_name: str) -> None:
        self.control_panel.set_theme_name(theme_name)
        self._apply_theme(theme_name)

    def _show_user_guide(self) -> None:
        message = (
            "Graph Algorithm Visualizer\n\n"
            "1. Nhập đồ thị trong ô Graph Input hoặc bấm Load File.\n"
            "2. Chọn thuật toán cần chạy.\n"
            "3. Nhập Start Vertex và Target Vertex nếu thuật toán yêu cầu.\n"
            "4. Bấm Run Algorithm để chạy.\n"
            "5. Dùng Next Step / Previous Step để debug từng bước.\n"
            "6. Dùng Auto Run để tự động chạy từng bước.\n"
            "7. Dùng Save File, Export Result hoặc Export Image để lưu dữ liệu."
        )

        QMessageBox.information(
            self,
            "User Guide",
            message
        )


    def _show_about(self) -> None:
        message = (
            "Graph Algorithm Visualizer\n\n"
            "A learning tool for graph algorithms.\n\n"
            "Supported algorithms:\n"
            "- BFS\n"
            "- DFS\n"
            "- Dijkstra\n"
            "- Bellman-Ford\n"
            "- Floyd-Warshall\n"
            "- Prim\n"
            "- Kruskal\n"
            "- Topological Sort\n\n"
            "Built with Python and PySide6."
        )

        QMessageBox.information(
            self,
            "About",
            message
        )
    #thanh tool
    def _setup_tool_bar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        self._add_toolbar_action(
            toolbar,
            "Load",
            self._load_graph_from_file
        )

        self._add_toolbar_action(
            toolbar,
            "Save",
            self._save_graph_to_file
        )

        toolbar.addSeparator()

        self._add_toolbar_action(toolbar, "Random Graph", self._generate_random_graph)  # THÊM

        toolbar.addSeparator()

        self._add_toolbar_action(
            toolbar,
            "Run",
            self._run_algorithm
        )

        self._add_toolbar_action(
            toolbar,
            "Previous",
            self._previous_step
        )

        self._add_toolbar_action(
            toolbar,
            "Next",
            self._next_step
        )

        toolbar.addSeparator()

        self._add_toolbar_action(
            toolbar,
            "Auto",
            self._start_auto_run
        )

        self._add_toolbar_action(
            toolbar,
            "Pause",
            self._pause_auto_run
        )

        self._add_toolbar_action(
            toolbar,
            "Result",
            self._show_final_result
        )

        toolbar.addSeparator()

        self._add_toolbar_action(
            toolbar,
            "Export TXT",
            self._export_result_to_file
        )

        self._add_toolbar_action(
            toolbar,
            "Export PNG",
            self._export_graph_image
        )

        toolbar.addSeparator()

        self._add_toolbar_action(
            toolbar,
            "Reset Layout",
            self._reset_layout
        )
        self._add_toolbar_action(
            toolbar,
            "Fit",
            self.graph_view.fit_graph
        )

        self._add_toolbar_action(
            toolbar,
            "Reset Zoom",
            self.graph_view.reset_zoom
        )
    
    def _add_toolbar_action(
        self,
        toolbar: QToolBar,
        text: str,
        slot
    ) -> QAction:
        action = QAction(text, self)
        action.triggered.connect(slot)
        toolbar.addAction(action)

        return action
    
    def _apply_graph_layout(self, layout_name: str) -> None:
        if self.current_graph is None:
            self._show_warning("No graph available to apply layout.")
            return

        self.graph_view.apply_layout(layout_name)
        self._show_success(f"{layout_name} layout applied.")

    def _ensure_current_graph(self) -> bool:
        graph_text = self.control_panel.get_graph_text().strip()

        if not graph_text:
            self.current_graph = Graph(directed=False, weighted=False)
            self.current_graph.add_vertex(1)
            self._sync_graph_input_from_current_graph()
            self.graph_view.draw_graph(self.current_graph)
            self._show_graph_info()
            return True

        try:
            self.current_graph = GraphParser.parse_from_text(graph_text)
            return True
        except Exception as error:
            self._show_error(
                "Lỗi dữ liệu đồ thị",
                f"Không thể chỉnh sửa vì dữ liệu đồ thị chưa hợp lệ.\n\n{error}"
            )
            return False
        
    def _sync_graph_input_from_current_graph(self) -> None:
        if self.current_graph is None:
            self.control_panel.set_graph_text("")
            return

        graph = self.current_graph

        vertices = sorted([vertex.id for vertex in graph.get_vertices()])

        if not vertices:
            self.control_panel.set_graph_text("")
            return

        max_vertex_id = max(vertices)
        edge_count = graph.number_of_edges()

        graph_type = "directed" if graph.directed else "undirected"
        weight_type = "weighted" if graph.weighted else "unweighted"

        lines = [
            f"{max_vertex_id} {edge_count} {graph_type} {weight_type}"
        ]

        for edge in graph.get_edges():
            if graph.weighted:
                lines.append(
                    f"{edge.source} {edge.target} {self._format_weight(edge.weight)}"
                )
            else:
                lines.append(
                    f"{edge.source} {edge.target}"
                )

        self.control_panel.set_graph_text("\n".join(lines))

    def _refresh_after_graph_edit(self, message: str) -> None:
        if self.current_graph is None:
            return

        self._sync_graph_input_from_current_graph()
        self.graph_view.draw_graph(self.current_graph)
        self._show_graph_info()
        self._update_algorithm_info()
        self._clear_algorithm_state()
        self._show_success(message)

    def _rebuild_graph(
        self,
        number_of_vertices: int,
        directed: bool,
        weighted: bool,
        edges: list[tuple[int, int, float]]
    ) -> Graph:
        graph = Graph(directed=directed, weighted=weighted)

        for vertex_id in range(1, number_of_vertices + 1):
            graph.add_vertex(vertex_id)

        for source, target, weight in edges:
            graph.add_edge(source, target, weight)

        return graph
    
    def _edge_exists(self, source: int, target: int) -> bool:
        if self.current_graph is None:
            return False

        for edge in self.current_graph.get_edges():
            if self.current_graph.directed:
                if edge.source == source and edge.target == target:
                    return True
            else:
                same_direction = edge.source == source and edge.target == target
                reverse_direction = edge.source == target and edge.target == source

                if same_direction or reverse_direction:
                    return True

        return False
    
    def _add_vertex(self) -> None:
        if not self._ensure_current_graph():
            return

        vertices = sorted([vertex.id for vertex in self.current_graph.get_vertices()])

        if not vertices:
            new_vertex_id = 1
        else:
            new_vertex_id = max(vertices) + 1

        self.current_graph.add_vertex(new_vertex_id)

        self.control_panel.set_edit_vertex_value(new_vertex_id)

        self._refresh_after_graph_edit(
            f"Vertex {new_vertex_id} added."
        )

    def _remove_vertex_from_input(self) -> None:
        vertex_id = self.control_panel.get_edit_vertex_id()
        self._remove_vertex_by_id(vertex_id)


    def _remove_vertex_by_id(self, vertex_id: int) -> None:
        if not self._ensure_current_graph():
            return

        if not self.current_graph.has_vertex(vertex_id):
            self._show_warning(f"Vertex {vertex_id} does not exist.")
            return

        vertices = sorted([vertex.id for vertex in self.current_graph.get_vertices()])

        if len(vertices) == 1:
            self.current_graph = None
            self.control_panel.set_graph_text("")
            self.graph_view.scene.clear()
            self.graph_info_text.clear()
            self._clear_algorithm_state()
            self._show_success("Last vertex removed. Graph is now empty.")
            return

        remaining_vertices = [
            old_id for old_id in vertices
            if old_id != vertex_id
        ]

        mapping = {
            old_id: new_id
            for new_id, old_id in enumerate(remaining_vertices, start=1)
        }

        new_edges = []

        for edge in self.current_graph.get_edges():
            if edge.source == vertex_id or edge.target == vertex_id:
                continue

            new_edges.append(
                (
                    mapping[edge.source],
                    mapping[edge.target],
                    edge.weight
                )
            )

        self.current_graph = self._rebuild_graph(
            number_of_vertices=len(remaining_vertices),
            directed=self.current_graph.directed,
            weighted=self.current_graph.weighted,
            edges=new_edges
        )

        self.graph_view.vertex_positions.clear()

        self._refresh_after_graph_edit(
            f"Vertex {vertex_id} removed. Vertices were re-indexed."
        )

    def _add_edge(self) -> None:
        if not self._ensure_current_graph():
            return

        source = self.control_panel.get_edge_source()
        target = self.control_panel.get_edge_target()
        weight = self.control_panel.get_edge_weight()

        if not self.current_graph.has_vertex(source):
            self._show_warning(f"Source vertex {source} does not exist.")
            return

        if not self.current_graph.has_vertex(target):
            self._show_warning(f"Target vertex {target} does not exist.")
            return

        if self._edge_exists(source, target):
            self._show_warning(f"Edge {source} -> {target} already exists.")
            return

        if not self.current_graph.weighted:
            weight = 1

        self.current_graph.add_edge(source, target, weight)

        self._refresh_after_graph_edit(
            f"Edge {source} -> {target} added."
        )

    def _remove_edge(self) -> None:
        if not self._ensure_current_graph():
            return

        source = self.control_panel.get_edge_source()
        target = self.control_panel.get_edge_target()

        old_edges = self.current_graph.get_edges()

        new_edges = []

        removed = False

        for edge in old_edges:
            if self.current_graph.directed:
                is_target_edge = edge.source == source and edge.target == target
            else:
                same_direction = edge.source == source and edge.target == target
                reverse_direction = edge.source == target and edge.target == source
                is_target_edge = same_direction or reverse_direction

            if is_target_edge:
                removed = True
                continue

            new_edges.append(
                (
                    edge.source,
                    edge.target,
                    edge.weight
                )
            )

        if not removed:
            self._show_warning(f"Edge {source} -> {target} does not exist.")
            return

        number_of_vertices = self.current_graph.number_of_vertices()

        self.current_graph = self._rebuild_graph(
            number_of_vertices=number_of_vertices,
            directed=self.current_graph.directed,
            weighted=self.current_graph.weighted,
            edges=new_edges
        )

        self._refresh_after_graph_edit(
            f"Edge {source} -> {target} removed."
        )

    def _handle_vertex_clicked(self, vertex_id: int) -> None:
        click_mode = self.control_panel.get_click_mode()

        if click_mode == "Set Start":
            self._set_start_vertex_from_graph(vertex_id)
        elif click_mode == "Set Target":
            self._set_target_vertex_from_graph(vertex_id)
        else:
            self.control_panel.set_edit_vertex_value(vertex_id)
            self._set_status(
                f"Vertex {vertex_id} selected.",
                "info",
                timeout_ms=2000
            )

    def _set_start_vertex_from_graph(self, vertex_id: int) -> None:
        self.control_panel.set_start_vertex_value(vertex_id)
        self.control_panel.set_edge_source_value(vertex_id)

        self._set_status(
            f"Start vertex set to {vertex_id}.",
            "success",
            timeout_ms=3000
        )


    def _set_target_vertex_from_graph(self, vertex_id: int) -> None:
        self.control_panel.set_target_vertex_value(vertex_id)
        self.control_panel.set_edge_target_value(vertex_id)

        self._set_status(
            f"Target vertex set to {vertex_id}.",
            "success",
            timeout_ms=3000
        )