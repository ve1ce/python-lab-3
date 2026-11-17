from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QTableWidgetItem, QWidget

from app.ui.widgets import card, label, page_layout, read_only_table


class HistoryPage(QWidget):
    def __init__(self, activity_log):
        super().__init__()
        self.activity_log = activity_log
        self.setObjectName("historyPage")
        self.setup_ui()
        self.activity_log.changed.connect(self.refresh_table)
        self.refresh_table()

    def setup_ui(self):
        layout = page_layout(self, "История", "Журнал действий пользователя")
        history_card, card_layout = card()
        header_layout = QHBoxLayout()
        self.event_count = label("", "mutedText")
        header_layout.addWidget(label("Активность", "sectionTitle"))
        header_layout.addStretch()
        header_layout.addWidget(self.event_count)
        card_layout.addLayout(header_layout)

        self.empty_label = label(
            "Пока нет событий. Добавьте слово или завершите тренировку.", "emptyMessage"
        )
        self.empty_label.setWordWrap(True)
        card_layout.addWidget(self.empty_label)

        self.table = read_only_table(("Дата и время", "Действие", "Описание"), 42, 300)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        card_layout.addWidget(self.table)
        layout.addWidget(history_card, 1)

    def refresh_table(self):
        events = self.activity_log.get_events()
        self.table.setRowCount(len(events))
        for row, event in enumerate(events):
            timestamp = event.timestamp.strftime("%d.%m.%Y %H:%M:%S")
            for column, value in enumerate((timestamp, event.action, event.details)):
                self.table.setItem(row, column, QTableWidgetItem(value))

        self.event_count.setText(f"Всего событий: {len(events)}")
        self.empty_label.setVisible(not events)
