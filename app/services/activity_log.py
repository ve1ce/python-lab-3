from datetime import datetime

from PySide6.QtCore import QObject, Signal

from app.models.activity import ActivityEvent


class ActivityLog(QObject):

    # Сигнал изменения журнала
    changed = Signal()

    def __init__(self):
        super().__init__()

        self._events = []

    def add_event(self, action, details):

        # Создаём новое событие
        event = ActivityEvent(
            timestamp=datetime.now(),
            action=action,
            details=details
        )

        # Добавляем событие в начало списка
        self._events.insert(0, event)

        # Сообщаем об изменении журнала
        self.changed.emit()

    def get_events(self):

        # Возвращаем копию списка событий
        return self._events.copy()