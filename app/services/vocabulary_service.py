import sqlite3

from app.exceptions import VocabularyValidationError


class VocabularyService:

    def __init__(self, repository):
        self.repository = repository

    def get_words(self):

        return self.repository.get_all()

    def add_word(self, word, translation):

        # Удаляем лишние пробелы
        word = word.strip()
        translation = translation.strip()

        # Проверяем заполнение полей
        if not word or not translation:
            raise VocabularyValidationError(
                "Заполните оба поля"
            )

        # Сохраняем слово в базе
        try:
            self.repository.add_word(
                word,
                translation
            )

        except sqlite3.IntegrityError as error:
            raise VocabularyValidationError(
                "Такое слово уже есть в словаре"
            ) from error

        return {
            "word": word,
            "translation": translation
        }

    def delete_word(self, word):

        word = word.strip()

        if not word:
            raise VocabularyValidationError(
                "Не указано слово для удаления"
            )

        deleted_count = self.repository.delete_word(word)

        if deleted_count == 0:
            raise VocabularyValidationError(
                "Слово не найдено в словаре"
            )