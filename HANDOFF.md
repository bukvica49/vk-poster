# HANDOFF — контекст для AI

Обновлено: 2026-11-03
Владелец: pokep (pokep-All-Series)
Репо: ~/vk-poster (git: bukvica49/vk-poster)
VK-группа: 200796423, «Родная Традиция»

## Что это
Автопостер ВК на славянском календаре (9-дневная неделя, Коляды Дар).
Автозапуск: GitHub Actions, cron `0 11 * * *` UTC = 18:00 KRAT.
Каждый день: slavic_now() -> найти праздник на «завтрашний» слав. день ->
пост в VK -> git push state через DEPLOY_KEY. ПК может быть выключен.

Секреты GitHub (Settings -> Secrets -> Actions):
- `VK_CONFIG`  — содержимое config.main.json
- `DEPLOY_KEY` — приватный SSH (fingerprint: SHA256:wIS9WCBCR9u2IzIPI4aiHTIXcwHLQiJgPUy/k0Kl278)

## Ключевые решения (НЕ переспрашивать)
1. Пост 18:00 = слав. «завтра». Слав. день с заката.
   Родомир (слав. 06.11) постится 05.11 вечером.
2. Ключ state = `YYYY-MM-DD|text[:40]`. Год в ключе -> 2027 пересчитается сам.
3. Многодневный праздник (Неделя Праотцев) = отдельная запись на каждый день,
   свой image. Разные image -> разные text_md (патч hd_img).
4. Несколько праздников в один день = норма, только `text` должен различаться.
5. Фото в КОРНЕ vk-poster/, не в подпапке. Через PagesCMS Upload.
6. Праздники правятся через app.pagescms.org/bukvica49/vk-poster
7. Источник данных = `content/holidays/*.json` (PagesCMS collection,
   1 файл = 1). Старый `holidays.json` (массив) удалён в c3e1b60.

## Что починено
- fa4a1af: постинг без фото -> FAIL main=1 (раньше уходил без фото)
- патч: text_md подбирается по (text, image), не только по text
  проверка: grep -c "hd_img" poster.py  -> должно быть >= 2
- 2026-11-03: шапка поста перестроена:
  * шапка → в НАЧАЛО (было в конец)
  * Чертог в шапке с полом: «Бог-Покровитель» / «Богиня-Покровительница»
  * «🌳 Священное Древо: <порода>» — в шапке
  * «от С.М.З.Х.» приклеено к строке 1 (без строки-дубля)
  * сдвиг Чертогов +1 (индекс CHERTOG_STARTS в chertogs.json)
  проверка: python3 poster.py config.main.json --dry-run
- c3e1b60: holidays.json → content/holidays/*.json (PagesCMS collection)
- e30c509: кнопки ✏️/📋 в правом верхнем углу карточки превью
- 0b2473b: ➕ Новый праздник в шапке превью
- d30a506: toolbar ровно — убран inline-style margin-left:auto
  (перебивал .secondary{margin-left:6px} → gap=0)

## Файлы
- poster.py             — код (main(), holidays_today(), load_state(),
                           сборка шапки поста в НАЧАЛЕ)
- slavic_auto.py        — build_info(day): Чертог + пол + Древо + Круголет
- slavic_calendar.py    — календарь, header(day)
- chertogs.json         — массив Чертогов + CHERTOG_STARTS (индекс начала)
- tools/build_site_slavic_js.py — генератор js/slavic-date.js для сайта
- md_to_vk.py           — Markdown -> VK
- content/holidays/*.json — праздники (PagesCMS collection, 1 файл = 1)
- make_preview.py       — генератор _site/ (кнопки + deep-link)
- .github/workflows/pages.yml — автодеплой превью на push в main
- config.main.json      — токены (НЕ в git, НЕ в чат)
- state-200796423.json  — что уже постил
- MANUAL.md             — шпаргалка для владельца
- run_poster.sh         — cron wrapper

## Диагностика (первое, что делать при «сломалось»)
tail -5  ~/vk-poster/log-runs.txt      # main=0 ок, main=1 упало, sync!=0 pull упал
tail -20 ~/vk-poster/log-main.txt      # конкретная причина
cd ~/vk-poster && python3 poster.py config.main.json --dry-run   # что будет запощено

## Известные причины отказа
- getWallUploadServer 27 или 5 -> user_token просрочен (vkhost.github.io -> VK Admin)
- «Файл не найден» -> фото нет в репо (залить через PagesCMS в корень)
- sync!=0 -> конфликт git pull (смотреть log-sync.txt)

## Формат шапки поста (2026-11-04, финальный)

СЕДМИЦА · 4 Айлѣтъ Сороковнiкъ (Мѣсꙗцъ) Новых Даровъ · Лѣто ҂ЗФЛЕ(7535)  Ѿ  С.М.З.Х.
⚡ Чертог Щуки – Богиня-Покровительница Рожана ⚡
🌳 Священное Древо: Слива.
● 15-є Лѣтъ (из 16-ти) в Крɣгє лѣтъ;
● 15-є Лѣтъ (из 144-х) в Крɣгє Жизни;
● Круголѣт: Хоромы (дом);
● Стихия: Луна;
● Цвет: фиолѣт.

Порядок: шапка сверху → тело поста → фото.
Сборка: header_full() в slavic_calendar.py;
        вызывается из poster.py (line 237) и make_preview.py (line 98);
        тело поста = slavic_auto.build_info(day) + chertogs.json.

## Превью-сайт (bukvica49.github.io/vk-poster)
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

## Сайт (~/site/bukvica49.github.io-main)
Отдельный репо bukvica49/bukvica49.github.io (~/site/...), GitHub Pages.
js/slavic-date.js — СГЕНЕРИРОВАННЫЙ, не править руками.
Синхронизация после правки Чертогов:

    cd ~/vk-poster && python3 tools/build_site_slavic_js.py

Генератор сам бампает ?v=N в index.html + nav/*.html.
Подробности: ~/site/bukvica49.github.io-main/MANUAL.md

## Правила для AI в новом чате
1. Сначала прочитай HANDOFF.md и MANUAL.md — весь контекст там.
2. По пункту «Ключевые решения» — НЕ переспрашивать, они согласованы.
3. Диагностика = ОДНА команда в чат, не список из пяти.
4. Патч = сначала текст в чате, потом команда. Не вслепую.
5. Не спрашивать «A или B?» без оговорки «по умолчанию делаю X».
6. Не гадать про «шапку с 8-ми пунктами» — это старая непонятая тема,
   если всплывёт, уточнять у владельца конкретно.

- 2026-11-03: make_preview.py — published посты (есть в state) сразу уезжают
  вниз с ⏳ {след. год} (не ждут 18:00, не показывают ✅).
  Логика: `if f"{occ}|{text}" in posted: occ = occ.year + 1`.
  Badge всегда ⏳. Проверка: grep -c "✅ отправлено" _site/index.html → 0

---

## 🔒 ФИНАЛ 2026-11-03 — fire-логика подтверждена, 3 фикса

### Что работает (НЕ ТРОГАТЬ)
- `slavic_calendar.slavic_now()` возвращает `today + 1` после 18:00 KRAT.
  Это **источник fire-логики**. State-key = target day (actual). 
- `poster.py holidays_today(today)` фильтрует `d == today` где today уже сдвинут на +1 после 18:00 → пост выходит накануне в 18:00. **Правильно.**
- Ручной пост Мирослава 31.10 → state-key `2026-11-01` — это target day, не fire. **Не путать.**

### Что починено
- **P1 (make_preview.py):** `today_civil = slavic_calendar.today_krat()` (было `date.today()` = UTC на GH Actions → превью отставало на 1 день в 00:00–07:00 KRAT)
- **P2 (poster.py):** state-key = полный `text` (было `text[:40]` — длинные праздники «висели» в превью после публикации)
- **P3 (content/holidays/den-miroslava-tariyskogo.json):** удалён битый `slavic` ({month:Айлетъ, day:2} → парсился как 21.09). Источник = `date=11-01` → fire всегда **31.10 18:00**. Проверено 2026/2027/2028.

### Что НЕ ДЕЛАТЬ (потеряно 4 часа на ложные гипотезы)
- ❌ **P4:** не сдвигать `holidays_today(today + 1)` — `slavic_now()` уже +1 → посты выйдут на 2 дня раньше.
- ❌ **while-цикл для state** — не нужен, `slavic_now()` уже поднимает год.
- ❌ **Удалять/пересоздавать 52 праздника** — данные чистые (51/52 OK, 1 битый = Мирослав, исправлен).
- ❌ **Мигрировать state 2026** — корректен (target day, не fire day).

### Расписание на 2027 (проверка)
| Праздник | fire (KRAT) | target day (state) |
|---|---|---|
| Дидовъ | 28.10.2027 18:00 | 2027-10-29 |
| Мирослав | 31.10.2027 18:00 | 2027-11-01 |
| Харий | 02.11.2027 18:00 | 2027-11-03 |
| Лебедь | 03.11.2027 18:00 | 2027-11-04 |

### Контроль после любых правок

```bash
python3 -c "from slavic_calendar import slavic_now, today_krat; print(slavic_now(), today_krat())"
python3 make_preview.py && python3 poster.py --dry-run
```

**Последний успешный HEAD:** `834409e` (TZ + state-key + Мирослав).
**Покрыто фиксами:** `make_preview.py`, `poster.py`, `content/holidays/den-miroslava-tariyskogo.json`.
