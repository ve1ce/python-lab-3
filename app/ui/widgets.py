from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QLabel, QPushButton, QScrollArea, QTableWidget, QVBoxLayout,
    QWidget,
)

'''текстовая надпись с именем объекта'''
def label(text, name):
    widget = QLabel(text)
    widget.setObjectName(name)
    return widget

'''кнопка с именем объекта'''
def button(text, name, min_height):
    widget = QPushButton(text)
    widget.setObjectName(name)
    widget.setMinimumHeight(min_height)
    return widget

'''создание стандартной структуры страницы с заголовком'''
def page_layout(page, title, subtitle, *, scrollable=False, spacing=20):
    content = page
    if scrollable:
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setObjectName("pageScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QWidget()
        content.setObjectName("pageContent")
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    layout = QVBoxLayout(content)
    layout.setContentsMargins(35, 35, 35, 35)
    layout.setSpacing(spacing)
    layout.addWidget(label(title, "pageTitle"))
    layout.addWidget(label(subtitle, "mutedText"))
    return layout

'''создание карточки (отдельный блок информации)'''
def card(margins=(20, 20, 20, 20), spacing=15):
    frame = QFrame()
    frame.setObjectName("contentCard")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return frame, layout

'''таблица для словаря и истории'''
def read_only_table(headers, row_height, min_height):
    table = QTableWidget(0, len(headers))
    table.setObjectName("dataTable")
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().hide()
    table.verticalHeader().setDefaultSectionSize(row_height)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setMinimumHeight(min_height)
    return table

'''динамическое изменение виджетов (правильный/неправильный ответ кнопка)'''
def set_style_state(widget, state):
    widget.setProperty("state", state)
    # Qt кэширует правила QSS с динамическими свойствами.
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
