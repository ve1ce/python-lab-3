import random

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QProgressBar
)


class PracticePage(QWidget):

    def __init__(self, get_words, activity_log):
        super().__init__()

        self.get_words = get_words
        self.activity_log = activity_log

        # Данные текущей тренировки
        self.questions = []
        self.translations = []

        self.current_index = 0
        self.correct_answers = 0
        self.answered = False

        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):

        # Основная область
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("practiceScroll")
        scroll.setWidgetResizable(True)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        outer_layout.addWidget(scroll)

        content = QWidget()
        content.setObjectName("practiceContent")

        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(20)

        # Заголовок страницы
        title = QLabel("Практика")
        title.setObjectName("practiceTitle")

        subtitle = QLabel(
            "Проверьте свои знания английских слов"
        )
        subtitle.setObjectName("mutedText")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # --------------------------------
        # Начальный экран
        # --------------------------------

        self.start_card = QFrame()
        self.start_card.setObjectName("contentCard")

        start_layout = QVBoxLayout(self.start_card)
        start_layout.setContentsMargins(25, 30, 25, 30)
        start_layout.setSpacing(18)

        start_title = QLabel("Тренировка перевода")
        start_title.setObjectName("sectionTitle")

        start_description = QLabel(
            "Вам будет предложено до 5 английских слов. "
            "Для каждого слова необходимо выбрать правильный "
            "перевод из четырёх вариантов."
        )

        start_description.setWordWrap(True)
        start_description.setObjectName("mutedText")

        self.start_message = QLabel("")
        self.start_message.setObjectName("errorText")
        self.start_message.setWordWrap(True)

        start_button = QPushButton("Начать тренировку")
        start_button.setObjectName("primaryButton")
        start_button.setMinimumHeight(40)

        start_button.clicked.connect(self.start_practice)

        start_layout.addWidget(start_title)
        start_layout.addWidget(start_description)
        start_layout.addWidget(self.start_message)
        start_layout.addWidget(start_button)

        layout.addWidget(self.start_card)

        # --------------------------------
        # Экран тренировки
        # --------------------------------

        self.quiz_card = QFrame()
        self.quiz_card.setObjectName("contentCard")

        quiz_layout = QVBoxLayout(self.quiz_card)
        quiz_layout.setContentsMargins(25, 25, 25, 25)
        quiz_layout.setSpacing(20)

        # Информация о тренировке
        info_layout = QHBoxLayout()

        self.question_counter = QLabel()
        self.question_counter.setObjectName("mutedText")

        self.score_label = QLabel()
        self.score_label.setObjectName("mutedText")

        info_layout.addWidget(self.question_counter)
        info_layout.addStretch()
        info_layout.addWidget(self.score_label)

        quiz_layout.addLayout(info_layout)

        # Полоса прогресса
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("practiceProgress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)

        quiz_layout.addWidget(self.progress_bar)

        # Текст задания
        question_hint = QLabel("Выберите перевод слова")
        question_hint.setObjectName("mutedText")

        question_hint.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.word_label = QLabel()
        self.word_label.setObjectName("wordLabel")

        self.word_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        quiz_layout.addSpacing(10)
        quiz_layout.addWidget(question_hint)
        quiz_layout.addWidget(self.word_label)
        quiz_layout.addSpacing(10)

        # Варианты ответов
        self.answer_buttons = []

        for _ in range(4):

            button = QPushButton()
            button.setObjectName("answerButton")
            button.setMinimumHeight(46)

            button.clicked.connect(
                lambda checked=False, btn=button:
                self.check_answer(btn)
            )

            self.answer_buttons.append(button)
            quiz_layout.addWidget(button)

        # Сообщение о результате
        self.feedback_label = QLabel("")
        self.feedback_label.setObjectName("feedbackText")

        self.feedback_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.feedback_label.setWordWrap(True)

        quiz_layout.addWidget(self.feedback_label)

        # Следующий вопрос
        self.next_button = QPushButton("Следующий вопрос")
        self.next_button.setObjectName("primaryButton")
        self.next_button.setMinimumHeight(40)

        self.next_button.clicked.connect(
            self.next_question
        )

        quiz_layout.addWidget(self.next_button)

        layout.addWidget(self.quiz_card)

        # --------------------------------
        # Экран завершения
        # --------------------------------

        self.finish_card = QFrame()
        self.finish_card.setObjectName("contentCard")

        finish_layout = QVBoxLayout(self.finish_card)
        finish_layout.setContentsMargins(25, 30, 25, 30)
        finish_layout.setSpacing(18)

        finish_title = QLabel("Тренировка завершена")
        finish_title.setObjectName("sectionTitle")

        self.result_label = QLabel()
        self.result_label.setObjectName("resultLabel")

        finish_description = QLabel(
            "Вы можете пройти тренировку ещё раз. "
            "Вопросы и варианты ответов будут перемешаны."
        )

        finish_description.setObjectName("mutedText")
        finish_description.setWordWrap(True)

        restart_button = QPushButton("Пройти ещё раз")
        restart_button.setObjectName("primaryButton")
        restart_button.setMinimumHeight(40)

        restart_button.clicked.connect(
            self.start_practice
        )

        finish_layout.addWidget(finish_title)
        finish_layout.addWidget(self.result_label)
        finish_layout.addWidget(finish_description)
        finish_layout.addWidget(restart_button)

        layout.addWidget(self.finish_card)
        layout.addStretch()

        # В начале показываем только стартовый экран
        self.quiz_card.hide()
        self.finish_card.hide()

    def start_practice(self):

        words = self.get_words()

        # Собираем уникальные переводы
        unique_translations = {}

        for item in words:
            translation = item["translation"]
            key = translation.casefold()

            if key not in unique_translations:
                unique_translations[key] = translation

        self.translations = list(
            unique_translations.values()
        )

        # Для четырёх вариантов нужны четыре перевода
        if len(self.translations) < 4:

            self.start_card.show()
            self.quiz_card.hide()
            self.finish_card.hide()

            self.start_message.setText(
                "Для тренировки необходимо минимум "
                "4 слова с разными переводами."
            )

            return

        # Выбираем максимум пять случайных слов
        question_count = min(5, len(words))

        self.questions = random.sample(
            words,
            question_count
        )

        self.current_index = 0
        self.correct_answers = 0

        self.progress_bar.setMaximum(question_count)
        self.progress_bar.setValue(0)

        # Показываем тренировку
        self.start_card.hide()
        self.finish_card.hide()
        self.quiz_card.show()

        self.show_question()

    def show_question(self):

        self.answered = False

        question = self.questions[self.current_index]

        word = question["word"]
        correct_translation = question["translation"]

        # Обновляем информацию
        self.question_counter.setText(
            f"Вопрос {self.current_index + 1} "
            f"из {len(self.questions)}"
        )

        self.score_label.setText(
            f"Верных ответов: {self.correct_answers}"
        )

        self.word_label.setText(word)

        # Получаем три неправильных варианта
        wrong_answers = [
            translation
            for translation in self.translations
            if translation.casefold()
            != correct_translation.casefold()
        ]

        options = random.sample(wrong_answers, 3)

        # Добавляем правильный ответ
        options.append(correct_translation)

        # Перемешиваем варианты
        random.shuffle(options)

        for button, text in zip(
            self.answer_buttons,
            options
        ):

            button.setText(text)
            button.setEnabled(True)
            button.setStyleSheet("")

        self.feedback_label.setText("")

        self.next_button.setEnabled(False)

        if self.current_index == len(self.questions) - 1:
            self.next_button.setText("Завершить тренировку")
        else:
            self.next_button.setText("Следующий вопрос")

    def check_answer(self, selected_button):

        # Запрещаем повторный ответ
        if self.answered:
            return

        self.answered = True

        question = self.questions[self.current_index]

        correct_translation = question["translation"]

        selected_answer = selected_button.text()

        is_correct = (
            selected_answer.casefold()
            == correct_translation.casefold()
        )

        if is_correct:

            self.correct_answers += 1

            self.feedback_label.setText(
                "Верно! Отличная работа."
            )

        else:

            self.feedback_label.setText(
                f"Неверно. Правильный ответ: "
                f"{correct_translation}"
            )

        # Подсвечиваем ответы
        for button in self.answer_buttons:

            button.setEnabled(False)

            if button.text().casefold() == correct_translation.casefold():

                button.setStyleSheet("""
                    background-color: #e7f3eb;
                    border: 1px solid #74a789;
                    color: #25603c;
                """)

            elif button == selected_button:

                button.setStyleSheet("""
                    background-color: #fbeaea;
                    border: 1px solid #cf8888;
                    color: #a13b3b;
                """)

        self.score_label.setText(
            f"Верных ответов: {self.correct_answers}"
        )

        self.progress_bar.setValue(
            self.current_index + 1
        )

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

        total = len(self.questions)

        # Показываем результат
        self.result_label.setText(
            f"Правильных ответов: "
            f"{self.correct_answers} из {total}"
        )

        # Записываем результат в историю
        self.activity_log.add_event(
            "Завершена тренировка",
            f"Правильных ответов: {self.correct_answers} из {total}"
        )

        self.quiz_card.hide()
        self.finish_card.show()

    def setup_styles(self):

        self.setStyleSheet("""

            QWidget#practiceContent,
            QScrollArea#practiceScroll {
                background-color: #f5f6f8;
                border: none;
            }

            QFrame#contentCard {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }

            QLabel#practiceTitle {
                font-size: 26px;
                font-weight: 600;
                color: #1f2937;
            }

            QLabel#sectionTitle {
                font-size: 17px;
                font-weight: 600;
                color: #1f2937;
            }

            QLabel#mutedText {
                font-size: 13px;
                color: #6b7280;
            }

            QLabel#wordLabel {
                font-size: 30px;
                font-weight: 600;
                color: #1f2937;
                padding: 15px;
            }

            QLabel#resultLabel {
                font-size: 22px;
                font-weight: 600;
                color: #315b91;
            }

            QLabel#feedbackText {
                font-size: 13px;
                color: #4b5563;
            }

            QLabel#errorText {
                font-size: 13px;
                color: #b45309;
            }

            QPushButton#primaryButton {
                background-color: #416b9b;
                border: none;
                border-radius: 5px;
                padding: 10px 16px;
                color: white;
                font-size: 13px;
            }

            QPushButton#primaryButton:hover {
                background-color: #365a84;
            }

            QPushButton#primaryButton:disabled {
                background-color: #cbd5e1;
            }

            QPushButton#answerButton {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 10px;
                color: #374151;
                font-size: 14px;
                text-align: left;
            }

            QPushButton#answerButton:hover {
                background-color: #f3f6fa;
                border: 1px solid #7697bd;
            }

            QProgressBar#practiceProgress {
                background-color: #e5e7eb;
                border: none;
                border-radius: 4px;
            }

            QProgressBar#practiceProgress::chunk {
                background-color: #7697bd;
                border-radius: 4px;
            }

        """)