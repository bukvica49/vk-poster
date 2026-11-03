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
cd ~/vk-poster && python3 poster.py config.main.json --dry-run

## Ручной запуск локально (если ПК включён)
cd ~/vk-poster && python3 poster.py config.main.json; echo "exit=$?"
# ВНИМАНИЕ: запускает РЕАЛЬНЫЙ пост в VK.

## Если пост не вышел

### Шаг 1 — GitHub Actions (главное)
1. https://github.com/bukvica49/vk-poster/actions/workflows/post.yml
2. Верхний запуск → клик
3. зелёная галочка = успех, красный крестик = упало → клик на шаг `Run poster` → причина

### Шаг 2 — локально
tail -5  ~/vk-poster/log-runs.txt
#  main=0 = ок/дубль,  main=1 = не вышел,  sync!=0 = git pull упал

tail -20 ~/vk-poster/log-main.txt
#  getWallUploadServer 27 → токен просрочен
#  Файл не найден → фото нет в репо

## Токен сломается (раз в 1-2 года)
vkhost.github.io/vk.html → "VK Admin" → права на группу → токен после #access_token= → заменить в config.main.json И в секрете VK_CONFIG на GitHub.

## Сайт — синхронизация с автопостером
После правки chertogs.json / CHERTOG_STARTS / формата шапки:

    cd ~/vk-poster && python3 tools/build_site_slavic_js.py
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

СЕДМИЦА · 4 Айлѣтъ · Лѣто 7535 от С.М.З.Х.
⚡ Чертог Щуки – Богиня-Покровительница Рожана ⚡
🌳 Священное Древо: Слива.
● 15-є Лѣтъ (из 16-ти) в Крɣгє лѣтъ;
● 15-є Лѣтъ (из 144-х) в Крɣгє Жизни;
● Круголѣт: Хоромы (дом);
● Стихия: Луна;
● Цвет: фиолѣт.

[Тело поста из holidays.json: text_md + info[]]
[Фото из поля image]

Что где:
- Строка 1: день недели · дата · Лѣто + «от С.М.З.Х.» (если add_krug=true)
- Строка 2: Чертог + пол (Бог-Покровитель / Богиня-Покровительница)
- Строка 3: Священное Древо Чертога
- Далее: 5 строк Круголета
- Шапка ВСЕГДА в начале поста (было в конце до 2026-11-03)

Настройки:
- add_krug (config.main.json) — вкл/выкл «от С.М.З.Х.»
- chertogs.json / CHERTOG_STARTS — индекс начала массива Чертогов

## Профилактика — раз в месяц
cd ~/vk-poster && tail -30 log-runs.txt | grep -c "main=1"
0 → спи дальше
>0 → grep "main=1" -B2 -A2 log-runs.txt → если повторится — в чат

## Для AI
Прочитай ~/vk-poster/HANDOFF.md и ~/vk-poster/MANUAL.md — это контекст.
Продолжаем оттуда. Проблема: <одна строка что случилось>.

🚀 Следующая сессия — с чего начинать
Если вернёшься к проекту — одна команда для контекста:

cd ~/site/vk-poster && cat HANDOFF.md
