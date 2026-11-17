import sqlite3

from datetime import datetime

import pytest

from app.models.activity import ActivityEvent
from app.database.activity_repository import ActivityRepository
from app.services.activity_log import ActivityLog


def test_empty_activity_history(db_path):

    repository = ActivityRepository(db_path)

    events = repository.get_all()

    assert events == []


def test_event_saved_with_timestamp(db_path):

    repository = ActivityRepository(db_path)

    timestamp = datetime(2026, 11, 10, 14, 30, 15)

    event = ActivityEvent(
        timestamp=timestamp,
        action="Добавлено слово",
        details="hello — привет"
    )

    repository.add_event(event)

    events = repository.get_all()

    assert len(events) == 1
    assert events[0] == event


def test_recent_events_first(db_path):

    repository = ActivityRepository(db_path)

    repository.add_event(
        ActivityEvent(
            timestamp=datetime(2026, 11, 10, 12, 0),
            action="Добавлено слово",
            details="computer — компьютер"
        )
    )

    repository.add_event(
        ActivityEvent(
            timestamp=datetime(2026, 11, 10, 12, 5),
            action="Удалено слово",
            details="computer — компьютер"
        )
    )

    events = repository.get_all()

    assert len(events) == 2

    assert events[0].action == "Удалено слово"
    assert events[1].action == "Добавлено слово"


def test_event_persists_after_reconnection(db_path):

    first_repository = ActivityRepository(db_path)

    first_repository.add_event(
        ActivityEvent(
            timestamp=datetime(2026, 11, 10, 15, 0),
            action="Завершена тренировка",
            details="Правильных ответов: 4 из 5"
        )
    )

    # Создаём новый объект репозитория
    second_repository = ActivityRepository(db_path)

    events = second_repository.get_all()

    assert len(events) == 1
    assert events[0].action == "Завершена тренировка"


def test_activity_log_records_event(db_path):

    repository = ActivityRepository(db_path)
    activity_log = ActivityLog(repository)

    activity_log.add_event(
        "Добавлено слово",
        "book — книга"
    )

    events = activity_log.get_events()

    assert len(events) == 1

    assert events[0].action == "Добавлено слово"
    assert events[0].details == "book — книга"

    assert isinstance(events[0].timestamp, datetime)


def test_activity_log_emits_changed_signal(db_path):

    repository = ActivityRepository(db_path)
    activity_log = ActivityLog(repository)

    # Список для регистрации сигналов
    notifications = []

    # Подключаем обработчик
    activity_log.changed.connect(
        lambda: notifications.append("changed")
    )

    activity_log.add_event(
        "Добавлено слово",
        "apple — яблоко"
    )

    # Сигнал должен сработать ровно один раз
    assert notifications == ["changed"]

    # Событие при этом должно находиться в БД
    assert len(repository.get_all()) == 1


def test_no_signal_when_save_fails():

    # Репозиторий, имитирующий ошибку SQLite
    class FailingRepository:

        def add_event(self, event):
            raise sqlite3.OperationalError(
                "Ошибка записи в базу данных"
            )

    activity_log = ActivityLog(FailingRepository())

    notifications = []

    activity_log.changed.connect(
        lambda: notifications.append("changed")
    )

    with pytest.raises(sqlite3.OperationalError):

        activity_log.add_event(
            "Добавлено слово",
            "hello — привет"
        )

    # Если запись не удалась, сигнал не отправляется
    assert notifications == []