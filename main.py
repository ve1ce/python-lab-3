import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Изучение иностранных языков")
        self.resize(1000, 650)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Приложение для изучения языков")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.info_label = QLabel("Добро пожаловать!")

        button = QPushButton("Начать обучение")
        button.clicked.connect(self.on_button_click)

        layout.addWidget(title)
        layout.addWidget(self.info_label)
        layout.addWidget(button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_button_click(self):
        self.info_label.setText("Обучение скоро начнётся!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())