# Автопостер — шпаргалка

## Добавить праздник — через превью
https://bukvica49.github.io/vk-poster/ → `➕ Новый` в шапке → форма PagesCMS.

1. Заполнить поля
2. Save → PagesCMS auto-commit в `content/holidays/{slug}.json`
3. Через 1-2 мин — live (деплой: `.github/workflows/pages.yml`)

## Прямо в PagesCMS
https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays

`content/holidays/*.json` — **1 файл = 1 праздник** (не массив).

Поля:
- `date`    — обязательно, `MM-DD` (не `DD-MM`). **Гражданский день, в 18:00 которого
              выйдет пост.** ⚠️ Это **канун** праздника: слав. сутки с заката.
              Пример: «День Мирослава» 1 ноября → JSON `date: "10-31"` →
              пост 31.10 18:00 KRAT.
              Проверка: python3 -c "import poster; from datetime import date; print([t for t,_,_ in poster.holidays_today(date(2026,10,31))])"
- `text`    — обязательно, заголовок поста
- `slug`    — опционально (= имя файла; PagesCMS ставит автоматически)
- `text_md` — опционально, Markdown-тело поста (если пусто — берётся `text`)
- `post_time` — опционально, время поста `ЧЧ:ММ` (локально по KRAT, пусто = 18:00). Примеры: `09:00`, `21:30`
- `info`    — опционально, массив строк внизу поста
- `info_md` — legacy, в схеме PagesCMS больше не отображается (используй `info[]`)
- `image`   — опционально, имя файла в КОРНЕ репо (Upload через PagesCMS)

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

## Несколько дней подряд / несколько в день
- Многодневный: каждый день — своя запись, свой `image` → каждый день отдельный пост
- Два разных праздника в 1 день: разные `text` → оба поста выйдут

## Автозапуск (GitHub Actions) — ГЛАВНОЕ
Пост идёт САМ каждый день в 18:00 KRAT через GitHub Actions.
Компьютер может быть выключен.

- Воркфлоу: `.github/workflows/post.yml`
- Cron: `0 11 * * *` UTC = 18:00 KRAT
- Ручной запуск: https://github.com/bukvica49/vk-poster/actions/workflows/post.yml → Run workflow
- Секреты (Settings → Secrets → Actions):
  - `VK_CONFIG` — содержимое config.main.json
  - `DEPLOY_KEY` — приватный SSH, fingerprint: wIS9WCBCR9u2IzIPI4aiHTIXcwHLQiJgPUy/k0Kl278

ВНИМАНИЕ: локальный cron НЕ нужен. Если включишь — двойные посты.

## Проверить ДО публикации
cd ~/site/vk-poster-ARCHIVE-20261104 && python3 poster.py --dry-run
# конкретная дата: python3 poster.py --dry-run --date 2026-10-31

## Ручной запуск локально (если ПК включён)
cd ~/site/vk-poster-ARCHIVE-20261104 && python3 poster.py; echo "exit=$?"
# ВНИМАНИЕ: запускает РЕАЛЬНЫЙ пост в VK.

## Если пост не вышел

### Шаг 1 — GitHub Actions (главное)
1. https://github.com/bukvica49/vk-poster/actions/workflows/post.yml
2. Верхний запуск → клик
3. зелёная галочка = успех, красный крестик = упало → клик на шаг `Run poster` → причина

### Шаг 2 — локально
tail -5  ~/site/vk-poster-ARCHIVE-20261104/log-runs.txt
#  main=0 = ок/дубль,  main=1 = не вышел,  sync!=0 = git pull упал

tail -20 ~/site/vk-poster-ARCHIVE-20261104/log-main.txt
#  getWallUploadServer 27 → токен просрочен
#  Файл не найден → фото нет в репо

## Токен сломается (раз в 1-2 года)
vkhost.github.io/vk.html → "VK Admin" → права на группу → токен после #access_token= → заменить в config.main.json И в секрете VK_CONFIG на GitHub.

## Сайт — синхронизация с автопостером
После правки chertogs.json / CHERTOG_STARTS / формата шапки:

    cd ~/site/vk-poster-ARCHIVE-20261104 && python3 tools/build_site_slavic_js.py
    cd ~/site/bukvica49.github.io-main
    git add js/ index.html nav/
    git commit -m "sync: славянская дата из chertogs.json"
    git push

Генератор сам поднимет ?v=N→N+1 в index.html и nav/*.html (cache-bust).
Подробности: ~/site/bukvica49.github.io-main/MANUAL.md
### Часовые пояса — VK и сайт могут расходиться

- **VK-пост** = канонический Slavic день по **Красноярску** (`slavic_calendar.slavic_now()` → `datetime.now(KRAT)`).
- **Сайт** (`js/slavic-date.js`) = Slavic день по **локальному TZ читателя** (рубеж 18:00 — по его часам).
- ⚠️ У **не-красноярцев** VK-пост и сайт **могут показывать разные дни** в один момент — **осознанное решение, не баг**.
- У **красноярцев** — совпадают всегда.

Связано с фиксом `a10512d` (`slavic_calendar.py`: `datetime.now()` → `datetime.now(KRAT)`).


## Поиск и настройки вида

С ноября 2026 в превью появилась панель поиска и настроек. Работает без логина и без сервера.

Поиск (поле сверху) фильтрует карточки по названию, дате, slug и всему тексту. Примеры запросов: щука, нояб, 05.11, 2026, rodomira. Escape в поле — сброс.

Настройки (кнопка рядом с поиском) — ночной режим и фон страницы. Фон берётся из картинок праздников или загружается локально с компьютера. Лимит загружаемого фона — 4 МБ.

Хранение — localStorage браузера под ключом vp-prefs. Только в твоём браузере; другой человек увидит стандартный вид. Очистка кэша браузера сбрасывает настройки.

Код — один файл web/app.js (примерно 200 строк, без зависимостей). Собирается в _site/app.js через make_preview.py и подключается в шаблоне как script src="app.js" defer.

## Поиск по репозиторию — шпаргалка

`./ed.py find` ищет по всем полям (`slug`, `text`, `text_md`, `info`, `image`), без учёта регистра, кириллица/латиница — как есть. Остальное — `grep`/`rg`/`find`.

| Что нужно | Команда |
|---|---|
| Пост по slug | `./ed.py show chertog-devy` |
| Пост по слову (заголовок/тело/инфо) | `./ed.py find щук` |
| Все посты месяца | `./ed.py list \| grep '^01-'` |
| Посты с `date_to` (многодневные) | `grep -l '"date_to"' content/holidays/*.json` |
| Кто ссылается на картинку | `grep -l 'Дева.jpg' content/holidays/*.json` |
| Посты без картинки | `./ed.py validate \| grep '^⚠'` |
| Посты с жёсткой ошибкой | `./ed.py validate \| grep '^✗'` |
| Что менял последним | `./ed.py status`, `git log --oneline -10` |
| Рекурсивно по всем файлам | `rg -n 'паттерн'` (или `grep -rn 'паттерн' . --exclude-dir=.git`) |
| Только `.json`, мимо `.git` | `find . -name '*.json' -not -path './.git/*'` |
| Найти файл по имени (без учёта регистра) | `find . -iname '*дев*' -not -path './.git/*'` |

Три мелочи, которые экономят время:

- `grep '^⚠'` — `^` обязателен. Строка итогов `Итого: 58 ✓, 12 ⚠, 0 ✗` тоже содержит `⚠`, и без `^` в grep-пайп попадёт `58` вместо slug. Проверено на практике — цикл упал на `content/holidays/58.json`.
- `./ed.py list --json` → `python3 -m json.tool` — если хочется отступить JSON для чтения.
- `git grep 'паттерн'` — если `rg` нет, а нужно быстро и с учётом индекса.

## ed.py — редактор постов

Один файл в корне репо, без зависимостей. Запуск `./ed.py` (если `Permission denied` — `chmod +x ed.py`; или `python3 ed.py`).

| Задача | Команда |
|---|---|
| Что сейчас в базе | `./ed.py list` |
| Посмотреть пост | `./ed.py show chertog-devy` |
| Найти по слову | `./ed.py find щук` |
| Поправить руками | `./ed.py edit chertog-devy` |
| Создать новый | `./ed.py new` |
| Прописать картинку | `./ed.py image chertog-devy images/Дева.jpg` |
| Удалить пост | `./ed.py rm chertog-devy` |
| Проверить базу | `./ed.py validate` |
| Собрать превью | `./ed.py preview` |
| Опубликовать | `./ed.py publish` — всё, `./ed.py publish chertog-devy -m "..."` — один пост |

`validate` различает два типа ошибок: `✗` — пост битый (нет `slug`/`date`/`text` или кривая `MM-DD`), exit 1; `⚠` — нет файла картинки, exit 0 (пост опубликуется без картинки). Флаг `--strict` считает `⚠` тоже ошибкой — его вызывает `publish` перед коммитом, чтобы битый пост не ушёл на Pages.

Справка по любой команде: `./ed.py <команда> -h`.

## Графический интерфейс (poster-gui.py)

Настольное окно вместо терминала. `ed.py` под капотом, но всё делается мышкой — формы, кнопки, лог внизу окна. Без браузера.

Запуск:
Один раз проверить, что tkinter на месте: `python3 -c "import tkinter" && echo OK`. Если ModuleNotFoundError — `sudo apt install python3-tk` (Ubuntu/Debian) или `sudo pacman -S tk` (Arch).

Что в окне:

- Слева — список постов (дата, slug, заголовок) и строка поиска.
- Справа — форма выбранного поста: slug, date, date_to, post_time, text, text_md, info, image. Правка → кнопка «Сохранить» = запись в `content/holidays/<slug>.json`.
- Внизу — лог: все запущенные команды (validate, dry-run, publish) печатаются сюда же.

Кнопки и меню:

| Кнопка / пункт | Что делает |
|---|---|
| 💾 Сохранить | Пишет поля в текущий `.json` |
| 🗑 Удалить | Удаляет `.json` (с подтверждением) |
| 📷 Картинку | Открывает файловый диалог, копирует выбранный файл в `images/`, прописывает `/images/<file>` в поле `image` и сохраняет пост |
| 👁 Превью VK | Открывает окно: как пост будет выглядеть в ВК (картинка + заголовок + тело + info). Только просмотр, ничего не постит |
| ✅ Проверить | `./ed.py validate`, вывод в лог |
| 🚀 Опубликовать | `./ed.py publish` — validate --strict + git push (сайт обновится за 1–2 мин). **В ВК НЕ постит.** |
| Файл → Новый пост | Спрашивает slug, создаёт пустой `.json` |
| Файл → Обновить | Перечитывает `content/holidays/*.json` (если правил в другом редакторе) |
| Действия → dry-run | `python3 poster.py --dry-run` — безопасно, VK не трогает |
| Действия → dry-run на дату | То же, но с `--date YYYY-MM-DD` |

Публикация в ВК — **только** через автопостер (GitHub Actions по расписанию в `post_time`). Из GUI пост в ВК не уходит, чтобы случайно не постичь не то и не тогда. Dry-run — можно, он только показывает, что выйдет.

Превью VK (`👁 Превью VK`) показывает пост как есть; если картинка — JPG и Pillow не установлен, вместо картинки будет текстовая пометка. Поставить Pillow (для красивого превью JPG): `pip install Pillow` — необязательно, всё остальное работает без него.

`config.main.json` (токены VK) нужен **только** реальному постингу. Он **не в git** — на GitHub живёт как секрет `VK_CONFIG`, workflow раскладывает его в файл перед запуском.

- `poster.py --dry-run` работает **без** config. В stderr печатается `[dry-run] нет config.main.json — config не нужен для dry-run` — это норма, а не ошибка.
- `poster.py` без `--dry-run` без config печатает инструкцию и `exit=2`, без трейсбека.
- Шаблон структуры: `config.example.json` (без токенов, в git есть). Скопируй в `config.main.json` и подставь свои значения.

### Проверка плейсхолдеров

Если `config.main.json` скопирован из `config.example.json`, но плейсхолдеры (`ВСТАВЬ_СВОЙ_ТОКЕН`, `ОПЦИОНАЛЬНО_...`) не заменены:

- `poster.py` **без** `--dry-run` — останавливается **до** обращения к VK с понятной ошибкой и `exit=2`. Никакого `invalid token` от VK, никакого трейсбека.
- `poster.py --dry-run` — работает; плейсхолдер не мешает предпросмотру.
- `poster.py --date YYYY-MM-DD` — тот же стоп `exit=2`.
- Плейсхолдер в `user_token` (для загрузки картинки) — тот же стоп, с отдельной подсказкой.

Проверено: `cp config.example.json config.main.json && python3 poster.py --date 2026-01-10` → `exit=2`.

## Файлы
content/holidays/*.json       — праздники (PagesCMS collection, 1 файл = 1)
make_preview.py               — генератор _site/ (превью-сайт с кнопками)
config.main.json            — токены (НЕ в git; копия в секрете VK_CONFIG)
state-200796423.json        — что уже постил
log-runs.txt                — итоги локальных запусков
MANUAL.md                   — эта шпаргалка
HANDOFF.md                  — контекст для AI
.github/workflows/post.yml  — автозапуск постинга
.github/workflows/pages.yml — автодеплой превью на push в main

## Формат поста — как выглядит

Структура (сверху вниз):

Сєго днꙗ: въ Лѣтъ ҂ЗФЛЕ (7535)  ѿ  С.М.З.Х.,
7-го Айлѣтъ - Сороковнiка (Мѣсꙗцъ) Новых Даровъ, ПОНЕДѢЛЬНИКЪ,
(с 18.00, 5-го ноября, 2026 г., до 18.00, 6-го ноября, 2026 г. местн.вр.)
⚡ Чертог Лебедя – Богиня-Покровительница Макошь ⚡
🌳 Священное Древо: Сосна.
● 15-є Лѣтъ (из 16-ти) в Крɣгє лѣтъ;
● 15-є Лѣтъ (из 144-х) в Крɣгє Жизни;
● Круголѣт: Хоромы (дом);
● Стихия: Луна;
● Цвет: фиолѣт.

[Тело поста из holidays.json: text_md + info[]]
[Фото из поля image]

Что где:
- Строки 1–3 (шапка, 3 строки с 2026-11-05):
  1) «Сєго днꙗ: въ Лѣтъ … ѿ С.М.З.Х.,»
  2) «N-го <мѣсяцъ> - <Сороковнiкъ> Новых Даровъ, <ДЕНЬ НЕДѢЛИ>,»
  3) «(с 18.00, <канун>, до 18.00, <праздник>, … местн.вр.)»
  Вокруг «ѿ» — по два пробела с каждой стороны (важно для VK).
  ⚠️ Шапка описывает ДЕНЬ ПРАЗДНИКА = krugолет(fire_date + 1), не fire-дату.
  Пост выходит в 18:00 кануна → это начало слав. суток праздника (закат).
- Строка 4: Чертог + пол (Бог-Покровитель / Богиня-Покровительница)
- Строка 5: Священное Древо Чертога
- Строки 6–10: 5 строк Круголета (● …)
- Шапка ВСЕГДА в начале поста
- Формируется `header_full()` в `slavic_calendar.py`; старая `header()` — legacy, для постов НЕ использовать.
- ⚠️ **Тело поста** = `build_info(fire_date + 1)` — синхронно с шапкой.
  Патч 2026-11-05; затронуто 3 праздника (Лебедь 11-03, Купало 06-20, Праотцев-7 01-07).

Настройки:
- add_krug (config.main.json) — вкл/выкл «от С.М.З.Х.»
- chertogs.json / CHERTOG_STARTS — индекс начала массива Чертогов

## Профилактика — раз в месяц
cd ~/site/vk-poster-ARCHIVE-20261104 && tail -30 log-runs.txt | grep -c "main=1"
0 → спи дальше
>0 → grep "main=1" -B2 -A2 log-runs.txt → если повторится — в чат

## Для AI
Прочитай ~/site/vk-poster-ARCHIVE-20261104/HANDOFF.md и ~/site/vk-poster-ARCHIVE-20261104/MANUAL.md — это контекст.
Продолжаем оттуда. Проблема: <одна строка что случилось>.

🚀 Следующая сессия — с чего начинать
Если вернёшься к проекту — одна команда для контекста:

cd ~/site/vk-poster-ARCHIVE-20261104 && cat HANDOFF.md

- **`ed.py`** — 12 команд (`list/show/find/validate/edit/new/image/rm/preview/publish/status/export`). `validate` различает `✗` (жёсткая, exit 1) и `⚠` (нет картинки, exit 0). `--strict` — для хука в `publish`. `Итого:` печатается всегда.
- **Картинки**: `image` копирует файл в `images/` и прописывает `/images/<file>` в JSON. `сhertog-devy` и ещё 11 — без картинок (файлов никогда не было), `image` удалён из JSON. У `chertog-busla`, `chertog-lebedy` и других — есть.
- **Git**: `publish` без slug — `git add -A`, со slug — точечно. Хук вызывает `validate --strict` перед коммитом.
- **Дата**: `MM-DD` = канун праздника (слав. сутки с заката), пост 18:00 KRAT (или `post_time`).
