import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.exceptions import VocabularyValidationError


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

'''класс описывает события пользователя'''
@dataclass(frozen=True)
class ActivityEvent:
    timestamp: datetime
    action: str
    details: str


PRACTICE_COMPLETED = "Завершена тренировка"

#подключаемся к postgre
BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")

'''подгрузка переменных из .env'''
def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        dbname=os.getenv("POSTGRES_DB", "language_lab"),
        user=os.getenv("POSTGRES_USER", "lab_user"),
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5
    )

'''инициализация'''
def initialize_database():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # защита от одновременного запуска интерфейсов
            cursor.execute("SELECT pg_advisory_xact_lock(731003)")
            cursor.execute(
                "SELECT to_regclass('public.words')"
            )

            is_first_run = cursor.fetchone()[0] is None

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS words (
                    id SERIAL PRIMARY KEY,
                    word TEXT NOT NULL,
                    translation TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS words_unique
                ON words (LOWER(word))
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS practice_sessions (
                    id UUID PRIMARY KEY,
                    questions JSONB NOT NULL,
                    question_index INTEGER NOT NULL DEFAULT 0,
                    selected INTEGER,
                    score INTEGER NOT NULL DEFAULT 0
                )
            """)

            if is_first_run:
                cursor.executemany("""
                    INSERT INTO words (word, translation)
                    VALUES (%s, %s)
                """, INITIAL_WORDS)


def record_activity(connection, action, details):
    connection.execute("""
        INSERT INTO activities (timestamp, action, details)
        VALUES (%s, %s, %s)
    """, (datetime.now(), action, details))


def get_activities(connection, limit=None):
    rows = connection.execute("""
        SELECT timestamp, action, details FROM activities
        ORDER BY timestamp DESC, id DESC
        LIMIT %s
    """, (limit,)).fetchall()
    return [ActivityEvent(*row) for row in rows]


def get_dashboard(today):
    with get_connection() as connection:
        connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        counts = connection.execute("""
            SELECT (SELECT COUNT(*) FROM words),
                   COUNT(*) FILTER (WHERE action = %s),
                   COUNT(DISTINCT timestamp::date)
            FROM activities
        """, (PRACTICE_COMPLETED,)).fetchone()
        daily_counts = connection.execute("""
            SELECT timestamp::date, COUNT(*) FROM activities
            WHERE timestamp >= %s AND timestamp < %s
            GROUP BY timestamp::date
        """, (today - timedelta(days=6), today + timedelta(days=1))).fetchall()
        return counts, dict(daily_counts), get_activities(connection, limit=3)


def create_practice(session_id, questions):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO practice_sessions (id, questions) VALUES (%s, %s)
        """, (session_id, Jsonb(questions)))


def get_practice(session_id):
    with get_connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
        return cursor.execute("""
            SELECT * FROM practice_sessions WHERE id = %s
        """, (session_id,)).fetchone()


def update_practice(session_id, index, choice):
    with get_connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
        # Блокировка строки защищает от одновременных и повторных отправок формы.
        session = cursor.execute("""
            SELECT * FROM practice_sessions WHERE id = %s FOR UPDATE
        """, (session_id,)).fetchone()
        if session is None:
            return False

        questions = session["questions"]
        if index != session["question_index"] or index == len(questions):
            return True

        selected, score = session["selected"], session["score"]
        if choice is not None and not 0 <= choice < len(questions[index]["options"]):
            raise ValueError("Недопустимый вариант ответа")
        if choice is not None and selected is None:
            selected = choice
            score += int(choice == questions[index]["correct"])
        elif choice is None and selected is not None:
            index += 1
            selected = None
        else:
            return True

        cursor.execute("""
            UPDATE practice_sessions SET question_index = %s, selected = %s, score = %s
            WHERE id = %s
        """, (index, selected, score, session_id))
        if index == len(questions):
            record_activity(
                connection, PRACTICE_COMPLETED,
                f"Правильных ответов: {score} из {len(questions)}"
            )
        return True


class VocabularyRepository:

    def get_words(self):
        with get_connection() as connection:
            rows = connection.execute("""
                SELECT id, word, translation
                FROM words
                ORDER BY id
            """).fetchall()

        return [
            {
                "id": word_id,
                "word": word,
                "translation": translation
            }
            for word_id, word, translation in rows
        ]

    def add_word(self, word, translation):
        word = word.strip()
        translation = translation.strip()

        if not word or not translation:
            raise VocabularyValidationError("Заполните оба поля")

        if len(word) > 80 or len(translation) > 80:
            raise VocabularyValidationError(
                "Максимальная длина — 80 символов"
            )

        #обработка транзакций
        try:
            with get_connection() as connection:
                connection.execute("""
                    INSERT INTO words (word, translation)
                    VALUES (%s, %s)
                """, (word, translation))

                record_activity(
                    connection,
                    "Добавлено слово",
                    f"{word} — {translation}"
                )
            return {"word": word, "translation": translation}

        except psycopg.errors.UniqueViolation as error:
            raise VocabularyValidationError(
                "Такое слово уже есть в словаре"
            ) from error

    def delete_word(self, word_id):
        with get_connection() as connection:
            row = connection.execute("""
                DELETE FROM words
                WHERE id = %s
                RETURNING word, translation
            """, (word_id,)).fetchone()

            if row is None:
                raise VocabularyValidationError(
                    "Слово не найдено в словаре"
                )

            record_activity(
                connection,
                "Удалено слово",
                f"{row[0]} — {row[1]}"
            )


class ActivityRepository:
    def get_all(self):
        with get_connection() as connection:
            return get_activities(connection)
