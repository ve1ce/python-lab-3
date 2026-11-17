import random
import sqlite3
from datetime import datetime

from PySide6.QtCore import QObject, Signal

from app.database import ActivityEvent
from app.exceptions import VocabularyValidationError

PRACTICE_COMPLETED = "Завершена тренировка"


class VocabularyService:
    def __init__(self, repository):
        self.repository = repository

    def get_words(self):
        return self.repository.get_all()

    def add_word(self, word, translation):
        word, translation = word.strip(), translation.strip()

        if not word or not translation:
            raise VocabularyValidationError("Заполните оба поля")

        try:
            self.repository.add_word(word, translation)
        except sqlite3.IntegrityError as error:
            raise VocabularyValidationError(
                "Такое слово уже есть в словаре"
            ) from error

        return {"word": word, "translation": translation}

    def delete_word(self, word):
        word = word.strip()

        if not word:
            raise VocabularyValidationError(
                "Не указано слово для удаления"
            )

        if self.repository.delete_word(word) == 0:
            raise VocabularyValidationError(
                "Слово не найдено в словаре"
            )


class ActivityLog(QObject):
    changed = Signal()

    def __init__(self, repository):
        super().__init__()
        self.repository = repository

    def add_event(self, action, details):
        self.repository.add_event(
            ActivityEvent(datetime.now(), action, details)
        )
        self.changed.emit()

    def get_events(self):
        return self.repository.get_all()


def practice_questions(words, question_count=5):
    unique_translations = {}

    for item in words:
        translation = item["translation"]
        unique_translations.setdefault(
            translation.casefold(), translation
        )

    translations = list(unique_translations.values())

    if len(words) < question_count or len(translations) < 4:
        return [], translations

    questions = random.sample(words, question_count)

    return questions, translations


def practice_options(translations, correct_translation):
    wrong_answers = [
        translation for translation in translations
        if translation.casefold() != correct_translation.casefold()
    ]

    options = random.sample(wrong_answers, 3)
    options.append(correct_translation)
    random.shuffle(options)

    return options