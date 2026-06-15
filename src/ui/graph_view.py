import math
import random
from typing import Iterable, Tuple

from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QMenu,
)

from src.model.graph import Graph


class DraggableVertexItem(QGraphicsEllipseItem):
    """
    Đỉnh có thể kéo thả.

    Đỉnh gồm:
    - hình tròn
    - nhãn số đỉnh nằm bên trong
    """

    def __init__(
        self,
        vertex_id: int,
        x: float,
        y: float,
        radius: float,
        graph_view
    ):
        super().__init__(
            -radius,
            -radius,
            2 * radius,
            2 * radius
        )

        self.vertex_id = vertex_id
        self.radius = radius
        self.graph_view = graph_view

        self.setPos(x, y)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        self.setZValue(2)

        self.label_item = QGraphicsTextItem(str(vertex_id), self)
        self.label_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.label_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.label_item.setDefaultTextColor(QColor("#000000"))


        rect = self.label_item.boundingRect()
        self.label_item.setPos(
            -rect.width() / 2,
            -rect.height() / 2
        )

        self.label_item.setZValue(3)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if not self.graph_view.is_redrawing:
                position = self.pos()
                self.graph_view.vertex_positions[self.vertex_id] = (
                    position.x(),
                    position.y()
                )

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        position = self.pos()
        self.graph_view.on_vertex_moved(
            self.vertex_id,
            position.x(),
            position.y()
        )
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.graph_view.vertex_clicked.emit(self.vertex_id)

        super().mousePressEvent(event)


    def contextMenuEvent(self, event):
        self.graph_view.show_vertex_context_menu(
            self.vertex_id,
            event.screenPos()
        )

class GraphView(QGraphicsView):
    vertex_clicked = Signal(int)
    set_start_requested = Signal(int)
    set_target_requested = Signal(int)
    remove_vertex_requested = Signal(int)
    """
    Vùng hiển thị đồ thị.

    Chức năng:
    - Vẽ đỉnh
    - Vẽ cạnh thẳng
    - Vẽ cạnh cong khi có hai cạnh ngược chiều
    - Vẽ self-loop
    - Vẽ mũi tên cho đồ thị có hướng
    - Vẽ trọng số
    - Highlight đường đi / cây khung
    - Kéo thả đỉnh
    - Zoom / Pan
    - Nhiều layout: Circle, Grid, Random, Force-directed
    """

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setMinimumSize(600, 420)
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #bfc9ca;")

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        self.vertex_radius = 22

        self.vertex_positions: dict[int, tuple[float, float]] = {}

        self.current_graph: Graph | None = None
        self.current_highlighted_vertices: set[int] = set()
        self.current_highlighted_edges: set[Tuple[int, int]] = set()

        self.is_redrawing = False

    def draw_graph(
        self,
        graph: Graph,
        highlighted_vertices: Iterable[int] | None = None,
        highlighted_edges: Iterable[Tuple[int, int]] | None = None,
    ) -> None:
        old_vertices = set(self.vertex_positions.keys())

        self.current_graph = graph
        self.current_highlighted_vertices = set(highlighted_vertices or [])
        self.current_highlighted_edges = set(highlighted_edges or [])

        if graph is None:
            self.scene.clear()
            return

        new_vertices = set(vertex.id for vertex in graph.get_vertices())

        should_fit = old_vertices != new_vertices or not self.vertex_positions

        self._redraw(fit_view=should_fit)

    def _redraw(self, fit_view: bool = False) -> None:
        if self.current_graph is None:
            return

        graph = self.current_graph

        self.is_redrawing = True
        self.scene.clear()

        if graph.number_of_vertices() == 0:
            self.is_redrawing = False
            return

        self._ensure_vertex_positions(graph)

        self._draw_edges(graph, self.current_highlighted_edges)

        vertices = sorted([vertex.id for vertex in graph.get_vertices()])
        self._draw_vertices(vertices, self.current_highlighted_vertices)

        self.scene.setSceneRect(
            self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50)
        )

        self.is_redrawing = False

        if fit_view:
            self.fit_graph()

    def _ensure_vertex_positions(self, graph: Graph) -> None:
        vertices = sorted([vertex.id for vertex in graph.get_vertices()])

        valid_vertices = set(vertices)

        for vertex_id in list(self.vertex_positions.keys()):
            if vertex_id not in valid_vertices:
                del self.vertex_positions[vertex_id]

        if not vertices:
            return

        missing_vertices = [
            vertex_id for vertex_id in vertices
            if vertex_id not in self.vertex_positions
        ]

        if not missing_vertices:
            return

        n = len(vertices)
        center_x = 320
        center_y = 210
        radius = 160 if n <= 10 else 220

        if n == 1:
            self.vertex_positions[vertices[0]] = (center_x, center_y)
            return

        for index, vertex_id in enumerate(vertices):
            if vertex_id in self.vertex_positions:
                continue

            angle = 2 * math.pi * index / n

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            self.vertex_positions[vertex_id] = (x, y)

    def on_vertex_moved(self, vertex_id: int, x: float, y: float) -> None:
        if self.is_redrawing:
            return

        self.vertex_positions[vertex_id] = (x, y)
        self._redraw(fit_view=False)

    def reset_layout(self) -> None:
        self.apply_layout("Circle")

    def apply_layout(self, layout_name: str) -> None:
        if self.current_graph is None:
            return

        key = layout_name.lower().strip()

        if key == "circle":
            self._apply_circle_layout()
        elif key == "grid":
            self._apply_grid_layout()
        elif key == "random":
            self._apply_random_layout()
        elif key in ["force-directed", "force directed", "force"]:
            self._apply_force_directed_layout()
        else:
            self._apply_circle_layout()

        self._redraw(fit_view=True)

    def _apply_circle_layout(self) -> None:
        graph = self.current_graph

        if graph is None:
            return

        vertices = sorted([vertex.id for vertex in graph.get_vertices()])
        n = len(vertices)

        if n == 0:
            return

        center_x = 320
        center_y = 210
        radius = 160 if n <= 10 else 230

        self.vertex_positions.clear()

        if n == 1:
            self.vertex_positions[vertices[0]] = (center_x, center_y)
            return

        for index, vertex_id in enumerate(vertices):
            angle = 2 * math.pi * index / n

            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            self.vertex_positions[vertex_id] = (x, y)

    def _apply_grid_layout(self) -> None:
        graph = self.current_graph

        if graph is None:
            return

        vertices = sorted([vertex.id for vertex in graph.get_vertices()])
        n = len(vertices)

        if n == 0:
            return

        columns = math.ceil(math.sqrt(n))

        start_x = 120
        start_y = 80
        gap_x = 120
        gap_y = 100

        self.vertex_positions.clear()

        for index, vertex_id in enumerate(vertices):
            row = index // columns
            col = index % columns

            x = start_x + col * gap_x
            y = start_y + row * gap_y

            self.vertex_positions[vertex_id] = (x, y)

    def _apply_random_layout(self) -> None:
        graph = self.current_graph

        if graph is None:
            return

        vertices = sorted([vertex.id for vertex in graph.get_vertices()])

        self.vertex_positions.clear()

        for vertex_id in vertices:
            x = random.randint(80, 560)
            y = random.randint(60, 380)

            self.vertex_positions[vertex_id] = (x, y)

    def _apply_force_directed_layout(self) -> None:
        graph = self.current_graph

        if graph is None:
            return

        vertices = sorted([vertex.id for vertex in graph.get_vertices()])
        n = len(vertices)

        if n == 0:
            return

        width = 620
        height = 420
        area = width * height
        k = math.sqrt(area / n)

        if not self.vertex_positions or set(self.vertex_positions.keys()) != set(vertices):
            self._apply_random_layout()

        positions = {
            vertex_id: list(self.vertex_positions[vertex_id])
            for vertex_id in vertices
        }

        iterations = 120

        for iteration in range(iterations):
            displacement = {
                vertex_id: [0.0, 0.0]
                for vertex_id in vertices
            }

            # Lực đẩy giữa các cặp đỉnh.
            for i in range(n):
                v = vertices[i]

                for j in range(i + 1, n):
                    u = vertices[j]

                    dx = positions[v][0] - positions[u][0]
                    dy = positions[v][1] - positions[u][1]

                    distance = math.sqrt(dx * dx + dy * dy) + 0.01

                    force = k * k / distance

                    fx = dx / distance * force
                    fy = dy / distance * force

                    displacement[v][0] += fx
                    displacement[v][1] += fy

                    displacement[u][0] -= fx
                    displacement[u][1] -= fy

            # Lực hút theo cạnh.
            for edge in graph.get_edges():
                v = edge.source
                u = edge.target

                if v not in positions or u not in positions:
                    continue

                dx = positions[v][0] - positions[u][0]
                dy = positions[v][1] - positions[u][1]

                distance = math.sqrt(dx * dx + dy * dy) + 0.01

                force = distance * distance / k

                fx = dx / distance * force
                fy = dy / distance * force

                displacement[v][0] -= fx
                displacement[v][1] -= fy

                displacement[u][0] += fx
                displacement[u][1] += fy

            temperature = width / 10 * (1 - iteration / iterations)

            for vertex_id in vertices:
                dx, dy = displacement[vertex_id]
                distance = math.sqrt(dx * dx + dy * dy) + 0.01

                positions[vertex_id][0] += dx / distance * min(distance, temperature)
                positions[vertex_id][1] += dy / distance * min(distance, temperature)

                positions[vertex_id][0] = min(width - 40, max(40, positions[vertex_id][0]))
                positions[vertex_id][1] = min(height - 40, max(40, positions[vertex_id][1]))

        self.vertex_positions = {
            vertex_id: (positions[vertex_id][0], positions[vertex_id][1])
            for vertex_id in vertices
        }

    def _draw_edges(
        self,
        graph: Graph,
        highlighted_edges: set[Tuple[int, int]]
    ) -> None:
        normal_pen = QPen(QColor("#555555"), 2)
        highlight_pen = QPen(QColor("#e74c3c"), 4)

        edge_pairs = {
            (edge.source, edge.target)
            for edge in graph.get_edges()
        }

        for edge in graph.get_edges():
            source = edge.source
            target = edge.target

            if source not in self.vertex_positions or target not in self.vertex_positions:
                continue

            is_highlighted = (source, target) in highlighted_edges

            if not graph.directed:
                is_highlighted = (
                    is_highlighted or
                    (target, source) in highlighted_edges
                )

            pen = highlight_pen if is_highlighted else normal_pen

            if source == target:
                path = self._create_self_loop_path(source)
                self.scene.addPath(path, pen)

                if graph.directed:
                    self._draw_arrow_on_path(path, pen, percent=0.85)

                if graph.weighted:
                    label_point = path.pointAtPercent(0.25)
                    self._draw_weight_label(edge.weight, label_point.x(), label_point.y())

                continue

            has_reverse_edge = graph.directed and (target, source) in edge_pairs

            if has_reverse_edge:
                curve_offset = 45 if source < target else -45
                path = self._create_curved_edge_path(source, target, curve_offset)
            else:
                path = self._create_straight_edge_path(source, target)

            self.scene.addPath(path, pen)

            if graph.directed:
                self._draw_arrow_on_path(path, pen)

            if graph.weighted:
                label_point = path.pointAtPercent(0.5)
                self._draw_weight_label(edge.weight, label_point.x(), label_point.y())

    def _create_straight_edge_path(self, source: int, target: int) -> QPainterPath:
        x1, y1 = self.vertex_positions[source]
        x2, y2 = self.vertex_positions[target]

        start_x, start_y, end_x, end_y = self._get_shortened_line(
            x1, y1, x2, y2
        )

        path = QPainterPath(QPointF(start_x, start_y))
        path.lineTo(QPointF(end_x, end_y))

        return path

    def _create_curved_edge_path(
        self,
        source: int,
        target: int,
        curve_offset: float
    ) -> QPainterPath:
        x1, y1 = self.vertex_positions[source]
        x2, y2 = self.vertex_positions[target]

        start_x, start_y, end_x, end_y = self._get_shortened_line(
            x1, y1, x2, y2
        )

        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2

        dx = end_x - start_x
        dy = end_y - start_y

        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            length = 1

        normal_x = -dy / length
        normal_y = dx / length

        control_x = mid_x + normal_x * curve_offset
        control_y = mid_y + normal_y * curve_offset

        path = QPainterPath(QPointF(start_x, start_y))
        path.quadTo(
            QPointF(control_x, control_y),
            QPointF(end_x, end_y)
        )

        return path

    def _create_self_loop_path(self, vertex_id: int) -> QPainterPath:
        x, y = self.vertex_positions[vertex_id]

        loop_width = 58
        loop_height = 46

        rect = QRectF(
            x + self.vertex_radius * 0.2,
            y - self.vertex_radius * 2.7,
            loop_width,
            loop_height
        )

        path = QPainterPath()
        path.addEllipse(rect)

        return path

    def _get_shortened_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float
    ) -> tuple[float, float, float, float]:
        dx = x2 - x1
        dy = y2 - y1

        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return x1, y1, x2, y2

        unit_x = dx / length
        unit_y = dy / length

        start_x = x1 + self.vertex_radius * unit_x
        start_y = y1 + self.vertex_radius * unit_y

        end_x = x2 - self.vertex_radius * unit_x
        end_y = y2 - self.vertex_radius * unit_y

        return start_x, start_y, end_x, end_y

    def _draw_arrow_on_path(
        self,
        path: QPainterPath,
        pen: QPen,
        percent: float = 1.0
    ) -> None:
        arrow_size = 14

        end_percent = max(0.01, min(1.0, percent))
        start_percent = max(0.0, end_percent - 0.04)

        start_point = path.pointAtPercent(start_percent)
        end_point = path.pointAtPercent(end_percent)

        angle = math.atan2(
            end_point.y() - start_point.y(),
            end_point.x() - start_point.x()
        )

        tip = QPointF(end_point.x(), end_point.y())

        left = QPointF(
            end_point.x() - arrow_size * math.cos(angle - math.pi / 6),
            end_point.y() - arrow_size * math.sin(angle - math.pi / 6)
        )

        right = QPointF(
            end_point.x() - arrow_size * math.cos(angle + math.pi / 6),
            end_point.y() - arrow_size * math.sin(angle + math.pi / 6)
        )

        arrow = QPolygonF([tip, left, right])

        brush = QBrush(pen.color())
        self.scene.addPolygon(arrow, pen, brush)

    def _draw_weight_label(
        self,
        weight: float,
        x: float,
        y: float
    ) -> None:
        weight_text = self._format_weight(weight)

        text_item = self.scene.addText(weight_text, QFont("Arial", 10))
        text_item.setDefaultTextColor(QColor("#000000"))

        rect = text_item.boundingRect()

        text_item.setPos(
            x - rect.width() / 2,
            y - rect.height() / 2
        )

        text_item.setZValue(4)

    def _draw_vertices(
        self,
        vertices: list[int],
        highlighted_vertices: set[int]
    ) -> None:
        normal_brush = QBrush(QColor("#d6eaf8"))
        highlight_brush = QBrush(QColor("#f9e79f"))
        border_pen = QPen(QColor("#1f618d"), 2)

        for vertex_id in vertices:
            x, y = self.vertex_positions[vertex_id]

            brush = highlight_brush if vertex_id in highlighted_vertices else normal_brush

            vertex_item = DraggableVertexItem(
                vertex_id=vertex_id,
                x=x,
                y=y,
                radius=self.vertex_radius,
                graph_view=self
            )

            vertex_item.setPen(border_pen)
            vertex_item.setBrush(brush)

            self.scene.addItem(vertex_item)

    def zoom_in(self) -> None:
        self.scale(1.2, 1.2)

    def zoom_out(self) -> None:
        self.scale(1 / 1.2, 1 / 1.2)

    def reset_zoom(self) -> None:
        self.resetTransform()

    def fit_graph(self) -> None:
        if self.scene.items():
            rect = self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50)
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event) -> None:
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

        event.accept()

    def export_to_png(self, file_path: str) -> None:
        if self.current_graph is None or self.current_graph.number_of_vertices() == 0:
            raise ValueError("Chưa có đồ thị để export ảnh.")

        scene_rect = self.scene.itemsBoundingRect()

        if scene_rect.isNull() or scene_rect.isEmpty():
            raise ValueError("Không có nội dung đồ thị để export ảnh.")

        margin = 40
        scene_rect = scene_rect.adjusted(
            -margin,
            -margin,
            margin,
            margin
        )

        image_width = max(1, int(scene_rect.width()))
        image_height = max(1, int(scene_rect.height()))

        image = QImage(
            image_width,
            image_height,
            QImage.Format.Format_ARGB32
        )

        image.fill(QColor("white"))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        target_rect = QRectF(0, 0, image_width, image_height)

        self.scene.render(
            painter,
            target_rect,
            scene_rect
        )

        painter.end()

        saved = image.save(file_path)

        if not saved:
            raise ValueError("Không thể lưu ảnh PNG.")

    def _format_weight(self, value: float) -> str:
        if float(value).is_integer():
            return str(int(value))

        return str(value)
    
    def show_vertex_context_menu(self, vertex_id: int, screen_pos) -> None:
        menu = QMenu()

        set_start_action = menu.addAction(f"Set {vertex_id} as Start Vertex")
        set_target_action = menu.addAction(f"Set {vertex_id} as Target Vertex")
        menu.addSeparator()
        remove_vertex_action = menu.addAction(f"Remove Vertex {vertex_id}")

        selected_action = menu.exec(screen_pos)

        if selected_action == set_start_action:
            self.set_start_requested.emit(vertex_id)
        elif selected_action == set_target_action:
            self.set_target_requested.emit(vertex_id)
        elif selected_action == remove_vertex_action:
            self.remove_vertex_requested.emit(vertex_id)
    
  