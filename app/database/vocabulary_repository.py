import sqlite3

from contextlib import closing

from app.database.connection import DB_PATH


class VocabularyRepository:

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def get_all(self):

        # Подключаемся к базе данных
        with closing(sqlite3.connect(self.db_path)) as connection:

            # Получаем все слова
            cursor = connection.execute("""
                SELECT word, translation
                FROM words
                ORDER BY id
            """)

            rows = cursor.fetchall()

        # Преобразуем записи в список словарей
        return [
            {
                "word": row[0],
                "translation": row[1]
            }
            for row in rows
        ]

    def add_word(self, word, translation):

        with closing(sqlite3.connect(self.db_path)) as connection:

            # Транзакция с автоматическим commit/rollback
            with connection:

                connection.execute("""
                    INSERT INTO words (word, translation)
                    VALUES (?, ?)
                """, (word, translation))

    def delete_word(self, word):

        with closing(sqlite3.connect(self.db_path)) as connection:

            with connection:

                cursor = connection.execute("""
                    DELETE FROM words
                    WHERE word = ?
                """, (word,))

                # Количество удалённых записей
                return cursor.rowcount