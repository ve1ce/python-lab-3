import sqlite3
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "app.db"
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


@dataclass(frozen=True)
class ActivityEvent:
    timestamp: datetime
    action: str
    details: str


@contextmanager
def database_connection(db_path):
    with closing(sqlite3.connect(db_path)) as connection, connection:
        yield connection


def initialize_database(db_path=DB_PATH):
    with database_connection(db_path) as connection:
        # Проверка, создание таблиц и заполнение словаря выполняются в одной транзакции.
        connection.execute("BEGIN IMMEDIATE")
        words_exist = connection.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'words'
        """).fetchone()
        connection.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL COLLATE NOCASE UNIQUE,
                translation TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL
            )
        """)
        if words_exist is None:
            connection.executemany(
                "INSERT INTO words (word, translation) VALUES (?, ?)", INITIAL_WORDS
            )


class VocabularyRepository:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def get_all(self):
        with database_connection(self.db_path) as connection:
            rows = connection.execute("SELECT word, translation FROM words ORDER BY id").fetchall()
        return [{"word": word, "translation": translation} for word, translation in rows]

    def add_word(self, word, translation):
        with database_connection(self.db_path) as connection:
            connection.execute(
                "INSERT INTO words (word, translation) VALUES (?, ?)", (word, translation)
            )

    def delete_word(self, word):
        with database_connection(self.db_path) as connection:
            return connection.execute("DELETE FROM words WHERE word = ?", (word,)).rowcount


class ActivityRepository:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def add_event(self, event: ActivityEvent):
        with database_connection(self.db_path) as connection:
            connection.execute(
                "INSERT INTO activities (timestamp, action, details) VALUES (?, ?, ?)",
                (event.timestamp.isoformat(timespec="seconds"), event.action, event.details),
            )

    def get_all(self):
        with database_connection(self.db_path) as connection:
            rows = connection.execute("""
                SELECT timestamp, action, details FROM activities ORDER BY id DESC
            """).fetchall()
        return [
            ActivityEvent(datetime.fromisoformat(timestamp), action, details)
            for timestamp, action, details in rows
        ]
