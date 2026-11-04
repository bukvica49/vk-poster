# HANDOFF — контекст для AI

Обновлено: 2026-11-04
Владелец: pokep (pokep-All-Series)
Репо: ~/site/vk-poster (git: bukvica49/vk-poster)
VK-группа: 200796423, «Родная Традиция»

## Что это
Автопостер ВК на славянском календаре (9-дневная неделя, Коляды Дар).
Автозапуск: GitHub Actions, cron `0 11 * * *` UTC = 18:00 KRAT.
Каждый день: slavic_now() = datetime.now(KRAT).date() -> найти праздник
с `date = сегодня` в content/holidays/*.json -> пост в VK -> git push state
через DEPLOY_KEY. ПК может быть выключен.

⚠️ `date` в JSON = гражданский день поста в 18:00 KRAT (канун праздника;
слав. сутки с заката). Пример: «День Мирослава» 1 ноября → `date="10-31"` →
пост 31.10 18:00 KRAT.

Секреты GitHub (Settings -> Secrets -> Actions):
- `VK_CONFIG`  — содержимое config.main.json
- `DEPLOY_KEY` — приватный SSH (fingerprint: SHA256:wIS9WCBCR9u2IzIPI4aiHTIXcwHLQiJgPUy/k0Kl278)

## Ключевые решения (НЕ переспрашивать)
1. Пост 18:00 = канун праздника (слав. сутки с заката).
   Пример: Родомир 06.11 → JSON `date="11-05"` → пост 05.11 18:00 KRAT.
   `date` в JSON = день поста, НЕ день праздника.
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
tail -5  ~/site/vk-poster/log-runs.txt      # main=0 ок, main=1 упало, sync!=0 pull упал
tail -20 ~/site/vk-poster/log-main.txt      # конкретная причина
cd ~/site/vk-poster && python3 poster.py --dry-run   # что будет запощено (--date YYYY-MM-DD — конкретная дата)

## Известные причины отказа
- getWallUploadServer 27 или 5 -> user_token просрочен (vkhost.github.io -> VK Admin)
- «Файл не найден» -> фото нет в репо (залить через PagesCMS в корень)
- sync!=0 -> конфликт git pull (смотреть log-sync.txt)

## Формат шапки поста (2026-11-05: 3 строки, по два пробела вокруг ѿ)

⚠️ Шапка описывает **день праздника** = `krugолет(fire_date + 1)`, НЕ fire-дату.
Причина: пост выходит в 18:00 кануна = в начале слав. суток праздника
(слав. сутки идут с заката). Пример: fire=05.11 (Родомир, `date="11-05"`),
праздник=06.11 → шапка `7-го Айлѣтъ ПОНЕДѢЛЬНИКЪ` (НЕ `6-го Айлѣтъ НЕДѢЛѦ`).

Тот же паттерн для fire=31.10 → праздник=01.11 (Мирослав):
шапка `2-го Айлѣтъ ПѦТНИЦА` (НЕ `1-го Айлѣтъ ЧЕТВЕРИКЪ`).

⚠️ **Тело поста** следует ТОЙ ЖЕ логике: `build_info(fire_date + 1)`.
Без этого шапка говорит «Чертог Лебедя» (день праздника), а тело —
«Чертог Щуки» (fire-день). Патч 2026-11-05, 3 call sites:
`poster.py` (load_holidays + holidays_for_year), `make_preview.py`.
State-key по-прежнему на fire-дате.

Затронуто только 3 праздника, где Чертог меняется в полночь fire→праздник:
Лебедь (`11-03`), Купало (`06-20`), Праотцев-7 (`01-07`).

Сєго днꙗ: въ Лѣтъ ҚЗФЛЕ (7535)  ѿ  С.М.З.Х.,
7-го Айлѣтъ - Сороковнiка (Мѣсꙗцъ) Новых Даровъ, ПОНЕДѢЛЬНИКЪ,
(с 18.00, 5-го ноября, 2026 г., до 18.00, 6-го ноября, 2026 г. местн.вр.)
⚡ Чертог Лебедя – Богиня-Покровительница Макошь ⚡
🌳 Священное Древо: Сосна.
● 15-є Лѣтъ (из 16-ти) в Крɣгє лѣтъ;
● 15-є Лѣтъ (из 144-х) в Крɣгє Жизни;
● Круголѣт: Хоромы (дом);
● Стихия: Луна;
● Цвет: фиолѣт.

Порядок: шапка сверху → тело поста → фото.
Сборка: header_full() в slavic_calendar.py;
        вызывается из poster.py и make_preview.py;
        тело поста = slavic_auto.build_info(day + 1) + chertogs.json  # day = fire_date
Двойные пробелы вокруг «ѿ» — намеренно (VK сохраняет; локальное превью — CSS .slavic{white-space:pre-wrap}).
Старая header() — legacy однострочная (для постов НЕ использовать).
  Используется в `poster.py::_slavic_parse()` — парсит « · » для календарных расчётов.

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

    cd ~/site/vk-poster && python3 tools/build_site_slavic_js.py

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
- `slavic_calendar.slavic_now()` = `datetime.now(KRAT).date()` — **без сдвигов**.
- Eve-shift делает **сам JSON** через `date` — не код.
  State-key = `date` из JSON = гражданский день, в 18:00 которого вышел пост (fire day). 
- `poster.py holidays_today(today)` фильтрует `d == today`, где `today = slavic_now()` = **сегодняшняя гражданская дата по KRAT** (без сдвигов). Пост в 18:00 самого `date` из JSON = канун праздника. **Правильно.**
- Ручной пост Мирослава 31.10.2026 → state-key `2026-11-01|…` — **исторический артефакт** старой логики (`date="11-01"` + `slavic_now=+1`). Под вариантом A с 2027 key = `date` = fire day (для Мирослава → `2027-10-31|…`). **Не путать.**

### Что починено
- **P1 (make_preview.py):** `today_civil = slavic_calendar.today_krat()` (было `date.today()` = UTC на GH Actions → превью отставало на 1 день в 00:00–07:00 KRAT)
- **P2 (poster.py):** state-key = полный `text` (было `text[:40]` — длинные праздники «висели» в превью после публикации)
- **P3 (den-miroslava-tariyskogo.json):** удалён битый `slavic` ({month:Айлетъ, day:2} → парсился как 21.09). Текущий файл: `date="10-31"` → пост 31.10 18:00 KRAT. (Ключ state сменился: было `2026-11-01|…` по старой логике, стало `2026-10-31|…`. 2026 уже отработал по старому, для 2027 пойдёт по-новому.)

### Что НЕ ДЕЛАТЬ (потеряно 4 часа на ложные гипотезы)
- ❌ **P4 (историческая ловушка):** не добавлять `+1` в `holidays_today(today + 1)` — раньше это компенсировало `+1` в `slavic_now`. Сейчас `slavic_now` = `today` без сдвигов; `today+1` даст посты на 1 день позже. Eve-shift — только в `date` JSON.
- ❌ **while-цикл для state** — не нужен, `slavic_now()` уже поднимает год.
- ❌ **Удалять/пересоздавать 52 праздника** — данные чистые (51/52 OK, 1 битый = Мирослав, исправлен).
- ❌ **Мигрировать state 2026** — ключи `2026-…`; в 2027 пойдут `2027-…`; коллизий нет, миграция не нужна.

### Расписание на 2027 (вариант A: state-key = `date` = fire day)
| Праздник | JSON date | fire (KRAT) | state-key |
|---|---|---|---|
| Дидовъ | `10-28` | 28.10.2027 18:00 | `2027-10-28\|…` |
| Мирослав | `10-31` | 31.10.2027 18:00 | `2027-10-31\|…` |
| Харий | `11-02` | 02.11.2027 18:00 | `2027-11-02\|…` |
| Лебедь | `11-03` | 03.11.2027 18:00 | `2027-11-03\|…` |

Проверка: `python3 -c "import poster; from datetime import date; \
[print(d, [t[:40] for t,_,_ in poster.holidays_today(date(2027,*map(int,d.split('-'))))]) \
for d in ['10-28','10-31','11-02','11-03']]"`

### Контроль после любых правок

```bash
python3 -c "from slavic_calendar import slavic_now, today_krat; print(slavic_now(), today_krat())"
python3 make_preview.py && python3 poster.py --dry-run
```

**Последний успешный HEAD:** `834409e` (TZ + state-key + Мирослав).
**Покрыто фиксами:** `make_preview.py`, `poster.py`, `content/holidays/den-miroslava-tariyskogo.json`.

---

## 2026-11-04 — Фикс: Edit-кнопка в превью (filename вместо slug)

### ✅ Исправлено (`d3719b1`): Edit-URL строится из имени файла, не из `slug`

**Симптом:** праздник, созданный через PagesCMS (`den-gorislava-muchenika.json`),
в превью имел Edit-кнопку ✏️, ведущую на `content/holidays/Den' Gorislava Muchenika.json`
→ PagesCMS отвечал: `The file "…" does not exist yet`.

**Причина:** `make_preview.py` строил Edit-URL как `content/holidays/<slug-из-JSON>.json`.
PagesCMS генерирует `slug` транслитом title (для «День Горислава Мученика» →
`Den' Gorislava Muchenika`), а имя файла — по своей slug-конвенции
(`den-gorislava-muchenika`). У 53 из 54 старых файлов `slug` случайно совпадал с
именем файла → баг не проявлялся. Каждый новый CMS-файл ломался.

**Фикс (`make_preview.py`, 3 правки, commit `d3719b1`):**
1. `load_holidays()` инжектит `_d['_filename'] = f.stem` при чтении каждого файла
2. `rows.append(...)` несёт `'filename': h.get('_filename', '')`
3. `card_edit_url(r.get('filename', ''))` — URL из **фактического имени файла**

**Правило на будущее:** для файловых операций (edit URL, `open()`, лог имён)
использовать **`f.stem`**, никогда не `slug` из JSON. `slug` — только для UI
(`data-slug`, copy-фича), не для FS-путей.

### ✅ Уточнение к разделу выше: `image` в `images/` работает

**Исправление ошибочного опасения (проверено в `poster.py`):** изначально
здесь утверждалось, что `poster.py` не найдёт картинку в подпапке `images/`.
**Это было неверно.** Резолв идёт через `_resolve_image`:
`BASE = Path(__file__).resolve().parent`. Для `"image": "/images/<name>.jpg"`:
`lstrip("/")` → `"images/<name>.jpg"` → `BASE / "images/<name>.jpg"` → файл
находится. **Работает и для корня (`/xxx.jpg`), и для подпапки (`/images/xxx.jpg`).**

**Подтверждено на практике:**
- Чертог Лебедя: `"image": "/images/Лебедь.jpg"` — ушёл в ВК **с картинкой** ✅
- Светозар Вечный: `"image": "/images/День Светозара Вечного.jpg"` — тот же путь

**Правило на будущее:** PagesCMS пишет `image` как `"/images/<name>.ext"` —
`poster.py` это находит, ручных переносов в корень **не требуется**. Единственное,
что нужно проверять отдельно — что сам `.jpg` **в git** (untracked-файл локально
работает для поста в ВК, но на GitHub Pages превью покажет битую иконку).

### ✅ Прочее за сессию `5f413d1..d3719b1`
- Фантом `2026-11-04|Чертог Лебедя` убран из `state-200796423.json`
- Лебедь корректно уехал в 2027 (следующий цикл)
- Новый праздник «День Горислава Мученика» (CMS, commit `8928df8`) в списке превью
- Проверено: **все 54** edit-кнопки ведут на существующие файлы
