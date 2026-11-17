import sqlite3

from contextlib import closing
from datetime import datetime

from app.database.connection import DB_PATH
from app.models.activity import ActivityEvent


class ActivityRepository:

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def add_event(self, event: ActivityEvent):

        with closing(sqlite3.connect(self.db_path)) as connection:

            with connection:

                connection.execute("""
                    INSERT INTO activities (
                        timestamp,
                        action,
                        details
                    )
                    VALUES (?, ?, ?)
                """, (
                    event.timestamp.isoformat(timespec="seconds"),
                    event.action,
                    event.details
                ))

    def get_all(self):

        with closing(sqlite3.connect(self.db_path)) as connection:

            cursor = connection.execute("""
                SELECT timestamp, action, details
                FROM activities
                ORDER BY id DESC
            """)

            rows = cursor.fetchall()

        events = []

        for row in rows:

            event = ActivityEvent(
                timestamp=datetime.fromisoformat(row[0]),
                action=row[1],
                details=row[2]
            )

            events.append(event)

        return events