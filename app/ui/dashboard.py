from datetime import date, timedelta

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PySide6.QtWidgets import QHBoxLayout, QWidget

from app.database import get_dashboard
from app.ui.widgets import card, label, page_layout


class DashboardPage(QWidget):
    def __init__(self, activity_log):
        super().__init__()
        self.activity_log = activity_log
        self.setObjectName("dashboardPage")
        self.setup_ui()
        self.activity_log.changed.connect(self.refresh_dashboard)
        self.refresh_dashboard()
    '''создание 3х блоков: статы, график, посл действия'''
    def setup_ui(self):
        layout = page_layout(
            self, "Главная", "Обзор вашего прогресса в изучении языков",
            scrollable=True, spacing=24,
        )

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        #карточки статы
        self.stat_values = {}
        for key, title in (
            ("words", "Слов в словаре"),
            ("sessions", "Тренировок"),
            ("days", "Дней активности"),
        ):
            stat_card, stat_layout = card((20, 18, 20, 18), spacing=8)
            self.stat_values[key] = label("0", "statValue")
            stat_layout.addWidget(label(title, "mutedText"))
            stat_layout.addWidget(self.stat_values[key])
            stats_layout.addWidget(stat_card)
        layout.addLayout(stats_layout)

        chart_card, chart_layout = card((22, 20, 22, 18), spacing=12)
        chart_layout.addWidget(label("Активность за неделю", "sectionTitle"))
        self.chart_note = label("", "mutedText")
        chart_layout.addWidget(self.chart_note)
        #гистограмма
        self.figure = Figure(figsize=(7, 2.8), facecolor="white")
        self.axes = self.figure.add_subplot(111)
        self.chart_canvas = FigureCanvasQTAgg(self.figure)
        self.chart_canvas.setMinimumHeight(230)
        chart_layout.addWidget(self.chart_canvas)
        layout.addWidget(chart_card)

        history_card, history_layout = card((22, 20, 22, 20), spacing=16)
        history_layout.addWidget(label("Последние действия", "sectionTitle"))
        self.activity_rows = []
        for _ in range(3):
            row = QHBoxLayout()
            row.setSpacing(15)
            action_label = label("", "activityText")
            action_label.setWordWrap(True)
            time_label = label("", "mutedText")
            row.addWidget(action_label, 1)
            row.addWidget(time_label)
            history_layout.addLayout(row)
            self.activity_rows.append((action_label, time_label))
        layout.addWidget(history_card)
        layout.addStretch()

    '''обновление стр'''
    def refresh_dashboard(self):
        counts, events_by_date, events = get_dashboard(date.today())
        for key, value in zip(("words", "sessions", "days"), counts):
            self.stat_values[key].setText(str(value))
        self.refresh_activities(events)
        self.refresh_chart(events_by_date)

    '''обновление последних действий'''
    def refresh_activities(self, events):
        for index, (action_label, time_label) in enumerate(self.activity_rows):
            if index < len(events):
                event = events[index]
                action_label.setText(f"{event.action}: {event.details}")
                time_label.setText(event.timestamp.strftime("%d.%m %H:%M"))
            else:
                action_label.setText("Пока нет записанных действий" if index == 0 else "")
                time_label.clear()

    #построение графика
    def refresh_chart(self, events_by_date):
        today = date.today()
        dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
        weekdays = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
        days = [weekdays[day.weekday()] for day in dates]

        if int(self.stat_values["days"].text()):
            activity = [events_by_date.get(day, 0) for day in dates]
            self.chart_note.setText("Количество действий за последние 7 дней")
        else:
            activity = [2, 4, 3, 5, 4, 6, 3]
            self.chart_note.setText("Демонстрационные данные")

        self.axes.clear()
        self.axes.bar(days, activity, width=0.55, color="#7697bd")
        self.axes.set_ylim(0, max(5, max(activity) + 1))
        self.axes.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
        self.axes.grid(axis="y", alpha=0.2)
        self.axes.set_axisbelow(True)
        self.axes.tick_params(axis="both", length=0, labelsize=10, colors="#6b7280")
        for spine in self.axes.spines.values():
            spine.set_visible(False)
        self.figure.subplots_adjust(left=0.07, right=0.99, top=0.96, bottom=0.14)
        self.chart_canvas.draw_idle()
