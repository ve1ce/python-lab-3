from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView
)

from app.exceptions import VocabularyValidationError


class VocabularyPage(QWidget):

    def __init__(self):
        super().__init__()

        # Демонстрационные данные
        self.words = [
            {"word": "apple", "translation": "яблоко"},
            {"word": "book", "translation": "книга"},
            {"word": "friend", "translation": "друг"},
            {"word": "journey", "translation": "путешествие"},
            {"word": "learn", "translation": "учить"},
            {"word": "weather", "translation": "погода"},
            {"word": "beautiful", "translation": "красивый"},
            {"word": "practice", "translation": "практика"}
        ]

        self.setup_ui()
        self.setup_styles()
        self.refresh_table()

    def setup_ui(self):

        # Основная область
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("vocabularyScroll")
        scroll.setWidgetResizable(True)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        outer_layout.addWidget(scroll)

        content = QWidget()
        content.setObjectName("vocabularyContent")

        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel("Словарь")
        title.setObjectName("vocabularyTitle")

        subtitle = QLabel(
            "Добавляйте новые слова и повторяйте изученный материал"
        )
        subtitle.setObjectName("mutedText")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Карточка добавления слов
        add_card = QFrame()
        add_card.setObjectName("contentCard")

        add_layout = QVBoxLayout(add_card)
        add_layout.setContentsMargins(20, 20, 20, 20)
        add_layout.setSpacing(15)

        add_title = QLabel("Добавить новое слово")
        add_title.setObjectName("sectionTitle")

        add_layout.addWidget(add_title)

        # Поля ввода
        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(15)

        word_layout = QVBoxLayout()

        word_label = QLabel("Английское слово")

        self.word_input = QLineEdit()
        self.word_input.setObjectName("inputField")
        self.word_input.setPlaceholderText("Например, hello")
        self.word_input.setMaxLength(80)

        word_layout.addWidget(word_label)
        word_layout.addWidget(self.word_input)

        translation_layout = QVBoxLayout()

        translation_label = QLabel("Перевод")

        self.translation_input = QLineEdit()
        self.translation_input.setObjectName("inputField")
        self.translation_input.setPlaceholderText("Например, привет")
        self.translation_input.setMaxLength(80)

        translation_layout.addWidget(translation_label)
        translation_layout.addWidget(self.translation_input)

        inputs_layout.addLayout(word_layout)
        inputs_layout.addLayout(translation_layout)

        add_layout.addLayout(inputs_layout)

        # Сообщение и кнопка добавления
        actions_layout = QHBoxLayout()

        self.feedback_label = QLabel("")
        self.feedback_label.setWordWrap(True)

        add_button = QPushButton("Добавить слово")
        add_button.setObjectName("primaryButton")
        add_button.setMinimumHeight(38)

        add_button.clicked.connect(self.add_word)

        self.translation_input.returnPressed.connect(
            self.add_word
        )

        actions_layout.addWidget(self.feedback_label, 1)
        actions_layout.addWidget(add_button)

        add_layout.addLayout(actions_layout)

        layout.addWidget(add_card)

        # Карточка таблицы
        table_card = QFrame()
        table_card.setObjectName("contentCard")

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)

        table_header = QHBoxLayout()

        table_title = QLabel("Мои слова")
        table_title.setObjectName("sectionTitle")

        self.word_count = QLabel()
        self.word_count.setObjectName("mutedText")

        table_header.addWidget(table_title)
        table_header.addStretch()
        table_header.addWidget(self.word_count)

        table_layout.addLayout(table_header)

        # Поиск по словарю
        self.search_input = QLineEdit()
        self.search_input.setObjectName("inputField")
        self.search_input.setPlaceholderText(
            "Поиск по слову или переводу..."
        )

        self.search_input.textChanged.connect(
            self.refresh_table
        )

        table_layout.addWidget(self.search_input)

        # Таблица слов
        self.table = QTableWidget(0, 2)
        self.table.setObjectName("wordsTable")

        self.table.setHorizontalHeaderLabels([
            "Английское слово",
            "Перевод"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.verticalHeader().setVisible(False)

        self.table.verticalHeader().setDefaultSectionSize(38)

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(250)

        table_layout.addWidget(self.table)

        # Кнопка удаления
        bottom_layout = QHBoxLayout()

        hint = QLabel("Выберите строку для удаления")
        hint.setObjectName("mutedText")

        delete_button = QPushButton("Удалить слово")
        delete_button.setObjectName("deleteButton")
        delete_button.setMinimumHeight(36)

        delete_button.clicked.connect(self.delete_word)

        bottom_layout.addWidget(hint)
        bottom_layout.addStretch()
        bottom_layout.addWidget(delete_button)

        table_layout.addLayout(bottom_layout)

        layout.addWidget(table_card, 1)
        
    def get_words(self):
        return [item.copy() for item in self.words]

    def add_word(self):

        word = self.word_input.text().strip()
        translation = self.translation_input.text().strip()

        try:
            if not word or not translation:
                raise VocabularyValidationError(
                    "Заполните оба поля"
                )

            for item in self.words:
                if item["word"].casefold() == word.casefold():
                    raise VocabularyValidationError(
                        "Такое слово уже есть в словаре"
                    )

        except VocabularyValidationError as error:
            self.show_feedback(str(error), is_error=True)
            return

        # Добавление новой записи
        self.words.append({
            "word": word,
            "translation": translation
        })

        self.word_input.clear()
        self.translation_input.clear()

        # Сбрасываем поиск и обновляем таблицу
        self.search_input.clear()
        self.refresh_table()

        self.show_feedback("Слово успешно добавлено")

    def delete_word(self):

        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            self.show_feedback(
                "Сначала выберите слово в таблице",
                is_error=True
            )
            return

        row = selected_rows[0].row()

        word = self.table.item(row, 0).text()

        # Удаление записи из списка
        self.words = [
            item for item in self.words
            if item["word"].casefold() != word.casefold()
        ]

        self.refresh_table()

        self.show_feedback("Слово успешно удалено")

    def refresh_table(self):

        search_text = self.search_input.text().strip().casefold()

        # Фильтрация слов
        filtered_words = [
            item for item in self.words
            if search_text in item["word"].casefold()
            or search_text in item["translation"].casefold()
        ]

        self.table.setRowCount(len(filtered_words))

        for row, item in enumerate(filtered_words):

            word_item = QTableWidgetItem(item["word"])
            translation_item = QTableWidgetItem(
                item["translation"]
            )

            word_item.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter
            )

            translation_item.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter
            )

            self.table.setItem(row, 0, word_item)
            self.table.setItem(row, 1, translation_item)

        self.word_count.setText(
            f"Показано: {len(filtered_words)} из {len(self.words)}"
        )

    def show_feedback(self, message, is_error=False):

        self.feedback_label.setText(message)

        if is_error:
            color = "#b45309"
        else:
            color = "#347858"

        self.feedback_label.setStyleSheet(
            f"color: {color}; font-size: 12px;"
        )

    def setup_styles(self):

        self.setStyleSheet("""

            QWidget#vocabularyContent,
            QScrollArea#vocabularyScroll {
                background-color: #f5f6f8;
                border: none;
            }

            QFrame#contentCard {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }

            QLabel#vocabularyTitle {
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

            QLineEdit#inputField {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 9px 11px;
                font-size: 13px;
                color: #1f2937;
            }

            QLineEdit#inputField:focus {
                border: 1px solid #7697bd;
            }

            QPushButton#primaryButton {
                background-color: #416b9b;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: white;
                font-size: 13px;
            }

            QPushButton#primaryButton:hover {
                background-color: #365a84;
            }

            QPushButton#deleteButton {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 8px 16px;
                color: #4b5563;
                font-size: 13px;
            }

            QPushButton#deleteButton:hover {
                background-color: #f3f4f6;
            }

            QTableWidget#wordsTable {
                background-color: white;
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