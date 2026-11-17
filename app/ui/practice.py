from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QProgressBar, QWidget

from app.services import (
    PRACTICE_COMPLETED,
    practice_options,
    practice_questions
)

from app.ui.widgets import (
    button,
    card,
    label,
    page_layout,
    set_style_state
)


class PracticePage(QWidget):
    def __init__(self, get_words, activity_log):
        super().__init__()

        self.get_words = get_words
        self.activity_log = activity_log

        self.questions = []
        self.translations = []

        self.current_index = 0
        self.correct_answers = 0
        self.answered = False

        self.setObjectName("practicePage")
        self.setup_ui()

        self.activity_log.changed.connect(self.refresh_levels)
        self.refresh_levels()

    def setup_ui(self):
        layout = page_layout(
            self,
            "Практика",
            "Проверьте свои знания английских слов",
            scrollable=True
        )

        self.start_card = self.create_start_card()
        self.quiz_card = self.create_quiz_card()
        self.finish_card = self.create_finish_card()

        layout.addWidget(self.start_card)
        layout.addWidget(self.quiz_card)
        layout.addWidget(self.finish_card)
        layout.addStretch()

        self.quiz_card.hide()
        self.finish_card.hide()

    def create_start_card(self):
        start_card, layout = card(
            (25, 30, 25, 30),
            spacing=18
        )

        description = label(
            "Выберите уровень сложности тренировки.",
            "mutedText"
        )

        layout.addWidget(
            label("Тренировка перевода", "sectionTitle")
        )
        layout.addWidget(description)

        self.level_buttons = {}

        for count, name in (
            (5, "Лёгкий"),
            (10, "Средний"),
            (15, "Сложный")
        ):
            level_button = button(
                f"{name} — {count} вопросов",
                "primaryButton",
                40
            )

            level_button.clicked.connect(
                lambda checked=False, n=count: self.start_practice(n)
            )

            self.level_buttons[count] = level_button
            layout.addWidget(level_button)

        self.start_message = label("", "mutedText")
        self.start_message.setWordWrap(True)

        layout.addWidget(self.start_message)

        return start_card

    def create_quiz_card(self):
        quiz_card, layout = card(
            (25, 25, 25, 25),
            spacing=20
        )

        info_layout = QHBoxLayout()

        self.question_counter = label("", "mutedText")
        self.score_label = label("", "mutedText")

        info_layout.addWidget(self.question_counter)
        info_layout.addStretch()
        info_layout.addWidget(self.score_label)

        layout.addLayout(info_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("practiceProgress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)

        layout.addWidget(self.progress_bar)

        question_hint = label(
            "Выберите перевод слова",
            "mutedText"
        )
        question_hint.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.word_label = label("", "wordLabel")
        self.word_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addSpacing(10)
        layout.addWidget(question_hint)
        layout.addWidget(self.word_label)
        layout.addSpacing(10)

        self.answer_buttons = []

        for _ in range(4):
            answer = button("", "answerButton", 46)

            answer.clicked.connect(
                lambda checked=False, choice=answer:
                self.check_answer(choice)
            )

            self.answer_buttons.append(answer)
            layout.addWidget(answer)

        self.feedback_label = label("", "feedbackText")
        self.feedback_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.feedback_label.setWordWrap(True)

        layout.addWidget(self.feedback_label)

        self.next_button = button(
            "Следующий вопрос",
            "primaryButton",
            40
        )

        self.next_button.clicked.connect(self.next_question)

        layout.addWidget(self.next_button)

        return quiz_card

    def create_finish_card(self):
        finish_card, layout = card(
            (25, 30, 25, 30),
            spacing=18
        )

        self.result_label = label("", "resultLabel")

        description = label(
            "Вы можете пройти тренировку ещё раз "
            "или выбрать другой уровень сложности.",
            "mutedText"
        )
        description.setWordWrap(True)

        restart_button = button(
            "Выбрать уровень",
            "primaryButton",
            40
        )

        restart_button.clicked.connect(
            self.show_level_selection
        )

        layout.addWidget(
            label("Тренировка завершена", "sectionTitle")
        )
        layout.addWidget(self.result_label)
        layout.addWidget(description)
        layout.addWidget(restart_button)

        return finish_card

    def refresh_levels(self):
        words = self.get_words()

        unique_translations = {
            item["translation"].casefold()
            for item in words
        }

        for count, level_button in self.level_buttons.items():
            available = (
                len(words) >= count
                and len(unique_translations) >= 4
            )

            level_button.setEnabled(available)

        if len(words) < 5:
            self.start_message.setText(
                f"Слов в словаре: {len(words)}. "
                "Для тренировки необходимо минимум 5 слов."
            )

        elif len(unique_translations) < 4:
            self.start_message.setText(
                "Необходимо минимум 4 разных перевода."
            )

        else:
            self.start_message.setText(
                f"Слов в словаре: {len(words)}"
            )

    def show_level_selection(self):
        self.quiz_card.hide()
        self.finish_card.hide()
        self.start_card.show()

        self.refresh_levels()

    def start_practice(self, question_count):
        self.questions, self.translations = practice_questions(
            self.get_words(),
            question_count
        )

        if not self.questions:
            self.refresh_levels()
            return

        self.current_index = 0
        self.correct_answers = 0

        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setValue(0)

        self.start_card.hide()
        self.finish_card.hide()
        self.quiz_card.show()

        self.show_question()

    def show_question(self):
        self.answered = False

        question = self.questions[self.current_index]

        self.word_label.setText(question["word"])

        self.question_counter.setText(
            f"Вопрос {self.current_index + 1} "
            f"из {len(self.questions)}"
        )

        self.score_label.setText(
            f"Верных ответов: {self.correct_answers}"
        )

        options = practice_options(
            self.translations,
            question["translation"]
        )

        for answer, text in zip(self.answer_buttons, options):
            answer.setText(text)
            answer.setEnabled(True)
            set_style_state(answer, "")

        self.feedback_label.clear()
        self.next_button.setEnabled(False)

        if self.current_index == len(self.questions) - 1:
            self.next_button.setText("Завершить тренировку")
        else:
            self.next_button.setText("Следующий вопрос")

    def check_answer(self, selected_button):
        if self.answered:
            return

        self.answered = True

        correct_translation = (
            self.questions[self.current_index]["translation"]
        )

        correct_key = correct_translation.casefold()

        if selected_button.text().casefold() == correct_key:
            self.correct_answers += 1
            self.feedback_label.setText(
                "Верно! Отличная работа."
            )

        else:
            self.feedback_label.setText(
                f"Неверно. Правильный ответ: {correct_translation}"
            )

        for answer in self.answer_buttons:
            answer.setEnabled(False)

            if answer.text().casefold() == correct_key:
                set_style_state(answer, "correct")

            elif answer == selected_button:
                set_style_state(answer, "incorrect")

        self.score_label.setText(
            f"Верных ответов: {self.correct_answers}"
        )

        self.progress_bar.setValue(self.current_index + 1)
        self.next_button.setEnabled(True)

    def next_question(self):
        if not self.answered:
            return

        self.current_index += 1

        if self.current_index >= len(self.questions):
            self.finish_practice()
        else:
            self.show_question()

    def finish_practice(self):
        result = (
            f"Правильных ответов: {self.correct_answers} "
            f"из {len(self.questions)}"
        )

        self.result_label.setText(result)
        self.activity_log.add_event(PRACTICE_COMPLETED, result)

        self.quiz_card.hide()
        self.finish_card.show()