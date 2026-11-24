#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""calendar_engine.py — ЕДИНСТВЕННЫЙ источник дат для vk-poster.

ПРИНЦИП: один якорь в этом файле — всё остальное вычисляется отсюда.
Никаких вписанных дат в JSON-текстах, никаких компенсаций «+1 день».

СОГЛАШЕНИЯ (канон группы):
  • 1 Рамхатъ 7535 начинается в 18:00 (КРАТ) 19.09.2026.
  • Славянский день живёт в гражданском окне [18:00 дня D, 18:00 дня D+1)
    и приписывается гражданской дате D — дню, в который он НАЧИНАЕТСЯ.
  • Канон-проверка: 23.11.2026 → 25-е Айлѣтъ, Понєдѣльнiкъ.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

KRAT = ZoneInfo("Asia/Krasnoyarsk")

try:
    from bukvicy import to_bukvicy          # ҂ȤФЛЄ и т.п.
except Exception:                            # автономный режим (тесты без репо)
    def to_bukvicy(leto: int) -> str:
        return str(leto)

SLAVIC_DAYS = [
    "Понєдѣльнiкъ", "Вторнiкъ", "Тритєїнiкъ", "Чєтвѣрiкъ", "Пꙗтнiца",
    "Шєстица", "Сєдьмiца", "Осьмiца", "Нєдѣлꙗ",
]
SLAVIC_MONTHS = [
    "Рамхатъ", "Айлѣтъ", "Бейлѣтъ", "Гэйлѣтъ", "Дайлѣтъ",
    "Элѣтъ", "Вэйлѣтъ", "Хэйлѣтъ", "Тайлѣтъ",
]
MONTH_DESC = {
    1: "Божественного Начала",
    2: "Новых Даровъ",
    3: "Белаго Сiяния и Покоя Мира",
    4: "Вьюг и Стужи",
    5: "Пробужденiя Природы",
    6: "Посева и Нареченiя",
    7: "Ветровъ",
    8: "Полученiя Даровъ Природы",
    9: "Завершенiя",
}
CIVIL_MONTHS_GEN = ["", "января", "февраля", "марта", "апреля", "мая", "июня",
                    "июля", "августа", "сентября", "октября", "ноября", "декабря"]

MONTH_LENS_SIMPLE = [41, 40, 41, 40, 41, 40, 41, 40, 41]   # Σ = 365
MONTH_LENS_SACRED = [41] * 9                                # Σ = 369 (16-е Лѣто)

DAY_START = time(18, 0)   # 18:00 — начало славянского дня

# ─── ЯКОРЬ (единственная точка правды) ─────────────────────────
ANCHOR_DATE = date(2026, 9, 19)   # 1 Рамхатъ 7535 начинается 18:00 (КРАТ)
ANCHOR_LETO = 7535
ANCHOR_WIDX = 7                   # Осьмица в день якоря → 23.11.2026 = Понєдѣльнiкъ

# ─── Годовые циклы (Круг Жизни / Круголѣт / стихии) ─────────────
SUMMER_BASE = 7521

ELEMENTS = [None] + [
    ("Земля",  "чёрный"),
    ("Звезда", "красный"),
    ("Огонь",  "алый"),
    ("Солнце", "златый"),
    ("Дерево", "зелёный"),
    ("Свага",  "небесный"),
    ("Океан",  "синий"),
    ("Луна",   "фиолѣт"),
    ("Бог",    "белый"),
]

KRUGOLETY = [None,
    "Путь (странник)", "Жрец", "Жрица", "Мiр (Явь)",
    "Свиток", "Феникс", "Лис (Навь)", "Дракон",
    "Змей", "Орёл", "Дельфин", "Конь",
    "Пёс", "Тур (бык)", "Хоромы (дом)", "Капище (храм)",
]

# Наследованные границы Чертогов (день в лѣте, 1 = 1 Рамхатъ). Σ = 365.
# NB: сверить с chertogs.json после внедрения движка.
CHERTOG_STARTS = [1, 23, 45, 66, 88, 110, 134, 159, 184,
                  207, 229, 252, 274, 297, 319, 343]


def is_sacred(leto: int) -> bool:
    """16-е лѣто в 16-летнем круге — святое (369 дней)."""
    return leto % 16 == 0


def month_lens(leto: int) -> list[int]:
    return MONTH_LENS_SACRED if is_sacred(leto) else MONTH_LENS_SIMPLE


def _shift(leto, mi, d, wi, days):
    step = 1 if days >= 0 else -1
    for _ in range(abs(days)):
        wi = (wi + step) % 9
        d += step
        if d < 1:
            mi -= 1
            if mi < 0:
                mi = 8
                leto -= 1
            d = month_lens(leto)[mi]
        elif d > month_lens(leto)[mi]:
            d = 1
            mi += 1
            if mi > 8:
                mi = 0
                leto += 1
    return leto, mi, d, wi


def krugолет(dt: date):
    """Славянский день, НАЧИНАЮЩИЙСЯ в 18:00 гражданского дня dt.
    → (лѣто, индекс месяца, число, индекс дня недели)."""
    return _shift(ANCHOR_LETO, 0, 1, ANCHOR_WIDX, (dt - ANCHOR_DATE).days)


def today_krat() -> date:
    return datetime.now(KRAT).date()


def slavic_now(dt=None):
    if dt is None:
        return datetime.now(KRAT).date()
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        dt = dt.astimezone(KRAT)
    return dt.date() if hasattr(dt, "date") else dt


def current_civil(dt) -> date:
    """Гражданская дата D славянского дня, активного в момент dt.

    Славянский день начинается в 18:00: до 18:00 активен ещё вчерашний
    славянский день. Пост в 04:30 24-го ноября объявляет славянский день,
    начавшийся 18:00 23-го ноября (25 Айлѣтъ) — окно «с 18.00, 23-го».
    """
    if dt is None:
        dt = datetime.now(KRAT)
    if isinstance(dt, datetime):
        if dt.tzinfo is not None:
            dt = dt.astimezone(KRAT)
        d = dt.date()
        return d if dt.time() >= DAY_START else d - timedelta(days=1)
    return dt  # передана готовая гражданская дата (слот 18:00+)


# ─── Гражданские окна ──────────────────────────────────────────
def _fmt(d: date) -> str:
    return f"{d.day}-го {CIVIL_MONTHS_GEN[d.month]}, {d.year} г."


def civil_window(d: date) -> str:
    """Окно славянского дня, начинающегося 18:00 дня d."""
    return f"(с 18.00, {_fmt(d)}, до 18.00, {_fmt(d + timedelta(days=1))} местн.вр.)"


def civil_window_span(start: date, end: date) -> str:
    """Окно диапазона: от 18:00 дня start до 18:00 дня end+1 (конец последнего дня)."""
    return f"(с 18.00, {_fmt(start)}, до 18.00, {_fmt(end + timedelta(days=1))} местн.вр.)"


# ─── Строки шапки ──────────────────────────────────────────────
def slavic_day_line(d: date) -> str:
    _, mi, day, wi = krugолет(d)
    return (f"{day}-го {SLAVIC_MONTHS[mi]} - Сороковнiка (Мѣсꙗцъ) "
            f"{MONTH_DESC[mi + 1]}, {SLAVIC_DAYS[wi]},")


def slavic_range_lines(start: date, end: date) -> tuple[str, str]:
    _, mi1, d1, wi1 = krugолет(start)
    _, mi2, d2, _ = krugолет(end)
    l1 = (f"с {d1}-го {SLAVIC_MONTHS[mi1]} - Сороковнiка (Мѣсꙗцъ) "
          f"{MONTH_DESC[mi1 + 1]}, {SLAVIC_DAYS[wi1]},")
    l2 = (f"по {d2}-е {SLAVIC_MONTHS[mi2]} - Сороковнiка (Мѣсꙗцъ) "
          f"{MONTH_DESC[mi2 + 1]},")
    return l1, l2


def patron_title(pol: str, patron: str) -> str:
    if "," in patron:
        return "Боги-Покровители"
    return "Богъ-Покровитель" if pol == "м" else "Богиня-Покровительница"


def header_full(dt=None, add_smzh: bool = True, range_to=None,
                chertog_block: dict | None = None) -> str:
    """Полная шапка поста.

    dt          — момент публикации (или гражданская дата слота 18:00+).
                  Славянский день определяется по моменту: до 18:00 —
                  ещё вчерашний славянский день.
    range_to    — гражданская дата ПОСЛЕДНЕГО славянского дня диапазона
                  (Чертоги). None — одиночный день.
    chertog_block — {'patron','pol','tree','totem'}.
    """
    if dt is None:
        dt = datetime.now(KRAT)
    D = current_civil(dt)
    leto, mi, day, wi = krugолет(D)
    tail = "  ѿ  С.М.З.Х." if add_smzh else ""
    lines = [f"Сєго днꙗ: въ Лѣтъ {to_bukvicy(leto)} ({leto}){tail},"]
    if range_to is None:
        lines.append(slavic_day_line(D))
        lines.append(civil_window(D))
    else:
        l1, l2 = slavic_range_lines(D, range_to)
        lines.append(l1)
        lines.append(l2)
        lines.append(civil_window_span(D, range_to))
    if chertog_block:
        patron = str(chertog_block.get("patron", "?"))
        pol = chertog_block.get("pol", "ж")
        lines.append(f"👤 {patron_title(pol, patron)}: {patron}")
        lines.append(f"🌳 Священное Древо: {chertog_block.get('tree', '?')}")
        lines.append(f"🐾 Тотемъ: {chertog_block.get('totem', '?')}")
    return "\n".join(lines)


# ─── Обратный поиск: слав. дата → гражданская ──────────────────
def to_gregorian(month_name: str, day: int, start: date | None = None):
    """Первая гражданская дата D, где славянский день = (day, month_name),
    начиная со start (по умолчанию — 1 января текущего года)."""
    if start is None:
        start = date(date.today().year, 1, 1)
    cur, end = start, start + timedelta(days=400)
    while cur <= end:
        leto, mi, d, _wi = krugолет(cur)
        if d == day and SLAVIC_MONTHS[mi] == month_name:
            return cur
        cur += timedelta(days=1)
    return None


# ─── info-блок (наследие slavic_auto) ──────────────────────────
def _load_chertogs() -> dict:
    import json
    from pathlib import Path
    p = Path(__file__).parent / "chertogs.json"
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {str(i + 1): c for i, c in enumerate(data) if isinstance(c, dict)}
    if not isinstance(data, dict):
        return {}
    for key in ("chertogs", "items", "data"):
        inner = data.get(key)
        if isinstance(inner, dict) and inner:
            return {k: v for k, v in inner.items() if isinstance(v, dict)}
        if isinstance(inner, list) and inner:
            return {str(i + 1): c for i, c in enumerate(inner) if isinstance(c, dict)}
    return {k: v for k, v in data.items() if isinstance(v, dict)}


def summer_start(d: date) -> date:
    y = d.year - 1 if (d.month, d.day) < (9, 19) else d.year
    return date(y, 9, 19)


def summer_smzh(d: date) -> int:
    return summer_start(d).year + 5509


def skz(d: date) -> int:
    return ((summer_smzh(d) - SUMMER_BASE) % 144) + 1


def skl(d: date) -> int:
    return ((skz(d) - 1) % 16) + 1


def day_in_summer(d: date) -> int:
    return (d - summer_start(d)).days + 1


def element_number(d: date) -> int:
    return ((skz(d) - 1) // 2) % 9 + 1


def chertog_number(d: date) -> int:
    day = day_in_summer(d)
    n = 16
    for i, s in enumerate(CHERTOG_STARTS):
        if day >= s:
            n = i + 1
        else:
            break
    return n


def info_lines(d: date, chertog: bool = False) -> list[str]:
    s, sl_ = skz(d), skl(d)
    k_name = KRUGOLETY[skl(d)]
    e_name, e_color = ELEMENTS[element_number(d)]
    chn = chertog_number(d)
    ch = _load_chertogs().get(str(chn), {})
    ch_patron = ch.get("patron", "?")
    pol = ch.get("pol", "ж")
    out = []
    if not chertog:
        title = ("Боги-Покровители" if "," in ch_patron else
                 "Богъ-Покровитель" if pol == "м" else "Богиня-Покровительница")
        out.append(f"⚡ Чертог {ch.get('name_gen', ch.get('name', '?'))} – {title} {ch_patron} ⚡")
        out.append(f"🌳 Священное Древо: {ch.get('tree', '?')}.")
    out += [
        f"● {sl_}-є Лѣтъ (из 16-ти) в Крɣгє лѣтъ;",
        f"● {s}-є Лѣтъ (из 144-х) в Крɣгє Жизни;",
        f"● Круголѣт: {k_name};",
        f"● Стихия: {e_name};",
        f"● Цвет: {e_color}.",
    ]
    return out


def daily_weekday(d: date) -> int:
    """Индекс дня 9-дневки для ежедневных постов (без компенсаций)."""
    return krugолет(d)[3]

# Буквицы дней 9-дневки: 1-й день → Азъ … 9-й → Фита.
# Написания сверены с content/holidays/den-dnya-*.json.
WEEKDAY_BUKVICY = [
    "Азъ", "Вѣди", "Глаголи", "Добро", "Есть",
    "Зело", "Земля", "Иже", "Фита",
]


def weekday_and_bukvica(d: date):
    """(имя дня 9-дневки, буквица) — единый источник для шапки и заголовков."""
    i = daily_weekday(d)
    return SLAVIC_DAYS[i], WEEKDAY_BUKVICY[i]


if __name__ == "__main__":
    ok = True

    def check(name, got, want):
        global ok
        good = got == want
        ok = ok and good
        print(("  ✓ " if good else "  ✗ ") + f"{name}: {got}" + ("" if good else f"  (ожидалось {want})"))

    check("якорь 19.09 = 1 Рамхатъ", krugолет(date(2026, 9, 19)), (7535, 0, 1, 7))
    check("23.11.2026 = 25 Айлѣтъ, Понєдѣльнiкъ", krugолет(date(2026, 11, 23)), (7535, 1, 25, 0))
    check("обратный поиск: 25 Айлѣтъ", to_gregorian("Айлѣтъ", 25), date(2026, 11, 23))
    check("обратный поиск: 6 Бейлѣтъ", to_gregorian("Бейлѣтъ", 6), date(2026, 12, 14))
    # ── Якоря канонической таблицы Айлѣтъ 7535 (2026) ──
    # таблица указывает день, когда окно ЗАКАНЧИВАЕТСЯ (18:00);
    # krugолет(D) = день, который НАЧИНАЕТСЯ 18:00 D, т.е. столбец таблицы = D+1
    check("шов: 41-й Рамхатъ 29.10 (Рамхатъ = 41 день в 7535)", krugолет(date(2026, 10, 29)), (7535, 0, 41, 2))
    check("шов: 1-е Айлѣтъ — окно с 18.00 30.10, Чєтвѣрiкъ", krugолет(date(2026, 10, 30)), (7535, 1, 1, 3))
    check("шов: 2-е Айлѣтъ — окно 31.10→01.11", krugолет(date(2026, 10, 31)), (7535, 1, 2, 4))
    check("табл. 29 Айлѣтъ Пꙗтнiца — Ярослав (окно 27→28.11)", krugолет(date(2026, 11, 27)), (7535, 1, 29, 4))
    check("табл. 30 Айлѣтъ Шєстица (окно 28→29.11)", krugолет(date(2026, 11, 28)), (7535, 1, 30, 5))
    check("табл. 36 Айлѣтъ Тритєїнiкъ — Олег Пращедный (окно 04→05.12)", krugолет(date(2026, 12, 4)), (7535, 1, 36, 2))
    check("табл. 40 Айлѣтъ — конец месяца (окно 08→09.12)", krugолет(date(2026, 12, 8)), (7535, 1, 40, 6))
    check("табл. to_gregorian(Айлѣтъ, 29) = 27.11 — начало окна Ярослава", to_gregorian("Айлѣтъ", 29), date(2026, 11, 27))
    check("табл. to_gregorian(Айлѣтъ, 40) = 08.12 — конец Айлѣтъ", to_gregorian("Айлѣтъ", 40), date(2026, 12, 8))
    print()
    print("── Одиночный день (пост 23.11 18:00) ──")
    print(header_full(date(2026, 11, 23)))
    print()
    print("── Чертог Змея (пост 24.11 04:30!) ──")
    print(header_full(datetime(2026, 11, 24, 4, 30, tzinfo=KRAT),
                      range_to=to_gregorian("Бейлѣтъ", 6),
                      chertog_block={"patron": "Семаргл", "pol": "м",
                                     "tree": "Липа", "totem": "Змей"}))
    print()
    print("── info-блок для 23.11 ──")
    for ln in info_lines(date(2026, 11, 23), chertog=True):
        print("   " + ln)
    print()
    print("── Неделя вперёд ──")
    for k in range(10):
        D = date(2026, 11, 23) + timedelta(days=k)
        leto, mi, d, wi = krugолет(D)
        print(f"   {D:%d.%m} → {d} {SLAVIC_MONTHS[mi]} ({SLAVIC_DAYS[wi]}), Лѣто {leto}")
    print()
    print("ИТОГ:", "ВСЁ СХОДИТСЯ" if ok else "ЕСТЬ РАСХОЖДЕНИЯ")
    raise SystemExit(0 if ok else 1)


def post_slavic_date(civil: date, post_time: str) -> date:
    """Славянский день поста — от момента публикации (граница суток 18:00).

    Пост в 19:00 кануна: праздник уже начался в 18:00 -> следующий civil день.
    Ночной пост (04:30): сутки ещё те же -> тот же civil день.
    """
    try:
        hh, mm = (int(x) for x in post_time.strip().replace("-", ":").split(":", 1))
    except Exception:
        hh, mm = 19, 0
    return civil + timedelta(days=1) if (hh, mm) >= (18, 0) else civil
