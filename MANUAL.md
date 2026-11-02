# Автопостер — шпаргалка

## Добавить праздник
PagesCMS → holidays.json → блок в массив:

{"text":"Название","date":"11-06","image":"file.jpg","text_md":"**Текст**","info":["Пункт 1","Пункт 2"]}

- `text`+`date` — обязательно (`MM-DD`, не `DD-MM`)
- `image` — имя файла в корне репо
- `text_md` — Markdown
- `info` — массив строк внизу поста

Фото: Upload в корень репо через PagesCMS.

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

## Файлы
holidays.json               — праздники (PagesCMS)
config.main.json            — токены (НЕ в git; копия в секрете VK_CONFIG)
state-200796423.json        — что уже постил
log-runs.txt                — итоги локальных запусков
MANUAL.md                   — эта шпаргалка
HANDOFF.md                  — контекст для AI
.github/workflows/post.yml  — автозапуск через Actions

## Профилактика — раз в месяц
cd ~/vk-poster && tail -30 log-runs.txt | grep -c "main=1"
0 → спи дальше
>0 → grep "main=1" -B2 -A2 log-runs.txt → если повторится — в чат

## Для AI
Прочитай ~/vk-poster/HANDOFF.md и ~/vk-poster/MANUAL.md — это контекст.
Продолжаем оттуда. Проблема: <одна строка что случилось>.
