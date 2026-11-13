

---

## 🆕 Изменения 12.11.2026

### 1. Двух-токеновая схема VK (гибрид)

**Проблема 11.11.2026:** устаревший user-токен (Kate Mobile) → VK error 15 (`admin 2fa check fail`), пост не вышел.

**Решение:** в `VK_CONFIG` (секрет GitHub) два токена:
- `token` — **group token** сообщества (права `wall`): постинг `wall.post`. Стабилен, не привязан к аккаунту.
- `user_token` — **user-токен** (Kate Mobile, права `wall, photos, groups, offline`): **только загрузка фото** (`photos.getWallUploadServer` с group token недоступен — VK error 27).

**Признак слёта user-токена:** посты уходят без картинок. Лечится перевыпуском + `gh secret set VK_CONFIG`.

### 2. Ежедневные посты «день недели» (daily)

**9 файлов** `content/holidays/den-dnya-0.json` … `den-dnya-8.json`:
- поля: `slug`, `daily: true`, `weekday: 0..8`, `text`, `text_md`, `post_time: "19:00"`, `info`
- **нет поля `date`** — матч по славянскому дню недели огненного дня.
- Нумерация: 0 Понєдѣльникъ, 1 Въторникъ, 2 Тритейникъ, 3 Четверикъ, 4 Пятьница, 5 Шестица, 6 Сєдьмица, 7 Осьмица, 8 Нєдѣлѧ.
- `text_md` — описание дня (буквица, покровитель), подпись: «🌿 Слава Богам и Предкам наша! 🌿»
- Пост: заголовок → шапка → text_md → чертог-блок (как у праздника).

**Патч poster.py (`09776e6`, `6d4e7b4`):** `_daily_weekday(d)` = день недели огненного дня;
`daily_items(today_d)` — матч по `weekday`; в `main()`: `items = holidays_today() + daily_items()`.

**Расписание:** праздник — 18:00 (или свой `post_time`), daily — **19:00**. Разные слоты.
Святое лѣто 7536 (369 дней) календарь обрабатывает сам.

### 3. Сборка сайта: пропуск daily (`b126190`)

`make_preview.py` падал с `KeyError: 'date'` на daily → Pages краснел. Фикс: daily пропускаются
в `build()` — на витрине их карточек нет (осознанно), постинг в ВК работает.
Если сайт «не обновился»: запуск `.github/workflows/pages.yml` → `failure` → KeyError в логе.

### 4. Шпаргалка dry-run

```bash
# завтрашний пост:
python3 poster.py --dry-run --date $(date -d tomorrow +%F)
# любой день:
python3 poster.py --dry-run --date 2026-11-15
```

### 5. Терминология (для чатов с AI)

| Термин | Что это |
|---|---|
| Праздник | JSON с `date` (MM-DD), 18:00 или свой `post_time` |
| Чертог | Праздник с `chertog`, особый шаблон |
| Daily / пост дня недели | `den-dnya-0…8.json`, без `date`, 19:00, номер = день недели |
