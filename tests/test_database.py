import sqlite3

from contextlib import closing

from app.database import VocabularyRepository, initialize_database


def test_database_tables_created(db_path):

    with closing(sqlite3.connect(db_path)) as connection:

        cursor = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """)

        tables = {
            row[0] for row in cursor.fetchall()
        }

    assert "words" in tables
    assert "activities" in tables


def test_database_initialization_is_idempotent(db_path):

    # Повторно выполняем инициализацию
    initialize_database(db_path)
    initialize_database(db_path)

    repository = VocabularyRepository(db_path)

    words = repository.get_all()

    # Начальные данные не должны дублироваться
    assert len(words) == 8

    apple_count = sum(
        1 for item in words
        if item["word"] == "apple"
    )

    assert apple_count == 1


def test_deleted_words_are_not_restored(db_path):

    # Удаляем все слова из тестовой базы
    with closing(sqlite3.connect(db_path)) as connection:

        with connection:

            connection.execute(
                "DELETE FROM words"
            )

    # Повторно инициализируем базу
    initialize_database(db_path)

    repository = VocabularyRepository(db_path)

    words = repository.get_all()

    # Удалённые слова не должны появляться снова
    assert words == []
