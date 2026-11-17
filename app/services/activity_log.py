from datetime import datetime

from PySide6.QtCore import QObject, Signal

from app.models.activity import ActivityEvent


class ActivityLog(QObject):

    # Сигнал изменения истории
    changed = Signal()

    def __init__(self, repository):
        super().__init__()

        self.repository = repository

    def add_event(self, action, details):

        # Создаём событие
        event = ActivityEvent(
            timestamp=datetime.now(),
            action=action,
            details=details
        )

        # Сохраняем его в базе данных
        self.repository.add_event(event)

        # Уведомляем интерфейс
        self.changed.emit()

    def get_events(self):

        # Получаем события из базы
        return self.repository.get_all()