import sqlite3

from pathlib import Path


# Путь к корневой папке проекта
BASE_DIR = Path(__file__).resolve().parents[2]

# Путь к файлу базы данных
DB_PATH = BASE_DIR / "app.db"


# Начальные данные словаря
INITIAL_WORDS = [
    ("apple", "яблоко"),
    ("book", "книга"),
    ("friend", "друг"),
    ("journey", "путешествие"),
    ("learn", "учить"),
    ("weather", "погода"),
    ("beautiful", "красивый"),
    ("practice", "практика"),
]


def initialize_database(db_path=DB_PATH):

    # Открываем соединение с базой данных
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()

        # Проверяем, существует ли таблица words
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'words'
        """)

        is_first_run = cursor.fetchone() is None

        # Создаём таблицу слов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL COLLATE NOCASE UNIQUE,
                translation TEXT NOT NULL
            )
        """)

        # Создаём таблицу активности
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL
            )
        """)

        # Заполняем словарь только при создании таблицы
        if is_first_run:

            cursor.executemany("""
                INSERT INTO words (word, translation)
                VALUES (?, ?)
            """, INITIAL_WORDS)

        # Сохраняем изменения
        connection.commit()

    except sqlite3.Error:

        # Отменяем незавершённые изменения при ошибке
        connection.rollback()
        raise

    finally:

        # Закрываем соединение
        connection.close()


# Проверка базы при самостоятельном запуске модуля
if __name__ == "__main__":

    initialize_database()

    connection = sqlite3.connect(DB_PATH)

    try:
        words_count = connection.execute(
            "SELECT COUNT(*) FROM words"
        ).fetchone()[0]

        events_count = connection.execute(
            "SELECT COUNT(*) FROM activities"
        ).fetchone()[0]

    finally:
        connection.close()

    print(f"База данных: {DB_PATH}")
    print(f"Количество слов: {words_count}")
    print(f"Количество событий: {events_count}")