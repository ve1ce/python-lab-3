import sys
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.vocabulary import VocabularyPage

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QButtonGroup
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Изучение иностранных языков")
        self.resize(1100, 700)
        self.setMinimumSize(850, 550)

        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):

        # Центральный контейнер
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Боковая панель
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 20)
        sidebar_layout.setSpacing(8)

        # Название приложения
        app_title = QLabel("Изучение языков")
        app_title.setObjectName("appTitle")

        sidebar_layout.addWidget(app_title)
        sidebar_layout.addSpacing(30)

        # Группа кнопок навигации
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        # Контейнер страниц
        self.pages = QStackedWidget()

        # Список разделов
        sections = [
            ("Главная", "Добро пожаловать в приложение!"),
            ("Словарь", "Здесь будут ваши изучаемые слова."),
            ("Практика", "Здесь можно будет проходить упражнения."),
            ("История", "Здесь будет отображаться история активности.")
        ]

        for index, (title, description) in enumerate(sections):

            # Кнопка навигации
            button = QPushButton(title)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setMinimumHeight(42)

            self.nav_group.addButton(button, index)
            sidebar_layout.addWidget(button)

            # Страница раздела
            if index == 0:
                page = DashboardPage()

            elif index == 1:
                page = VocabularyPage()

            else:
                page = self.create_page(title, description)

            self.pages.addWidget(page)

            # Первая кнопка активна
            if index == 0:
                button.setChecked(True)

        # Обработчик переключения страниц
        self.nav_group.idClicked.connect(
            self.pages.setCurrentIndex
        )

        sidebar_layout.addStretch()

        # Подпись внизу боковой панели
        footer = QLabel("Лабораторная работа №3")
        footer.setObjectName("footer")

        sidebar_layout.addWidget(footer)

        # Добавляем элементы в главное окно
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages, 1)

        self.setCentralWidget(central_widget)

    def create_page(self, title, description):

        page = QWidget()
        page.setObjectName("page")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(12)

        # Заголовок страницы
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")

        # Описание страницы
        description_label = QLabel(description)
        description_label.setObjectName("pageDescription")

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()

        return page

    def setup_styles(self):

        self.setStyleSheet("""

            QWidget#centralWidget {
                background-color: #f5f6f8;
            }

            QWidget#page {
                background-color: #f5f6f8;
            }

            QFrame#sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e5e7eb;
            }

            QLabel#appTitle {
                font-size: 17px;
                font-weight: 600;
                color: #1f2937;
            }

            QPushButton#navButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 10px 14px;
                text-align: left;
                font-size: 14px;
                color: #4b5563;
            }

            QPushButton#navButton:hover {
                background-color: #f3f4f6;
            }

            QPushButton#navButton:checked {
                background-color: #e8eef7;
                color: #315b91;
                font-weight: 600;
            }

            QLabel#pageTitle {
                font-size: 26px;
                font-weight: 600;
                color: #1f2937;
            }

            QLabel#pageDescription {
                font-size: 14px;
                color: #6b7280;
            }

            QLabel#footer {
                font-size: 11px;
                color: #9ca3af;
            }

        """)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())