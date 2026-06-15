from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QSpinBox
)

class ControlPanel(QWidget):
    run_requested = Signal()
    load_sample_requested = Signal()
    load_file_requested = Signal()
    save_file_requested = Signal()
    clear_requested = Signal()
    generate_random_requested = Signal()
    export_result_requested = Signal()
    export_image_requested = Signal()
    algorithm_changed = Signal(str)
    theme_changed = Signal(str)

    previous_step_requested = Signal()
    next_step_requested = Signal()
    reset_step_requested = Signal()
    show_result_requested = Signal()

    auto_run_requested = Signal()
    pause_requested = Signal()
    reset_layout_requested = Signal()

    zoom_in_requested = Signal()
    zoom_out_requested = Signal()
    reset_zoom_requested = Signal()
    fit_view_requested = Signal()
    apply_layout_requested = Signal(str)

    add_vertex_requested = Signal()
    remove_vertex_requested = Signal()
    add_edge_requested = Signal()
    remove_edge_requested = Signal()

    def __init__(self):
        super().__init__()

        self.graph_input = QTextEdit()
        self.graph_input.setPlaceholderText(
            "Nhập đồ thị theo format:\n"
            "n m directed/undirected weighted/unweighted\n"
            "u v [w]\n"
            "u v [w]"
        )
        self.graph_input.setMinimumHeight(220)

        self.algorithm_combo = QComboBox()
        self.algorithm_info_text = QTextEdit()
        self.algorithm_info_text.setReadOnly(True)
        self.algorithm_info_text.setMaximumHeight(180)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText("Light")

        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Circle","Grid","Random","Force-directed",])

        '''
        self.algorithm_combo.addItems([
            "bfs",
            "dfs",
            "dijkstra",
            "bellman_ford",
            "floyd_warshall",
            "prim",
            "kruskal",
            "topo",
        ])
        '''
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Ví dụ: 1")

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Có thể bỏ trống")

        self.load_sample_button = QPushButton("Load Sample")
        self.load_file_button = QPushButton("Load File")
        self.save_file_button = QPushButton("Save File")
        self.run_button = QPushButton("Run Algorithm")
        self.export_result_button = QPushButton("Export Result")
        self.export_image_button = QPushButton("Export Image")
        self.clear_button = QPushButton("Clear")
        self.reset_layout_button = QPushButton("Reset Layout")

        self.vertex_count_input = QSpinBox()
        self.vertex_count_input.setRange(1, 100)
        self.vertex_count_input.setValue(6)

        self.edge_count_input = QSpinBox()
        self.edge_count_input.setRange(0, 1000)
        self.edge_count_input.setValue(8)

        self.directed_checkbox = QCheckBox("Directed")
        self.weighted_checkbox = QCheckBox("Weighted")
        self.weighted_checkbox.setChecked(True)

        self.min_weight_input = QSpinBox()
        self.min_weight_input.setRange(-100, 100)
        self.min_weight_input.setValue(1)

        self.max_weight_input = QSpinBox()
        self.max_weight_input.setRange(-100, 100)
        self.max_weight_input.setValue(10)

        self.allow_negative_checkbox = QCheckBox("Allow negative weight")
        self.generate_random_button = QPushButton("Generate Random Graph")

        self.previous_step_button = QPushButton("Previous Step")
        self.next_step_button = QPushButton("Next Step")
        self.reset_step_button = QPushButton("Reset Step")
        self.show_result_button = QPushButton("Show Result")
        self.auto_run_button = QPushButton("Auto Run")
        self.pause_button = QPushButton("Pause")

        self.apply_layout_button = QPushButton("Apply Layout")
        self.fit_view_button = QPushButton("Fit View")
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_out_button = QPushButton("Zoom Out")
        self.reset_zoom_button = QPushButton("Reset Zoom")

        self.speed_input = QSpinBox()
        self.speed_input.setRange(100, 3000)
        self.speed_input.setSingleStep(100)
        self.speed_input.setValue(800)
        self.speed_input.setSuffix(" ms")

        self.step_info_label = QLabel("Step: none")

        self.edit_vertex_input = QSpinBox()
        self.edit_vertex_input.setRange(1, 10000)
        self.edit_vertex_input.setValue(1)

        self.edge_source_input = QSpinBox()
        self.edge_source_input.setRange(1, 10000)
        self.edge_source_input.setValue(1)

        self.edge_target_input = QSpinBox()
        self.edge_target_input.setRange(1, 10000)
        self.edge_target_input.setValue(2)

        self.edge_weight_input = QSpinBox()
        self.edge_weight_input.setRange(-100000, 100000)
        self.edge_weight_input.setValue(1)

        self.add_vertex_button = QPushButton("Add Vertex")
        self.remove_vertex_button = QPushButton("Remove Vertex")
        self.add_edge_button = QPushButton("Add Edge")
        self.remove_edge_button = QPushButton("Remove Edge")

        self.click_mode_combo = QComboBox()
        self.click_mode_combo.addItems([
            "None",
            "Set Start",
            "Set Target",
        ])

        self._setup_ui()
        self._connect_signals()
        self._update_parameter_fields(self.algorithm_combo.currentText())

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        graph_group = QGroupBox("Graph Input")
        graph_layout = QVBoxLayout(graph_group)
        graph_layout.addWidget(QLabel("Dữ liệu đồ thị:"))
        graph_layout.addWidget(self.graph_input)

        random_group = QGroupBox("Random Graph")
        random_layout = QFormLayout(random_group)

        random_layout.addRow("Number of vertices:", self.vertex_count_input)
        random_layout.addRow("Number of edges:", self.edge_count_input)
        random_layout.addRow("", self.directed_checkbox)
        random_layout.addRow("", self.weighted_checkbox)
        random_layout.addRow("Min weight:", self.min_weight_input)
        random_layout.addRow("Max weight:", self.max_weight_input)
        random_layout.addRow("", self.allow_negative_checkbox)
        random_layout.addRow(self.generate_random_button)

        file_button_layout = QHBoxLayout()
        file_button_layout.addWidget(self.load_sample_button)
        file_button_layout.addWidget(self.load_file_button)
        file_button_layout.addWidget(self.save_file_button)
        file_button_layout.addWidget(self.clear_button)
        file_button_layout.addWidget(self.reset_layout_button)

        graph_layout.addLayout(file_button_layout)

        algorithm_group = QGroupBox("Algorithm")
        form_layout = QFormLayout(algorithm_group)
        form_layout.addRow("Thuật toán:", self.algorithm_combo)
        form_layout.addRow("Start vertex:", self.start_input)
        form_layout.addRow("Target vertex:", self.target_input)

        #algorithm_info_group = QGroupBox("Algorithm Information")
        #algorithm_info_layout = QVBoxLayout(algorithm_info_group)
        #algorithm_info_layout.addWidget(self.algorithm_info_text)
        '''
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        theme_layout.addRow("Theme:", self.theme_combo)
        '''
        #graph_view_group = QGroupBox("Graph View")
        #graph_view_layout = QVBoxLayout(graph_view_group)

        graph_editor_group = QGroupBox("Graph Editor")
        graph_editor_layout = QVBoxLayout(graph_editor_group)

        vertex_form = QFormLayout()
        vertex_form.addRow("Vertex ID:", self.edit_vertex_input)

        vertex_button_row = QHBoxLayout()
        vertex_button_row.addWidget(self.add_vertex_button)
        vertex_button_row.addWidget(self.remove_vertex_button)

        edge_form = QFormLayout()
        edge_form.addRow("Source:", self.edge_source_input)
        edge_form.addRow("Target:", self.edge_target_input)
        edge_form.addRow("Weight:", self.edge_weight_input)

        edge_button_row = QHBoxLayout()
        edge_button_row.addWidget(self.add_edge_button)
        edge_button_row.addWidget(self.remove_edge_button)

        click_form = QFormLayout()
        click_form.addRow("Click Mode:", self.click_mode_combo)

        graph_editor_layout.addLayout(vertex_form)
        graph_editor_layout.addLayout(vertex_button_row)
        graph_editor_layout.addLayout(edge_form)
        graph_editor_layout.addLayout(edge_button_row)
        graph_editor_layout.addLayout(click_form)

        layout_row = QHBoxLayout()
        layout_row.addWidget(QLabel("Layout:"))
        layout_row.addWidget(self.layout_combo)
        layout_row.addWidget(self.apply_layout_button)

        zoom_row_1 = QHBoxLayout()
        zoom_row_1.addWidget(self.zoom_in_button)
        zoom_row_1.addWidget(self.zoom_out_button)

        zoom_row_2 = QHBoxLayout()
        zoom_row_2.addWidget(self.fit_view_button)
        zoom_row_2.addWidget(self.reset_zoom_button)

        #graph_view_layout.addLayout(layout_row)
        #graph_view_layout.addLayout(zoom_row_1)
        #graph_view_layout.addLayout(zoom_row_2)

        debug_group = QGroupBox("Debug Step")
        debug_layout = QVBoxLayout(debug_group)

        debug_button_layout_1 = QHBoxLayout()
        debug_button_layout_1.addWidget(self.previous_step_button)
        debug_button_layout_1.addWidget(self.next_step_button)

        debug_button_layout_2 = QHBoxLayout()
        debug_button_layout_2.addWidget(self.reset_step_button)
        debug_button_layout_2.addWidget(self.show_result_button)

        debug_button_layout_3 = QHBoxLayout()
        debug_button_layout_3.addWidget(self.auto_run_button)
        debug_button_layout_3.addWidget(self.pause_button)

        debug_layout.addWidget(self.step_info_label)
        debug_layout.addLayout(debug_button_layout_1)
        debug_layout.addLayout(debug_button_layout_2)
        debug_layout.addLayout(debug_button_layout_3)

        debug_layout.addWidget(QLabel("Speed:"))
        debug_layout.addWidget(self.speed_input)

        main_layout.addWidget(graph_group)
        main_layout.addWidget(random_group)
        main_layout.addWidget(algorithm_group)
        main_layout.addWidget(self.export_result_button)
        main_layout.addWidget(self.export_image_button)
        #main_layout.addWidget(algorithm_info_group)
        #main_layout.addWidget(theme_group)
        #main_layout.addWidget(graph_view_group)
        main_layout.addWidget(graph_editor_group)
        main_layout.addWidget(self.run_button)
        main_layout.addWidget(debug_group)
        main_layout.addStretch()

    def _connect_signals(self) -> None:
        self.run_button.clicked.connect(self.run_requested.emit)
        self.export_result_button.clicked.connect(self.export_result_requested.emit)
        self.export_image_button.clicked.connect(self.export_image_requested.emit)
        self.load_sample_button.clicked.connect(self.load_sample_requested.emit)
        self.load_file_button.clicked.connect(self.load_file_requested.emit)
        self.save_file_button.clicked.connect(self.save_file_requested.emit)
        self.generate_random_button.clicked.connect(self.generate_random_requested.emit)
        self.clear_button.clicked.connect(self.clear_requested.emit)
        self.reset_layout_button.clicked.connect(self.reset_layout_requested.emit)

        self.add_vertex_button.clicked.connect(self.add_vertex_requested.emit)
        self.remove_vertex_button.clicked.connect(self.remove_vertex_requested.emit)
        self.add_edge_button.clicked.connect(self.add_edge_requested.emit)
        self.remove_edge_button.clicked.connect(self.remove_edge_requested.emit)

        self.zoom_in_button.clicked.connect(self.zoom_in_requested.emit)
        self.zoom_out_button.clicked.connect(self.zoom_out_requested.emit)
        self.reset_zoom_button.clicked.connect(self.reset_zoom_requested.emit)
        self.fit_view_button.clicked.connect(self.fit_view_requested.emit)

        self.apply_layout_button.clicked.connect(
            lambda: self.apply_layout_requested.emit(self.layout_combo.currentText())
        )

        self.previous_step_button.clicked.connect(self.previous_step_requested.emit)
        self.next_step_button.clicked.connect(self.next_step_requested.emit)
        self.reset_step_button.clicked.connect(self.reset_step_requested.emit)
        self.show_result_button.clicked.connect(self.show_result_requested.emit)
        self.auto_run_button.clicked.connect(self.auto_run_requested.emit)
        self.pause_button.clicked.connect(self.pause_requested.emit)

        self.algorithm_combo.currentTextChanged.connect(self._on_algorithm_changed)
        self.theme_combo.currentTextChanged.connect(self.theme_changed.emit)

    def _update_parameter_fields(self, algorithm_name: str) -> None:
        key = algorithm_name.lower().strip()

        self.start_input.setEnabled(True)
        self.target_input.setEnabled(True)

        self.start_input.setPlaceholderText("Ví dụ: 1")
        self.target_input.setPlaceholderText("Có thể bỏ trống")

        if key in ["bfs", "dfs", "dijkstra", "bellman_ford"]:
            self.start_input.setEnabled(True)
            self.target_input.setEnabled(True)
            self.start_input.setPlaceholderText("Bắt buộc")
            self.target_input.setPlaceholderText("Có thể bỏ trống")

        elif key == "prim":
            self.start_input.setEnabled(True)
            self.target_input.setEnabled(False)
            self.target_input.clear()
            self.start_input.setPlaceholderText("Có thể bỏ trống")

        elif key in ["kruskal", "topo", "topological_sort", "topological", "toposort"]:
            self.start_input.setEnabled(False)
            self.target_input.setEnabled(False)
            self.start_input.clear()
            self.target_input.clear()

        elif key in ["floyd_warshall", "floyd-warshall", "floyd"]:
            self.start_input.setEnabled(True)
            self.target_input.setEnabled(True)
            self.start_input.setPlaceholderText("Có thể bỏ trống")
            self.target_input.setPlaceholderText("Có thể bỏ trống")

    def get_graph_text(self) -> str:
        return self.graph_input.toPlainText()

    def set_graph_text(self, text: str) -> None:
        self.graph_input.setPlainText(text)

    def get_algorithm_name(self) -> str:
        return self.algorithm_combo.currentText().strip().lower()

    def get_start_vertex(self) -> int | None:
        if not self.start_input.isEnabled():
            return None

        text = self.start_input.text().strip()

        if text == "":
            return None

        return int(text)

    def get_target_vertex(self) -> int | None:
        if not self.target_input.isEnabled():
            return None

        text = self.target_input.text().strip()

        if text == "":
            return None

        return int(text)

    def set_step_info(self, current_step: int, total_steps: int) -> None:
        if total_steps <= 0:
            self.step_info_label.setText("Step: none")
        else:
            self.step_info_label.setText(f"Step: {current_step}/{total_steps}")

    def clear_all(self) -> None:
        self.graph_input.clear()
        self.start_input.clear()
        self.target_input.clear()
        self.set_step_info(0, 0)

    def get_speed_ms(self) -> int:
        return self.speed_input.value()
    
    def get_random_vertex_count(self) -> int:
        return self.vertex_count_input.value()
    
    def get_random_edge_count(self) -> int:
        return self.edge_count_input.value()

    def is_random_directed(self) -> bool:
        return self.directed_checkbox.isChecked()

    def is_random_weighted(self) -> bool:
        return self.weighted_checkbox.isChecked()

    def get_random_min_weight(self) -> int:
        return self.min_weight_input.value()

    def get_random_max_weight(self) -> int:
        return self.max_weight_input.value()

    def is_random_negative_allowed(self) -> bool:
        return self.allow_negative_checkbox.isChecked()   

    def _on_algorithm_changed(self, algorithm_name: str) -> None:
        self._update_parameter_fields(algorithm_name)
        self.algorithm_changed.emit(algorithm_name)   

    def set_algorithm_items(self, algorithm_names: list[str]) -> None:
        self.algorithm_combo.clear()
        self.algorithm_combo.addItems(algorithm_names)

        if algorithm_names:
            self.algorithm_combo.setCurrentIndex(0)
            self._update_parameter_fields(algorithm_names[0])
            self.algorithm_changed.emit(algorithm_names[0])


    def set_algorithm_info(self, text: str) -> None:
        self.algorithm_info_text.setPlainText(text)
    
    def get_theme_name(self) -> str:
        return self.theme_combo.currentText()

    def set_theme_name(self, theme_name: str) -> None:
        index = self.theme_combo.findText(theme_name)

        if index >= 0:
            old_state = self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentIndex(index)
            self.theme_combo.blockSignals(old_state)


    def set_speed_ms(self, speed_ms: int) -> None:
        old_state = self.speed_input.blockSignals(True)
        self.speed_input.setValue(speed_ms)
        self.speed_input.blockSignals(old_state)

    def get_layout_name(self) -> str:
        return self.layout_combo.currentText()
    
    def get_edit_vertex_id(self) -> int:
        return self.edit_vertex_input.value()


    def get_edge_source(self) -> int:
        return self.edge_source_input.value()


    def get_edge_target(self) -> int:
        return self.edge_target_input.value()


    def get_edge_weight(self) -> int:
        return self.edge_weight_input.value()


    def get_click_mode(self) -> str:
        return self.click_mode_combo.currentText()


    def set_start_vertex_value(self, vertex_id: int) -> None:
        self.start_input.setText(str(vertex_id))


    def set_target_vertex_value(self, vertex_id: int) -> None:
        self.target_input.setText(str(vertex_id))


    def set_edit_vertex_value(self, vertex_id: int) -> None:
        self.edit_vertex_input.setValue(vertex_id)


    def set_edge_source_value(self, vertex_id: int) -> None:
        self.edge_source_input.setValue(vertex_id)


    def set_edge_target_value(self, vertex_id: int) -> None:
        self.edge_target_input.setValue(vertex_id)