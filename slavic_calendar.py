"""Славянский календарь (Круголет Числобога).
Якорь: 28.10.2026 = 1 Рамхатъ 7535, ПОНЕДѢЛЬНИКЪ.
"""
from datetime import date, datetime, timedelta

SLAVIC_DAYS = [
    "ПОНЕДѢЛЬНИКЪ", "ВТОРНИКЪ", "ТРИТЕЙНИКЪ", "ЧЕТВЕРИКЪ", "ПѦТНИЦА",
    "ШЕСТИЦА", "СЕДМИЦА", "ОСЬМИЦА", "НЕДѢЛѦ",
]

SLAVIC_MONTHS = [
    "Рамхатъ", "Айлѣтъ", "Бейлѣтъ", "Гэйлѣтъ", "Дайлѣтъ",
    "Элѣтъ", "Вэйлѣтъ", "Хэйлѣтъ", "Тайлѣтъ",
]
MONTH_LENS = [41, 40, 41, 40, 41, 40, 41, 40, 41]  # Σ = 365

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
            d = MONTH_LENS[mi]
        elif d > MONTH_LENS[mi]:
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

def slavic_now(dt=None):
    """Момент → славянский день с учётом 18:00."""
    if dt is None:
        dt = datetime.now()
    d = dt.date() if hasattr(dt, "date") else dt
    hour = dt.hour if hasattr(dt, "hour") else 12
    if hour >= DAY_START_HOUR:
        d = d + timedelta(days=1)
    return d


def header(dt=None) -> str:
    """Полная славянская дата (учёт 18:00)."""
    if dt is None:
        dt = datetime.now()
    sl = slavic_now(dt) if isinstance(dt, datetime) else dt
    leto, mi, d, wi = krugолет(sl)
    return f"{SLAVIC_DAYS[wi]} · {d} {SLAVIC_MONTHS[mi]} · Лѣто {leto}"
if __name__ == "__main__":
    for iso in ["2026-10-28","2026-10-30","2026-11-01","2026-12-08","2027-01-01"]:
        dt = date.fromisoformat(iso)
        print(f"{iso}  →  {header(dt)}")
