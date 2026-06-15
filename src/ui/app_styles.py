def get_stylesheet(theme_name: str) -> str:
    key = theme_name.lower().strip()

    if key == "dark":
        return get_dark_stylesheet()

    return get_light_stylesheet()


def get_light_stylesheet() -> str:
    return """
    QMainWindow {
        background-color: #f4f6f7;
    }

    QWidget {
        font-family: Arial;
        font-size: 13px;
        color: #1f2d3d;
    }

    QGroupBox {
        border: 1px solid #bfc9ca;
        border-radius: 8px;
        margin-top: 10px;
        padding: 8px;
        background-color: #ffffff;
        font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        color: #1f618d;
    }

    QTextEdit, QLineEdit, QComboBox, QSpinBox {
        background-color: #ffffff;
        border: 1px solid #aab7b8;
        border-radius: 5px;
        padding: 5px;
        color: #1f2d3d;
    }

    QTextEdit:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border: 1px solid #2980b9;
    }

    QPushButton {
        background-color: #2980b9;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 7px 10px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #3498db;
    }

    QPushButton:pressed {
        background-color: #1f618d;
    }

    QPushButton:disabled {
        background-color: #bdc3c7;
        color: #7f8c8d;
    }

    QLabel {
        color: #1f2d3d;
    }

    QCheckBox {
        spacing: 6px;
    }

    QStatusBar {
        background-color: #ecf0f1;
        border-top: 1px solid #bfc9ca;
    }

    QSplitter::handle {
        background-color: #d5dbdb;
    }
    """


def get_dark_stylesheet() -> str:
    return """
    QMainWindow {
        background-color: #1e1e1e;
    }

    QWidget {
        font-family: Arial;
        font-size: 13px;
        color: #ecf0f1;
    }

    QGroupBox {
        border: 1px solid #566573;
        border-radius: 8px;
        margin-top: 10px;
        padding: 8px;
        background-color: #2c3e50;
        font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
        color: #85c1e9;
    }

    QTextEdit, QLineEdit, QComboBox, QSpinBox {
        background-color: #17202a;
        border: 1px solid #566573;
        border-radius: 5px;
        padding: 5px;
        color: #ecf0f1;
        selection-background-color: #2980b9;
    }

    QTextEdit:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border: 1px solid #5dade2;
    }

    QPushButton {
        background-color: #2471a3;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 7px 10px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #2e86c1;
    }

    QPushButton:pressed {
        background-color: #1b4f72;
    }

    QPushButton:disabled {
        background-color: #566573;
        color: #aab7b8;
    }

    QLabel {
        color: #ecf0f1;
    }

    QCheckBox {
        spacing: 6px;
        color: #ecf0f1;
    }

    QStatusBar {
        background-color: #17202a;
        border-top: 1px solid #566573;
        color: #ecf0f1;
    }

    QSplitter::handle {
        background-color: #566573;
    }
    """