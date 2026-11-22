import re
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from web import main


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(main, "initialize_database", lambda: None)
    with TestClient(main.app) as client:
        yield client


def make_words(count, translations=None):
    translations = translations or count
    return [
        {"id": i, "word": f"word-{i}", "translation": f"перевод-{i % translations}"}
        for i in range(count)
    ]


@pytest.mark.parametrize("count", [5, 10, 15])
def test_start_practice_creates_distinct_questions(client, monkeypatch, count):
    words = make_words(16, translations=4)
    monkeypatch.setattr(main.repository, "get_words", lambda: words)
    sessions = {}
    monkeypatch.setattr(main, "create_practice", sessions.__setitem__)

    response = client.post("/practice/start", data={"count": count}, follow_redirects=False)

    assert response.status_code == 303
    session_id = UUID(response.headers["location"].split("/")[-1])
    questions = sessions[session_id]
    assert len(questions) == len({question["word"] for question in questions}) == count
    translations = {word["word"]: word["translation"] for word in words}
    for question in questions:
        assert len(question["options"]) == len(set(question["options"])) == 4
        assert question["options"][question["correct"]] == translations[question["word"]]


@pytest.mark.parametrize(
    ("word_count", "translation_count", "available", "unavailable"),
    [(8, 8, {5}, 10), (15, 3, set(), 5), (4, 4, set(), 5)],
)
def test_practice_disables_unavailable_levels(
    client, monkeypatch, word_count, translation_count, available, unavailable,
):
    words = make_words(word_count, translation_count)
    monkeypatch.setattr(main.repository, "get_words", lambda: words)
    created = []
    monkeypatch.setattr(main, "create_practice", lambda *args: created.append(args))

    response = client.get("/practice")
    assert response.status_code == 200
    buttons = re.findall(r'name="count" value="(\d+)"\s*(disabled)?\s*>', response.text)
    assert len(buttons) == 3
    assert {int(count) for count, disabled in buttons if not disabled} == available

    response = client.post("/practice/start", data={"count": unavailable})
    assert response.history[0].status_code == 303
    assert "Для выбранного уровня сейчас недостаточно" in response.text
    assert created == []


def test_main_pages_show_navigation_and_empty_activity(client, monkeypatch):
    monkeypatch.setattr(main, "get_dashboard", lambda today: ((8, 0, 0), {}, []))
    monkeypatch.setattr(main.ActivityRepository, "get_all", lambda self: [])
    monkeypatch.setattr(main.repository, "get_words", lambda: make_words(8))

    pages = {
        "/": "Активность за неделю",
        "/vocabulary": "Мои слова",
        "/practice": "Тренировка перевода",
        "/history": "Всего событий: 0",
    }
    for path, heading in pages.items():
        response = client.get(path)
        assert response.status_code == 200
        assert heading in response.text
        assert 'aria-current="page"' in response.text
        assert all(f'href="{link}"' in response.text for link in pages)
    assert "Пока нет записанных действий" in client.get("/history").text
    assert client.get("/").text.count('class="chart-bar"') == 7
    assert client.get("/static/styles.css").status_code == 200
