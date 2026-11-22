import random

from PySide6.QtCore import QObject, Signal

#константа уровней сложности заданий
PRACTICE_LEVELS = {5: "Лёгкий", 10: "Средний", 15: "Сложный"}

'''класс посредник между интом и бд'''
class VocabularyService:
    def __init__(self, repository):
        self.repository = repository

    def get_words(self):
        return self.repository.get_words()

    def add_word(self, word, translation):
        return self.repository.add_word(word, translation)

    def delete_word(self, word_id):
        self.repository.delete_word(word_id)

'''класс получения истории пользователя'''
class ActivityLog(QObject):
    changed = Signal()

    def __init__(self, repository):
        super().__init__()
        self.repository = repository

    def get_events(self):
        return self.repository.get_all()

'''генератор подбора слов для заданий'''
def practice_questions(words, question_count=5):
    unique_translations = {}

    for item in words:
        translation = item["translation"]
        unique_translations.setdefault(
            translation.casefold(), translation
        )

    translations = list(unique_translations.values())

    if len(words) < question_count or len(translations) < 4:
        return [], translations

    questions = random.sample(words, question_count)

    return questions, translations

'''4 варианта ответан а 1 вопрос'''
def practice_options(translations, correct_translation):
    wrong_answers = [
        translation for translation in translations
        if translation.casefold() != correct_translation.casefold()
    ]

    options = random.sample(wrong_answers, 3)
    options.append(correct_translation)
    random.shuffle(options)

    return options

'''обзединяет предыдущие алгоритмы для заданий'''
def practice_quiz(words, question_count):
    if question_count not in PRACTICE_LEVELS:
        raise ValueError("Неизвестный уровень сложности")
    questions, translations = practice_questions(words, question_count)
    quiz = []
    for question in questions:
        options = practice_options(translations, question["translation"])
        quiz.append({
            "word": question["word"], "options": options,
            "correct": options.index(question["translation"]),
        })
    return quiz
