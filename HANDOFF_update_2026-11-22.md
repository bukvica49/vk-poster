## 2026-11-22 — карточки дней den-dnya-N.png (пейзаж+буквица), фиксы poster.py и make_preview.py

## Summary
Дни недели переведены на новые карточки den-dnya-0..8.png (1020×1020): пейзажи (Flux, NO text) + буквица/подписи Pillow (make_day_card.py). Файлы плоско в images/, в JSON поле "image": "/images/den-dnya-N.png". Фиксы: poster.py daily_items (резолв строки пути вместо dict), make_preview.py _add_week_rows (image из JSON, _p.name-нормализация, поиск в images/). Старые den-dnya-N.jpg больше не используются.

## Content
# 2026-11-22 — карточки дней недели

### Что изменилось
- 9 карточек den-dnya-0..8.png (1020×1020): пейзаж (Flux Schnell, генерация без текста) + золотая буквица и подписи, наложенные Pillow (make_day_card.py). Текст нейро-генерацией НЕ делаем — искажает.
- Файлы: images/den-dnya-0..8.png (плоско). JSON: content/holidays/den-dnya-0..8.json, поле "image": "/images/den-dnya-N.png".
- Постер: карточка одна (уже с текстом), патч «2 картинки» не нужен.
- Витрина: _add_week_rows теперь читает image из JSON, нормализует до _p.name (плоское имя) и ищет файл в HERE/images/, HERE/, HERE/images/Дни_недели/ (fallback).

### Грабли (НЕ повторять)
1. _resolve_image ждёт dict (h.get) — в daily_items img это СТРОКА пути: резолвить BASE / img.lstrip("/"), не передавать в _resolve_image.
2. Путь JSON с ведущим "/" в HERE / img без lstrip → абсолютный путь от корня ФС → FileNotFoundError.
3. _add_week_rows искал картинку только в HERE/ и images/Дни_недели/ — файлы в images/ не находились → «нет фото»; добавлен HERE / "images" / img.
4. Кэш браузера на витрине — только Ctrl+F5; Pages деплой после пуша 2–5 мин.

### Коммиты 22.11.2026
| Коммит | Что |
|---|---|
| a330195 | JSON-пути /images/den-dnya-N.png + фикс _resolve_image в poster.py |
| 8cd44b9 | 9 карточек png в images/den-dnya/ |
| 83881b5 | копия png в images/ (корень) для витрины |
| ad86b4a | _add_week_rows: image из JSON (v1, без lstrip — падение) |
| 51666ea | нормализация _p.name (v2) |
| (v3) | поиск в images/ — все 9 png на витрине |

### Проверка
python3 poster.py --dry-run            # [фото: den-dnya-N.png ✓]
python3 make_preview.py                # 79 постов
curl -s https://bukvica49.github.io/vk-poster/ | grep -o 'den-dnya[^"]*' | sort -u   # 9 png

## Keywords
2026-11-22, den-dnya-N.png, карточки дней, пейзаж, буквица, Pillow, make_day_card.py, poster.py, _resolve_image, daily_items, make_preview.py, _add_week_rows, lstrip, images/, fix_daily_image.py, a330195, 8cd44b9, 83881b5, ad86b4a, 51666ea
