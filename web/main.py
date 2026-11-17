from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from uuid import UUID, uuid4

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.exceptions import VocabularyValidationError
from app.services import practice_options, practice_questions
from web.database import (
    VocabularyRepository, create_practice, get_activities, get_connection,
    get_dashboard, get_practice, initialize_database, update_practice,
)


BASE_DIR = Path(__file__).resolve().parent
repository = VocabularyRepository()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Изучение иностранных языков",
    lifespan=lifespan
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)

PAGES = {
    "/": "Главная",
    "/vocabulary": "Словарь",
    "/practice": "Практика",
    "/history": "История"
}
PRACTICE_LEVELS = {5: "Лёгкий", 10: "Средний", 15: "Сложный"}


def render_page(request, path, **context):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": PAGES[path],
            "pages": PAGES,
            "current_path": path,
            **context
        }
    )


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    today = date.today()
    counts, daily_counts, recent = get_dashboard(today)
    dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    week = [(day, daily_counts.get(day, 0)) for day in dates]
    step = max(1, (max(count for _, count in week) + 3) // 4)
    scale = range(step * 4, -1, -step)
    return render_page(request, "/", counts=counts, week=week, scale=scale, recent=recent)


@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    with get_connection() as connection:
        events = get_activities(connection)
    return render_page(request, "/history", events=events)


@app.get("/practice", response_class=HTMLResponse)
def practice_levels(request: Request, unavailable: bool = False):
    words = repository.get_words()
    translation_count = len({item["translation"].casefold() for item in words})
    return render_page(
        request, "/practice", levels=PRACTICE_LEVELS, word_count=len(words),
        translation_count=translation_count, unavailable=unavailable,
    )


@app.post("/practice/start")
def start_practice(count: int = Form()):
    if count not in PRACTICE_LEVELS:
        raise HTTPException(400, "Неизвестный уровень сложности")

    questions, translations = practice_questions(repository.get_words(), count)
    if not questions:
        return RedirectResponse("/practice?unavailable=1", status_code=303)

    quiz = []
    for question in questions:
        options = practice_options(translations, question["translation"])
        quiz.append({
            "word": question["word"], "options": options,
            "correct": options.index(question["translation"]),
        })
    session_id = uuid4()
    create_practice(session_id, quiz)
    return RedirectResponse(f"/practice/{session_id}", status_code=303)


@app.get("/practice/{session_id}", response_class=HTMLResponse)
def practice_session(request: Request, session_id: UUID):
    session = get_practice(session_id)
    if session is None:
        raise HTTPException(404, "Тренировка не найдена")
    return render_page(request, "/practice", session=session)


@app.post("/practice/{session_id}")
def submit_practice(
    session_id: UUID, index: int = Form(ge=0), choice: Optional[int] = Form(None, ge=0, le=3),
):
    if not update_practice(session_id, index, choice):
        raise HTTPException(404, "Тренировка не найдена")
    return RedirectResponse(f"/practice/{session_id}", status_code=303)


@app.get("/vocabulary", response_class=HTMLResponse)
def vocabulary(
    request: Request,
    q: str = "",
    message: str = "",
    error: bool = False
):
    words = repository.get_words()
    search = q.strip().casefold()

    filtered_words = [
        item for item in words
        if search in item["word"].casefold()
        or search in item["translation"].casefold()
    ]

    return render_page(
        request,
        "/vocabulary",
        words=filtered_words,
        total=len(words),
        q=q,
        message=message,
        error=error
    )


def vocabulary_redirect(message, error=False):
    params = urlencode({
        "message": message,
        "error": int(error)
    })

    return RedirectResponse(
        url=f"/vocabulary?{params}",
        status_code=303
    )


@app.post("/vocabulary/add")
def add_word(
    word: str = Form(""),
    translation: str = Form("")
):
    try:
        repository.add_word(word, translation)
    except VocabularyValidationError as error:
        return vocabulary_redirect(str(error), error=True)

    return vocabulary_redirect("Слово успешно добавлено")


@app.post("/vocabulary/delete")
def delete_word(word_id: int = Form()):
    try:
        repository.delete_word(word_id)
    except VocabularyValidationError as error:
        return vocabulary_redirect(str(error), error=True)

    return vocabulary_redirect("Слово успешно удалено")
