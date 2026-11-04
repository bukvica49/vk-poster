"""Славянский календарь (Круголет Числобога).
Якорь: 28.10.2026 = 1 Рамхатъ 7535, ПОНЕДѢЛЬНИКЪ.
"""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from bukvicy import to_bukvicy

SLAVIC_DAYS = [
    "ПОНЕДѢЛЬНИКЪ", "ВТОРНИКЪ", "ТРИТЕЙНИКЪ", "ЧЕТВЕРИКЪ", "ПѦТНИЦА",
    "ШЕСТИЦА", "СЕДМИЦА", "ОСЬМИЦА", "НЕДѢЛѦ",
]

SLAVIC_MONTHS = [
    "Рамхатъ", "Айлѣтъ", "Бейлѣтъ", "Гэйлѣтъ", "Дайлѣтъ",
    "Элѣтъ", "Вэйлѣтъ", "Хэйлѣтъ", "Тайлѣтъ",
]
MONTH_DESC = {
    1: 'Божественного Начала',
    2: 'Новых Даровъ',
    3: 'Белаго Сiяния и Покоя Мира',
    4: 'Вьюг и Стужи',
    5: 'Пробужденiя Природы',
    6: 'Посева и Нареченiя',
    7: 'Ветровъ',
    8: 'Полученiя Даровъ Природы',
    9: 'Завершенiя',
}

MONTH_LENS_SIMPLE = [41, 40, 41, 40, 41, 40, 41, 40, 41]  # Σ = 365
MONTH_LENS_SACRED = [41, 41, 41, 41, 41, 41, 41, 41, 41]  # Σ = 369


def is_sacred(leto: int) -> bool:
    """16-е лѣто в 16-летнем круге — святое (369 дней)."""
    return leto % 16 == 0


def month_lens(leto: int):
    """Массив длин 9 месяцев для указанного лѣта."""
    return MONTH_LENS_SACRED if is_sacred(leto) else MONTH_LENS_SIMPLE

# ───── ЯКОРЬ ─────
ANCHOR_DATE  = date(2026, 9, 20)   # 1 Рамхатъ, начало лѣта 7535 (по info)
ANCHOR_LETO  = 7535
ANCHOR_MONTH = 0    # Рамхатъ
ANCHOR_DAY   = 1
ANCHOR_WIDX  = 7    # ОСЬМИЦА (28.10 = +38д = ПОНЕДѢЛЬНИКЪ ✓)

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
    return _shift(ANCHOR_LETO, ANCHOR_MONTH, ANCHOR_DAY, ANCHOR_WIDX,
                  (dt - ANCHOR_DATE).days)

# ─── 18:00 — начало славянского дня ───
DAY_START_HOUR = 18
KRAT = ZoneInfo('Asia/Krasnoyarsk')

def today_krat() -> date:
    """«Сегодня» по Красноярску — единая точка правды для всего проекта."""
    return datetime.now(KRAT).date()


def slavic_now(dt=None):
    """Момент → сегодняшняя дата по Красноярску. Какая дата в KRAT — та и есть."""
    if dt is None:
        return datetime.now(KRAT).date()
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        dt = dt.astimezone(KRAT)
    return dt.date() if hasattr(dt, "date") else dt


def header(dt=None) -> str:
    """Полная славянская дата (учёт 18:00)."""
    if dt is None:
        dt = datetime.now(KRAT)
    sl = slavic_now(dt) if isinstance(dt, datetime) else dt
    leto, mi, d, wi = krugолет(sl)
    return f"{SLAVIC_DAYS[wi]} · {d} {SLAVIC_MONTHS[mi]} · Лѣто {leto}"


def header_full(dt=None, add_smzh: bool = True) -> str:
    """Полная шапка поста — 5 строк (форм. 2026-11-05)."""
    CIVIL_MONTHS_GEN = ["", "января", "февраля", "марта", "апреля", "мая", "июня",
                        "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    if dt is None:
        dt = datetime.now(KRAT)
    dt_date = dt.date() if isinstance(dt, datetime) else dt
    sl = slavic_now(dt) if isinstance(dt, datetime) else dt
    leto, mi, d, wi = krugолет(sl)
    mn = SLAVIC_MONTHS[mi]
    desc = MONTH_DESC[mi + 1]
    bkv = to_bukvicy(leto)
    nd = dt_date + timedelta(days=1)
    tail = "  ѿ  С.М.З.Х." if add_smzh else ""
    line1 = f"Сєго днꙗ: въ Лѣтъ {bkv} ({leto}){tail},"
    line2 = f"{d}-го {mn} - Сороковнiка (Мѣсꙗцъ)"
    line3 = f"{desc}, {SLAVIC_DAYS[wi]},"
    line4 = (f"(с 18.00, {dt_date.day}-го "
             f"{CIVIL_MONTHS_GEN[dt_date.month]}, {dt_date.year} г.,")
    line5 = (f"до 18.00, {nd.day}-го "
             f"{CIVIL_MONTHS_GEN[nd.month]}, {nd.year} г. местн.вр.)")
    return "\n".join([line1, line2, line3, line4, line5])

if __name__ == "__main__":
    for iso in ["2026-10-28","2026-10-30","2026-11-01","2026-12-08","2027-01-01"]:
        dt = date.fromisoformat(iso)
        print(f"{iso}  →  {header(dt)}")
