import os
from uuid import uuid4

import psycopg
from psycopg import sql
import pytest

from app import database
from app.services import VocabularyService


@pytest.fixture(scope="session")
def test_database():
    # Административное подключение идёт в postgres, а не в пользовательскую БД.
    name = "language_lab_test_" + uuid4().hex
    settings = dict(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        user=os.getenv("POSTGRES_USER", "lab_user"),
        password=os.environ["POSTGRES_PASSWORD"], connect_timeout=5,
    )
    with psycopg.connect(dbname="postgres", autocommit=True, **settings) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        try:
            yield lambda: psycopg.connect(dbname=name, **settings)
        finally:
            # Удаляем только базу с именем, сгенерированным этим запуском.
            admin.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(name)))


@pytest.fixture
def db(test_database, monkeypatch):
    monkeypatch.setattr(database, "get_connection", test_database)
    with test_database() as connection:
        assert connection.execute("SELECT current_database()").fetchone()[0].startswith(
            "language_lab_test_"
        )
        connection.execute("DROP TABLE IF EXISTS practice_sessions, activities, words")
    database.initialize_database()


@pytest.fixture
def vocabulary_service(db):
    return VocabularyService(database.VocabularyRepository())
