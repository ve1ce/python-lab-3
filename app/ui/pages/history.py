from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView
)


class HistoryPage(QWidget):

    def __init__(self, activity_log):
        super().__init__()

        self.activity_log = activity_log

        self.setObjectName("historyPage")

        self.setup_ui()
        self.setup_styles()

        # Автоматическое обновление при изменении журнала
        self.activity_log.changed.connect(
            self.refresh_table
        )

        self.refresh_table()

    def setup_ui(self):

        # Основной контейнер
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("История")
        title.setObjectName("historyTitle")

        subtitle = QLabel(
            "Журнал действий пользователя"
        )
        subtitle.setObjectName("mutedText")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Основная карточка
        history_card = QFrame()
        history_card.setObjectName("historyCard")

        card_layout = QVBoxLayout(history_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)

        # Заголовок карточки
        header_layout = QHBoxLayout()

        section_title = QLabel("Активность")
        section_title.setObjectName("sectionTitle")

        self.event_count = QLabel()
        self.event_count.setObjectName("mutedText")

        header_layout.addWidget(section_title)
        header_layout.addStretch()
        header_layout.addWidget(self.event_count)

        card_layout.addLayout(header_layout)

        # Сообщение при отсутствии событий
        self.empty_label = QLabel(
            "Пока нет событий. Добавьте слово "
            "или завершите тренировку."
        )

        self.empty_label.setObjectName("emptyMessage")
        self.empty_label.setWordWrap(True)

        card_layout.addWidget(self.empty_label)

        # Таблица истории
        self.table = QTableWidget(0, 3)
        self.table.setObjectName("historyTable")

        self.table.setHorizontalHeaderLabels([
            "Дата и время",
            "Действие",
            "Описание"
        ])

        # Настройка ширины столбцов
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        # Оформление таблицы
        self.table.verticalHeader().setVisible(False)

        self.table.verticalHeader().setDefaultSectionSize(42)

        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.setMinimumHeight(300)

        card_layout.addWidget(self.table)

        layout.addWidget(history_card, 1)

    def refresh_table(self):

        # Получаем актуальные события
        events = self.activity_log.get_events()

        self.table.setRowCount(len(events))

        # Заполняем таблицу
        for row, event in enumerate(events):

            timestamp = event.timestamp.strftime(
                "%d.%m.%Y %H:%M:%S"
            )

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(timestamp)
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(event.action)
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(event.details)
            )

        # Обновляем количество событий
        self.event_count.setText(
            f"Всего событий: {len(events)}"
        )

        # Показываем сообщение, если событий нет
        self.empty_label.setVisible(
            len(events) == 0
        )

    def setup_styles(self):

        self.setStyleSheet("""

            QWidget#historyPage {
                background-color: #f5f6f8;
            }

            QFrame#historyCard {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }

            QLabel#historyTitle {
                font-size: 26px;
                font-weight: 600;
                color: #1f2937;
            }

            QLabel#sectionTitle {
                font-size: 16px;
                font-weight: 600;
                color: #1f2937;
            }

            QLabel#mutedText {
                font-size: 13px;
                color: #6b7280;
            }

            QLabel#emptyMessage {
                font-size: 13px;
                color: #9ca3af;
                padding: 10px 0;
            }

            QTableWidget#historyTable {
                background-color: #ffffff;
                alternate-background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 5px;
                color: #374151;
                font-size: 13px;
                selection-background-color: #e8eef7;
                selection-color: #1f2937;
            }

            QHeaderView::section {
                background-color: #f3f4f6;
                border: none;
                border-bottom: 1px solid #e5e7eb;
                padding: 10px;
                color: #4b5563;
                font-weight: 600;
            }

        """)