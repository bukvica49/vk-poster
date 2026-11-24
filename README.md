# vk-poster

Автопостинг славянского календаря (Коляды Даръ) в группу VK.

## Что делает
- Генерирует посты по Круголѣту Числобога: чертоги, стихии,
  дни 9-дневки, буквицы — всё считает движок calendar_engine.py.
- Карточки постов лежат в content/holidays/*.json.
- Выкладывает посты в вечерний слот (см. POST_WINDOW_HOURS в poster.py).

## Канон
- Единственный якорь дат — в calendar_engine.py, других точек отсчёта нет.
- Дни недели и буквицы берутся только из движка:
  weekday_and_bukvica(date) (коммит 5590a37).
- Файлы den-dnya-0..8.json соответствуют индексам дней 9-дневки 0..8.

## Команды

Сухой прогон (не тратит вызовы API):
    python3 poster.py --dry-run

Проверка синтаксиса:
    python3 -m py_compile poster.py calendar_engine.py

Сверка дня недели и буквицы:
    python3 -c "from datetime import date; import calendar_engine as ce; print(ce.weekday_and_bukvica(date(2026,11,24)))"

## Структура
- poster.py — автопостинг, слоты, анти-дубль, гвард бюджета.
- calendar_engine.py — движок Круголѣта, единственный источник дат.
- slavic_auto.py — блоки шапки: чертоги, Лѣто, стихии.
- bukvicy.py — кириллическая цифирь (҂ȤФЛЄ).
- content/holidays/*.json — карточки постов.
- HANDOFF.md — операционный мануал (что ломалось и как чинить).
