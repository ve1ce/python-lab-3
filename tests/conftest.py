import pytest

from app.database import VocabularyRepository, initialize_database
from app.services import VocabularyService


@pytest.fixture
def db_path(tmp_path):

    # Создаём путь к временной базе данных
    path = tmp_path / "test.db"

    # Создаём таблицы и начальные данные
    initialize_database(path)

    return path


@pytest.fixture
def vocabulary_service(db_path):

    # Репозиторий с тестовой базой
    repository = VocabularyRepository(db_path)

    # Сервис для тестирования
    service = VocabularyService(repository)

    return service
