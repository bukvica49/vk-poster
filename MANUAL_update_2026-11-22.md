## Изменения 22.11.2026 — карточки дней недели 1020×1020 (пейзаж+буквица), фиксы poster.py и make_preview.py

## Summary
Заменены карточки дней недели: вместо фона «день/ночь» с глючной буквой — 9 карточек den-dnya-0..8.png (1020×1020) с природными пейзажами (лес, скалы, водопад, горы, озеро, луг, каньон, курган; Flux Schnell, генерация БЕЗ текста) и наложенными кодом (Pillow, make_day_card.py) золотой буквицей (А, В, Г, Д, Є, Ѕ, Ȥ, И, Ѳ) и подписями дня без наложений. Патчи: poster.py — фикс _resolve_image для daily ('str' has no 'get'); make_preview.py _add_week_rows — чтение image из JSON (вместо захардкоженного .jpg), нормализация до _p.name, поиск картинки добавлен в images/. Проверено curl и dry-run.

## Content
# Изменения 22.11.2026

### 1. Новые карточки дней (конвейер)

- Пейзажи: нейрогенерация Flux Schnell с явным «NO text» — текст нейро искажает, поэтому надписи НЕ в генерации.
- Надписи: Pillow (make_day_card.py): буквица 300pt золотом (232,186,84) в зоне 6–46% высоты, название+пояснение в зоне 52–94%, полупрозрачные тёмные панели (rgba(20,16,8,110/130)) под текстом — читаемость на любом пейзаже. Перенос по словам, автоподбор размера.
- 9 файлов den-dnya-0..8.png (1020×1020), залиты в images/ (КОРЕНЬ) + копия в images/den-dnya/ (не используется витриной — можно удалить).

### 2. Фикс poster.py (daily падал)

Симптом: AttributeError: 'str' object has no attribute 'get' в daily_items → _resolve_image(img), где img — строка пути, а функция ждёт dict (h.get("image")).
Фикс: img_path = (BASE / img.lstrip("/")) if img else None — резолв строки напрямую.
Скрипт: fix_daily_image.py (идемпотентный, при отсутствии якоря печатает все вызовы _resolve_image).

### 3. Фикс make_preview.py _add_week_rows

- Было: img = f"den-dnya-{_wi}.jpg" — захардкожено, JSON-поле image игнорировалось → на витрине старые картинки.
- Стало: читать image из den-dnya-{_wi}.json; нормализация _p = HERE / path.lstrip("/"); img = _p.name if _p.is_file() else fallback jpg. ВАЖНО: без lstrip('/') путь '/images/...' становится абсолютным от корня ФС → FileNotFoundError (грабля 22.11).
- Цикл поиска _src_img дополнен HERE / "images" / img (наши файлы лежат в images/ корня); старые пути (корень, images/Дни_недели) оставлены как fallback.
- Коммиты: a330195 (JSON-пути + фикс poster), 8cd44b9 (9 png), 83881b5 (копия в images/), ad86b4a+51666ea (патчи _add_week_rows), финал v3 — поиск в images/.

### 4. Правила на будущее

- Картинка дня в JSON: "/images/den-dnya-N.png", файл — плоско в images/.
- Проверка витрины: curl -s https://bukvica49.github.io/vk-poster/ | grep -o 'den-dnya[^"]*' | sort -u
- После пуша Pages деплой 2–5 мин; браузер — Ctrl+F5.
- Старые den-dnya-N.jpg (день/ночь) в images/Дни_недели/ больше не используются — можно удалить.

## Keywords
22.11.2026, карточки дней, den-dnya-0..8.png, 1020x1020, пейзаж, Flux Schnell, NO text, буквица, Pillow, make_day_card.py, poster.py, _resolve_image, daily_items, AttributeError, str get, fix_daily_image.py, make_preview.py, _add_week_rows, захардкожено, lstrip, FileNotFoundError, images/, Дни_недели, a330195, 8cd44b9, 83881b5, ad86b4a, 51666ea, curl grep den-dnya, Ctrl+F5
