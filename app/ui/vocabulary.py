from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QTableWidgetItem, QVBoxLayout,
    QWidget,
)

from app.exceptions import VocabularyValidationError
from app.ui.widgets import button, card, label, page_layout, read_only_table, set_style_state


class VocabularyPage(QWidget):
    def __init__(self, activity_log, vocabulary_service):
        super().__init__()
        self.activity_log = activity_log
        self.vocabulary_service = vocabulary_service
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        layout = page_layout(
            self, "Словарь", "Добавляйте новые слова и повторяйте изученный материал",
            scrollable=True,
        )
        layout.addWidget(self.create_add_card())
        layout.addWidget(self.create_table_card(), 1)

    def create_add_card(self):
        add_card, layout = card()
        layout.addWidget(label("Добавить новое слово", "sectionTitle"))

        inputs = QHBoxLayout()
        inputs.setSpacing(15)
        self.word_input = self.add_word_field(inputs, "Английское слово", "Например, hello")
        self.translation_input = self.add_word_field(inputs, "Перевод", "Например, привет")
        layout.addLayout(inputs)

        actions = QHBoxLayout()
        self.feedback_label = label("", "wordFeedback")
        self.feedback_label.setWordWrap(True)
        add_button = button("Добавить слово", "primaryButton", 38)
        add_button.clicked.connect(self.add_word)
        self.translation_input.returnPressed.connect(self.add_word)
        actions.addWidget(self.feedback_label, 1)
        actions.addWidget(add_button)
        layout.addLayout(actions)
        return add_card

    def add_word_field(self, inputs, title, placeholder):
        column = QVBoxLayout()
        field = self.create_input(placeholder)
        field.setMaxLength(80)
        column.addWidget(QLabel(title))
        column.addWidget(field)
        inputs.addLayout(column)
        return field

    def create_table_card(self):
        table_card, layout = card()
        header = QHBoxLayout()
        self.word_count = label("", "mutedText")
        header.addWidget(label("Мои слова", "sectionTitle"))
        header.addStretch()
        header.addWidget(self.word_count)
        layout.addLayout(header)

        self.search_input = self.create_input("Поиск по слову или переводу...")
        self.search_input.textChanged.connect(self.refresh_table)
        layout.addWidget(self.search_input)

        self.table = read_only_table(("Английское слово", "Перевод"), 38, 250)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        delete_button = button("Удалить слово", "deleteButton", 36)
        delete_button.clicked.connect(self.delete_word)
        actions.addWidget(label("Выберите строку для удаления", "mutedText"))
        actions.addStretch()
        actions.addWidget(delete_button)
        layout.addLayout(actions)
        return table_card

    @staticmethod
    def create_input(placeholder):
        field = QLineEdit()
        field.setObjectName("inputField")
        field.setPlaceholderText(placeholder)
        return field

    def add_word(self):
        try:
            saved_word = self.vocabulary_service.add_word(
                self.word_input.text(), self.translation_input.text()
            )
        except VocabularyValidationError as error:
            self.show_feedback(str(error), is_error=True)
            return

        self.activity_log.add_event(
            "Добавлено слово", f"{saved_word['word']} — {saved_word['translation']}"
        )
        self.word_input.clear()
        self.translation_input.clear()
        if self.search_input.text():
            self.search_input.clear()
        else:
            self.refresh_table()
        self.show_feedback("Слово успешно добавлено")

    def delete_word(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_feedback("Сначала выберите слово в таблице", is_error=True)
            return

        row = selected_rows[0].row()
        word = self.table.item(row, 0).text()
        translation = self.table.item(row, 1).text()
        try:
            self.vocabulary_service.delete_word(word)
        except VocabularyValidationError as error:
            self.show_feedback(str(error), is_error=True)
            return

        self.activity_log.add_event("Удалено слово", f"{word} — {translation}")
        self.refresh_table()
        self.show_feedback("Слово успешно удалено")

    def refresh_table(self):
        words = self.vocabulary_service.get_words()
        search = self.search_input.text().strip().casefold()
        filtered_words = [
            item for item in words
            if search in item["word"].casefold() or search in item["translation"].casefold()
        ]
        self.table.setRowCount(len(filtered_words))
        for row, item in enumerate(filtered_words):
            for column, key in enumerate(("word", "translation")):
                cell = QTableWidgetItem(item[key])
                cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, column, cell)
        self.word_count.setText(f"Показано: {len(filtered_words)} из {len(words)}")

    def show_feedback(self, message, is_error=False):
        self.feedback_label.setText(message)
        set_style_state(self.feedback_label, "error" if is_error else "success")
