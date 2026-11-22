from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from app import database
from app.services import practice_quiz


def test_database_tables_created(db):
    with database.get_connection() as connection:
        tables = {row[0] for row in connection.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )}
    assert {"words", "activities", "practice_sessions"} <= tables


def test_database_initialization_is_idempotent(db):
    with database.get_connection() as connection:
        connection.execute("DROP TABLE practice_sessions, activities, words")
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda _: database.initialize_database(), range(2)))
    assert len(database.VocabularyRepository().get_words()) == 8


def test_deleted_words_are_not_restored(db):
    with database.get_connection() as connection:
        connection.execute("DELETE FROM words")
    database.initialize_database()
    assert database.VocabularyRepository().get_words() == []


def test_initialization_preserves_existing_data(db):
    repository = database.VocabularyRepository()
    repository.add_word("hello", "привет")
    session_id = uuid4()
    database.create_practice(session_id, practice_quiz(repository.get_words(), 5))
    session = database.get_practice(session_id)
    before = repository.get_words(), database.ActivityRepository().get_all()
    database.initialize_database()
    assert (repository.get_words(), database.ActivityRepository().get_all()) == before
    assert database.get_practice(session_id) == session
