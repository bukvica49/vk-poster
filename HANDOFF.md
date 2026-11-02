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

## Что починено
- fa4a1af: постинг без фото -> FAIL main=1 (раньше уходил без фото)
- патч: text_md подбирается по (text, image), не только по text
  проверка: grep -c "hd_img" poster.py  -> должно быть >= 2

## Файлы
- poster.py             — код (main(), holidays_today(), load_state())
- slavic_calendar.py    — календарь, summer_from_smzh(_, (9,20))
- md_to_vk.py           — Markdown -> VK
- holidays.json         — праздники
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

## Правила для AI в новом чате
1. Сначала прочитай HANDOFF.md и MANUAL.md — весь контекст там.
2. По пункту «Ключевые решения» — НЕ переспрашивать, они согласованы.
3. Диагностика = ОДНА команда в чат, не список из пяти.
4. Патч = сначала текст в чате, потом команда. Не вслепую.
5. Не спрашивать «A или B?» без оговорки «по умолчанию делаю X».
6. Не гадать про «шапку с 8-ми пунктами» — это старая непонятая тема,
   если всплывёт, уточнять у владельца конкретно.
