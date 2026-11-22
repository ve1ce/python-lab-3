from datetime import datetime

import psycopg
import pytest

from app import database
from app.exceptions import VocabularyValidationError
from app.services import ActivityLog


def test_empty_activity_history(db):
    assert database.ActivityRepository().get_all() == []


def test_event_persists_after_reconnection(db):
    with database.get_connection() as connection:
        database.record_activity(connection, "Добавлено слово", "hello — привет")
    events = ActivityLog(database.ActivityRepository()).get_events()
    assert len(events) == 1
    assert events[0].details == "hello — привет"
    assert isinstance(events[0].timestamp, datetime)
    assert database.ActivityRepository().get_all() == events


def test_recent_events_first(db):
    with database.get_connection() as connection:
        for timestamp, action in [("2026-11-10 12:05", "Новое"), ("2026-11-10 12:00", "Старое")]:
            connection.execute(
                "INSERT INTO activities (timestamp, action, details) VALUES (%s, %s, %s)",
                (timestamp, action, "тест"),
            )
    assert [event.action for event in database.ActivityRepository().get_all()] == ["Новое", "Старое"]


@pytest.mark.parametrize("delete", [False, True])
def test_word_and_activity_rollback_together(db, monkeypatch, delete):
    repository = database.VocabularyRepository()
    before = repository.get_words()

    def fail(*args):
        raise psycopg.OperationalError("Ошибка записи события")

    monkeypatch.setattr(database, "record_activity", fail)
    with pytest.raises(psycopg.OperationalError):
        if delete:
            repository.delete_word(before[0]["id"])
        else:
            repository.add_word("hello", "привет")
    assert repository.get_words() == before
    assert database.ActivityRepository().get_all() == []


def test_no_events_for_failed_or_repeated_word_operations(db):
    repository = database.VocabularyRepository()
    word_id = repository.get_words()[0]["id"]
    with pytest.raises(VocabularyValidationError):
        repository.add_word("APPLE", "дубликат")
    repository.delete_word(word_id)
    with pytest.raises(VocabularyValidationError):
        repository.delete_word(word_id)
    assert len(database.ActivityRepository().get_all()) == 1
