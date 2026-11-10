from datetime import datetime, timedelta

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


class DashboardPage(QWidget):

    def __init__(self, get_words, activity_log):
        super().__init__()

        # Источники данных
        self.get_words = get_words
        self.activity_log = activity_log

        self.setObjectName("dashboardPage")

        self.setup_ui()
        self.setup_styles()

        # Обновление при изменении журнала
        self.activity_log.changed.connect(
            self.refresh_dashboard
        )

        # Первоначальное заполнение
        self.refresh_dashboard()

    def setup_ui(self):

        # Основной контейнер
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Прокручиваемая область
        scroll = QScrollArea()
        scroll.setObjectName("dashboardScroll")
        scroll.setWidgetResizable(True)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        outer_layout.addWidget(scroll)

        # Содержимое страницы
        content = QWidget()
        content.setObjectName("dashboardContent")

        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(24)

        # Заголовок
        title = QLabel("Главная")
        title.setObjectName("dashboardTitle")

        subtitle = QLabel(
            "Обзор вашего прогресса в изучении языков"
        )
        subtitle.setObjectName("mutedText")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # --------------------------------
        # Карточки статистики
        # --------------------------------

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        # Ссылки на значения карточек
        self.stat_values = {}

        stats_layout.addWidget(
            self.create_stat_card(
                "Слов в словаре",
                "words"
            )
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Тренировок",
                "sessions"
            )
        )

        stats_layout.addWidget(
            self.create_stat_card(
                "Дней активности",
                "days"
            )
        )

        layout.addLayout(stats_layout)

        # --------------------------------
        # График активности
        # --------------------------------

        chart_card = QFrame()
        chart_card.setObjectName("contentCard")

        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(22, 20, 22, 18)
        chart_layout.setSpacing(12)

        chart_title = QLabel("Активность за неделю")
        chart_title.setObjectName("sectionTitle")

        self.chart_note = QLabel()
        self.chart_note.setObjectName("mutedText")

        chart_layout.addWidget(chart_title)
        chart_layout.addWidget(self.chart_note)

        # Создаём график
        self.chart_canvas = self.create_chart()

        chart_layout.addWidget(self.chart_canvas)

        layout.addWidget(chart_card)

        # --------------------------------
        # Последние действия
        # --------------------------------

        history_card = QFrame()
        history_card.setObjectName("contentCard")

        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(22, 20, 22, 20)
        history_layout.setSpacing(16)

        history_title = QLabel("Последние действия")
        history_title.setObjectName("sectionTitle")

        history_layout.addWidget(history_title)

        # Создаём три строки для событий
        self.activity_rows = []

        for _ in range(3):

            row = QHBoxLayout()
            row.setSpacing(15)

            action_label = QLabel()
            action_label.setObjectName("activityText")
            action_label.setWordWrap(True)

            time_label = QLabel()
            time_label.setObjectName("mutedText")

            row.addWidget(action_label, 1)
            row.addWidget(time_label)

            history_layout.addLayout(row)

            self.activity_rows.append(
                (action_label, time_label)
            )

        layout.addWidget(history_card)
        layout.addStretch()

    def create_stat_card(self, label, key):

        card = QFrame()
        card.setObjectName("contentCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(8)

        label_widget = QLabel(label)
        label_widget.setObjectName("mutedText")

        value_widget = QLabel("0")
        value_widget.setObjectName("statValue")

        card_layout.addWidget(label_widget)
        card_layout.addWidget(value_widget)

        # Запоминаем QLabel для обновления
        self.stat_values[key] = value_widget

        return card

    def create_chart(self):

        # Создаём фигуру Matplotlib
        self.figure = Figure(
            figsize=(7, 2.8),
            facecolor="white"
        )

        self.axes = self.figure.add_subplot(111)

        canvas = FigureCanvasQTAgg(self.figure)
        canvas.setMinimumHeight(230)

        return canvas

    def refresh_dashboard(self):

        # Получаем актуальные данные
        words = self.get_words()
        events = self.activity_log.get_events()

        # Количество завершённых тренировок
        sessions = sum(
            1 for event in events
            if event.action == "Завершена тренировка"
        )

        # Количество уникальных дней активности
        active_days = {
            event.timestamp.date()
            for event in events
        }

        # Обновляем статистику
        self.stat_values["words"].setText(
            str(len(words))
        )

        self.stat_values["sessions"].setText(
            str(sessions)
        )

        self.stat_values["days"].setText(
            str(len(active_days))
        )

        # Обновляем остальные компоненты
        self.refresh_activities(events)
        self.refresh_chart(events)

    def refresh_activities(self, events):

        for index, (action_label, time_label) in enumerate(
            self.activity_rows
        ):

            if index < len(events):

                event = events[index]

                action_label.setText(
                    f"{event.action}: {event.details}"
                )

                time_label.setText(
                    event.timestamp.strftime("%d.%m %H:%M")
                )

            else:

                if index == 0:
                    action_label.setText(
                        "Пока нет записанных действий"
                    )
                else:
                    action_label.setText("")

                time_label.setText("")

    def refresh_chart(self, events):

        # Последние семь календарных дней
        today = datetime.now().date()

        dates = [
            today - timedelta(days=6 - i)
            for i in range(7)
        ]

        weekday_names = [
            "Пн", "Вт", "Ср", "Чт",
            "Пт", "Сб", "Вс"
        ]

        days = [
            weekday_names[day.weekday()]
            for day in dates
        ]

        # Количество событий за каждый день
        activity = [
            sum(
                1 for event in events
                if event.timestamp.date() == day
            )
            for day in dates
        ]

        # Пока событий нет, показываем пример
        if not events:

            activity = [2, 4, 3, 5, 4, 6, 3]

            self.chart_note.setText(
                "Демонстрационные данные"
            )

        else:

            self.chart_note.setText(
                "Количество действий за последние 7 дней"
            )

        # Перерисовываем график
        self.axes.clear()

        self.axes.bar(
            days,
            activity,
            width=0.55,
            color="#7697bd"
        )

        # Настраиваем оси
        self.axes.set_ylim(
            0,
            max(5, max(activity) + 1)
        )

        self.axes.yaxis.set_major_locator(
            MaxNLocator(integer=True, nbins=5)
        )

        self.axes.grid(
            axis="y",
            alpha=0.2
        )

        self.axes.set_axisbelow(True)

        self.axes.tick_params(
            axis="both",
            length=0,
            labelsize=10,
            colors="#6b7280"
        )

        # Убираем рамки
        for spine in self.axes.spines.values():
            spine.set_visible(False)

        self.figure.subplots_adjust(
            left=0.07,
            right=0.99,
            top=0.96,
            bottom=0.14
        )

        # Обновляем виджет графика
        self.chart_canvas.draw_idle()

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