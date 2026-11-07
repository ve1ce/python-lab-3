from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("dashboardPage")

        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):

        # Основной контейнер
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Область с прокруткой
        scroll = QScrollArea()
        scroll.setObjectName("dashboardScroll")
        scroll.setWidgetResizable(True)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        outer_layout.addWidget(scroll)

        # Контейнер содержимого
        content = QWidget()
        content.setObjectName("dashboardContent")

        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(24)

        # Заголовок страницы
        title = QLabel("Главная")
        title.setObjectName("dashboardTitle")

        subtitle = QLabel(
            "Обзор прогресса · демонстрационные данные"
        )
        subtitle.setObjectName("mutedText")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Карточки статистики
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        stats_layout.addWidget(
            self.create_stat_card("Изучено слов", "248")
        )

        stats_layout.addWidget(
            self.create_stat_card("Упражнений", "36")
        )

        stats_layout.addWidget(
            self.create_stat_card("Дней подряд", "12")
        )

        layout.addLayout(stats_layout)

        # Карточка с графиком
        chart_card = QFrame()
        chart_card.setObjectName("contentCard")

        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(22, 20, 22, 18)
        chart_layout.setSpacing(12)

        chart_title = QLabel("Активность за неделю")
        chart_title.setObjectName("sectionTitle")

        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.create_chart())

        layout.addWidget(chart_card)

        # Карточка истории действий
        history_card = QFrame()
        history_card.setObjectName("contentCard")

        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(22, 20, 22, 20)
        history_layout.setSpacing(16)

        history_title = QLabel("Последние действия")
        history_title.setObjectName("sectionTitle")

        history_layout.addWidget(history_title)

        # Демонстрационная история
        activities = [
            ("Добавлено 5 новых слов", "Сегодня"),
            ("Завершено упражнение на перевод", "Вчера"),
            ("Повторены изученные слова", "Ранее"),
        ]

        for action, moment in activities:

            row = QHBoxLayout()

            action_label = QLabel(action)
            action_label.setObjectName("activityText")

            moment_label = QLabel(moment)
            moment_label.setObjectName("mutedText")

            row.addWidget(action_label)
            row.addStretch()
            row.addWidget(moment_label)

            history_layout.addLayout(row)

        layout.addWidget(history_card)
        layout.addStretch()

    def create_stat_card(self, label, value):

        card = QFrame()
        card.setObjectName("contentCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(8)

        label_widget = QLabel(label)
        label_widget.setObjectName("mutedText")

        value_widget = QLabel(value)
        value_widget.setObjectName("statValue")

        card_layout.addWidget(label_widget)
        card_layout.addWidget(value_widget)

        return card

    def create_chart(self):

        # Демонстрационные данные
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        learned_words = [15, 25, 18, 32, 24, 40, 28]

        # Создание графика
        figure = Figure(
            figsize=(7, 2.8),
            facecolor="white"
        )

        ax = figure.add_subplot(111)

        ax.bar(
            days,
            learned_words,
            width=0.55,
            color="#7697bd"
        )

        # Настройка осей
        ax.set_ylim(0, 45)
        ax.set_yticks([0, 10, 20, 30, 40])

        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)

        ax.tick_params(
            axis="both",
            length=0,
            labelsize=10,
            colors="#6b7280"
        )

        # Убираем рамки графика
        for spine in ax.spines.values():
            spine.set_visible(False)

        figure.subplots_adjust(
            left=0.07,
            right=0.99,
            top=0.96,
            bottom=0.14
        )

        # Встраиваем график в PySide6
        canvas = FigureCanvasQTAgg(figure)
        canvas.setMinimumHeight(230)

        return canvas

    def setup_styles(self):

        self.setStyleSheet("""

            QWidget#dashboardPage,
            QWidget#dashboardContent,
            QScrollArea#dashboardScroll {
                background-color: #f5f6f8;
                border: none;
            }

            QFrame#contentCard {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }

            QLabel#dashboardTitle {
                font-size: 26px;
                font-weight: 600;
                color: #1f2937;
            }

            QLabel#sectionTitle {
                font-size: 16px;
                font-weight: 600;
                color: #1f2937;
            }

            QLabel#statValue {
                font-size: 28px;
                font-weight: 600;
                color: #315b91;
            }

            QLabel#mutedText {
                font-size: 13px;
                color: #6b7280;
            }

            QLabel#activityText {
                font-size: 13px;
                color: #374151;
            }

        """)