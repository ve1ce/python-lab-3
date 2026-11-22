import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QFrame, QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget,
    QVBoxLayout, QWidget,
)

from app.database import ActivityRepository, VocabularyRepository, initialize_database
from app.services import ActivityLog, VocabularyService
from app.ui.dashboard import DashboardPage
from app.ui.history import HistoryPage
from app.ui.practice import PracticePage
from app.ui.vocabulary import VocabularyPage
from app.ui.widgets import button, label

STYLE_PATH = Path(__file__).resolve().parent / "app" / "ui" / "styles.qss"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #базовые параметры окна
        self.setWindowTitle("Изучение иностранных языков")
        self.resize(1100, 700)
        self.setMinimumSize(850, 550)

        #зависимости
        activity_log = ActivityLog(ActivityRepository())
        vocabulary_service = VocabularyService(VocabularyRepository())

        #создание интерфейса и подгрузка стилей
        self.setup_ui(activity_log, vocabulary_service)
        self.setup_menu()
        self.setStyleSheet(STYLE_PATH.read_text(encoding="utf-8"))

    '''главное окно'''
    def setup_ui(self, activity_log, vocabulary_service):
        #центральный виджет + горизонтальная компановка элементов
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 20)
        sidebar_layout.setSpacing(8)
        sidebar_layout.addWidget(label("Изучение языков", "appTitle"))
        sidebar_layout.addSpacing(30)

        #создание страниц
        self.nav_group = QButtonGroup(self)
        self.pages = QStackedWidget()
        vocabulary_page = VocabularyPage(activity_log, vocabulary_service)
        get_words = vocabulary_service.get_words
        sections = [
            ("Главная", DashboardPage(activity_log)),
            ("Словарь", vocabulary_page),
            ("Практика", PracticePage(get_words, activity_log)),
            ("История", HistoryPage(activity_log)),
        ]
        #кнопки навигации
        for index, (title, page) in enumerate(sections):
            nav_button = button(title, "navButton", 42)
            nav_button.setCheckable(True)
            self.nav_group.addButton(nav_button, index)
            sidebar_layout.addWidget(nav_button)
            self.pages.addWidget(page)

        self.refresh_pages = (
            sections[0][1].refresh_dashboard, vocabulary_page.refresh_table,
            sections[2][1].refresh_levels, sections[3][1].refresh_table,
        )
        self.nav_group.button(0).setChecked(True)
        self.nav_group.idClicked.connect(self.select_page)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(label("Лабораторная работа №3", "footer"))
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages, 1)
        self.setCentralWidget(central_widget)

    '''переключение страниц'''
    def select_page(self, index):
        self.refresh_pages[index]()
        self.pages.setCurrentIndex(index)

    '''меню приложения(врехняя строчка)'''
    def setup_menu(self):
        file_menu = self.menuBar().addMenu("Файл")
        exit_action = file_menu.addAction("Выход")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        help_menu = self.menuBar().addMenu("Справка")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self.show_about)

    def show_about(self):
        QMessageBox.about(
            self,
            "О программе",
            "Приложение для изучения иностранных языков\n\n"
            "Лабораторная работа №3\n"
            "Работа с графическим интерфейсом на Python\n\n"
            "Технологии: Python, PySide6, Matplotlib.\n\n"
            "Версия: 1.0",
        )

'''точка входа'''
if __name__ == "__main__":
    initialize_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
