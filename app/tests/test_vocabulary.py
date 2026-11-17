import pytest

from app.exceptions import VocabularyValidationError

from app.database.vocabulary_repository import VocabularyRepository
from app.services.vocabulary_service import VocabularyService


def test_initial_words(vocabulary_service):

    # Получаем слова из базы
    words = vocabulary_service.get_words()

    # Проверяем количество начальных слов
    assert len(words) == 8

    # Проверяем наличие слова apple
    assert {
        "word": "apple",
        "translation": "яблоко"
    } in words


def test_add_word(vocabulary_service):

    # Добавляем новое слово
    vocabulary_service.add_word(
        "computer",
        "компьютер"
    )

    # Получаем обновлённый словарь
    words = vocabulary_service.get_words()

    # Проверяем, что слово добавилось
    assert {
        "word": "computer",
        "translation": "компьютер"
    } in words

    assert len(words) == 9


def test_word_persistence(db_path, vocabulary_service):

    # Добавляем слово с лишними пробелами
    vocabulary_service.add_word(
        "  hello  ",
        "  привет  "
    )

    # Создаём новый репозиторий и сервис
    new_repository = VocabularyRepository(db_path)

    new_service = VocabularyService(
        new_repository
    )

    # Проверяем сохранение данных
    words = new_service.get_words()

    assert {
        "word": "hello",
        "translation": "привет"
    } in words


def test_duplicate_word(vocabulary_service):

    # Проверяем обработку дубликата
    with pytest.raises(
        VocabularyValidationError,
        match="Такое слово уже есть"
    ):

        vocabulary_service.add_word(
            "APPLE",
            "другое значение"
        )


@pytest.mark.parametrize(
    "word, translation",
    [
        ("", "привет"),
        ("hello", ""),
        ("   ", "привет"),
        ("hello", "   ")
    ]
)
def test_empty_fields(
    vocabulary_service,
    word,
    translation
):

    # Проверяем некорректные данные
    with pytest.raises(
        VocabularyValidationError,
        match="Заполните оба поля"
    ):

        vocabulary_service.add_word(
            word,
            translation
        )


def test_delete_word(vocabulary_service):

    # Удаляем существующее слово
    vocabulary_service.delete_word("apple")

    words = vocabulary_service.get_words()

    # Проверяем, что слово удалено
    assert not any(
        item["word"] == "apple"
        for item in words
    )

    assert len(words) == 7


def test_delete_missing_word(vocabulary_service):

    # Пытаемся удалить несуществующее слово
    with pytest.raises(
        VocabularyValidationError,
        match="Слово не найдено"
    ):

        vocabulary_service.delete_word(
            "nonexistent"
        )