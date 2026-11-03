#!/usr/bin/env python3
"""patch_manual_handoff.py — MANUAL.md + HANDOFF.md после перехода на
content/holidays/*.json и превью-сайт с кнопками. Идемпотентно."""
import re
from pathlib import Path

MANUAL  = Path(__file__).parent / 'MANUAL.md'
HANDOFF = Path(__file__).parent / 'HANDOFF.md'

NEW_ADD = """## Добавить праздник — через превью
https://bukvica49.github.io/vk-poster/ → `➕ Новый` в шапке → форма PagesCMS.

1. Заполнить поля
2. Save → PagesCMS auto-commit в `content/holidays/{slug}.json`
3. Через 1-2 мин — live (деплой: `.github/workflows/pages.yml`)

## Прямо в PagesCMS
https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays

`content/holidays/*.json` — **1 файл = 1 праздник** (не массив).

Поля:
- `date`    — обязательно, `MM-DD` (не `DD-MM`)
- `text`    — обязательно, заголовок поста
- `slug`    — опционально (= имя файла; PagesCMS ставит автоматически)
- `text_md` — опционально, Markdown-тело поста (если пусто — берётся `text`)
- `info`    — опционально, массив строк внизу поста
- `info_md` — опционально, Markdown-версия `info[]`
- `image`   — опционально, имя файла в КОРНЕ репо (Upload через PagesCMS)
- `slavic`  — опционально, `{month, day}` — точный слав. день, перебивает
              пересчёт из `date` (для «плавающих» праздников). Читает только
              `poster.py`; `make_preview.py` — не использует.

Фото: Upload в корень репо через PagesCMS.

## Работа через превью
https://bukvica49.github.io/vk-poster/

Кнопки шапки (слева→справа):
- `📅 Праздники` — collection/holidays
- `🕯 Чертоги`   — file/chertogs
- `🌀 Круголеты` — file/krugolyety
- `➕ Новый`     — collection/holidays/new

Кнопки карточки (верхний правый угол):
- `✏️` — edit deep-link: `/edit/content%2Fholidays%2F{slug}.json`
- `📋` — текст поста → clipboard → `Ctrl+V` в VK

Deep-link slug URL-encoded (content%2Fholidays%2F{slug}.json).
Ctrl+Shift+R — hard refresh (если live не обновился после push).

"""

NEW_PREVIEW_HANDOFF = """## Превью-сайт (bukvica49.github.io/vk-poster)
Отдельно от `~/site/bukvica49.github.io-main` — страница праздников.

- URL:        https://bukvica49.github.io/vk-poster/
- Генератор:  `make_preview.py` → `_site/index.html`
- Автодеплой: `.github/workflows/pages.yml` (push в `main`)
- Данные:     `content/holidays/*.json`

Кнопки шапки: 📅 Праздники / 🕯 Чертоги / 🌀 Круголеты / ➕ Новый
Кнопки карточек: ✏️ edit / 📋 copy

⚠️ НЕ ломать:
- gap между secondary = `.secondary{margin-left:6px}`
- НЕ добавлять inline `margin-left:auto` — перебьёт gap (баг d30a506)
- slug URL-encoded: `content%2Fholidays%2F{slug}.json`

"""

def patch_manual():
    src = MANUAL.read_text(encoding='utf-8')
    if '## Работа через превью' in src:
        print('  MANUAL:  уже обновлён (skip)'); return
    # 1. Заменить ## Добавить праздник (до ## Несколько дней)
    new_src = re.sub(
        r'## Добавить праздник\n.*?(?=## Несколько дней подряд)',
        NEW_ADD, src, count=1, flags=re.DOTALL)
    if new_src == src:
        print('  MANUAL:  !! ## Добавить праздник не найден — проверь'); return
    src = new_src
    # 2. ## Файлы — holidays.json -> content/holidays/*.json + make_preview.py
    old = 'holidays.json               — праздники (PagesCMS)'
    new = ('content/holidays/*.json       — праздники (PagesCMS collection, 1 файл = 1)\n'
           'make_preview.py               — генератор _site/ (превью-сайт с кнопками)')
    if old in src: src = src.replace(old, new, 1)
    # 3. .github/workflows/pages.yml
    old = '.github/workflows/post.yml  — автозапуск через Actions'
    new = ('.github/workflows/post.yml  — автозапуск постинга\n'
           '.github/workflows/pages.yml — автодеплой превью на push в main')
    if old in src: src = src.replace(old, new, 1)
    MANUAL.write_text(src, encoding='utf-8')
    print('  MANUAL:  обновлён ✓')

def patch_handoff():
    src = HANDOFF.read_text(encoding='utf-8')
    if '## Превью-сайт' in src:
        print('  HANDOFF: уже обновлён (skip)'); return
    # 1. ## Ключевые решения — п.7 после п.6
    old = '6. Праздники правятся через app.pagescms.org/bukvica49/vk-poster'
    new = (old + '\n'
           '7. Источник данных = `content/holidays/*.json` (PagesCMS collection,\n'
           '   1 файл = 1). Старый `holidays.json` (массив) удалён в c3e1b60.')
    if old in src: src = src.replace(old, new, 1)
    # 2. ## Что починено — 4 записи в конец (перед ## Файлы)
    old = '  проверка: python3 poster.py config.main.json --dry-run'
    new = (old
           + '\n- c3e1b60: holidays.json → content/holidays/*.json (PagesCMS collection)'
           + '\n- e30c509: кнопки ✏️/📋 в правом верхнем углу карточки превью'
           + '\n- 0b2473b: ➕ Новый праздник в шапке превью'
           + '\n- d30a506: toolbar ровно — убран inline-style margin-left:auto\n'
             '  (перебивал .secondary{margin-left:6px} → gap=0)')
    idx = src.rfind(old)
    if idx >= 0: src = src[:idx] + new + src[idx+len(old):]
    # 3. ## Файлы — holidays.json -> 3 строки
    old = '- holidays.json         — праздники'
    new = ('- content/holidays/*.json — праздники (PagesCMS collection, 1 файл = 1)\n'
           '- make_preview.py       — генератор _site/ (кнопки + deep-link)\n'
           '- .github/workflows/pages.yml — автодеплой превью на push в main')
    if old in src: src = src.replace(old, new, 1)
    # 4. ## Превью-сайт — перед ## Сайт (~/site/...)
    old = '## Сайт (~/site/bukvica49.github.io-main)'
    new = NEW_PREVIEW_HANDOFF + old
    if old in src: src = src.replace(old, new, 1)
    HANDOFF.write_text(src, encoding='utf-8')
    print('  HANDOFF: обновлён ✓')

if __name__ == '__main__':
    patch_manual()
    patch_handoff()
    print('OK. Проверь diff и коммить.')
