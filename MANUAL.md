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

## Проверить ДО публикации
cd ~/vk-poster && python3 poster.py config.main.json --dry-run

## Ручной запуск
cd ~/vk-poster && python3 poster.py config.main.json; echo "exit=$?"

## Если пост не вышел
tail -5 ~/vk-poster/log-runs.txt
#  main=0 = ок/дубль,  main=1 = не вышел,  sync≠0 = git pull упал

tail -20 ~/vk-poster/log-main.txt
#  getWallUploadServer 27 → токен просрочен
#  Файл не найден → фото нет в репо

## Токен сломается (раз в 1-2 года)
vkhost.github.io/vk.html → "VK Admin" → права на группу → токен после #access_token= → заменить в config.main.json

## Cron
crontab -e
# 0 18 * * * /home/pokep/vk-poster/run_poster.sh

## Файлы
holidays.json      — праздники (PagesCMS)
config.main.json   — токены (не в git)
state-200796423.json — что уже постил
log-runs.txt       — итоги запусков
MANUAL.md          — эта шпаргалка

Если что-то сломается — три команды
tail -5 ~/vk-poster/log-runs.txt        # какой запуск упал
tail -20 ~/vk-poster/log-main.txt       # почему
grep FAIL ~/vk-poster/log-main.txt      # только причины

для ии

Прочитай ~/vk-poster/HANDOFF.md и ~/vk-poster/MANUAL.md — это контекст по автопостеру.
Продолжаем оттуда. Проблема: <одна строка что случилось>.

🎯 Единственное правило на будущее
Каждый месяц — 1 минута, профилактика:

cd ~/vk-poster && tail -30 log-runs.txt | grep -c "main=1"
0 → спи дальше
>0 → grep "main=1" -B2 -A2 log-runs.txt → если повторится — в чат
