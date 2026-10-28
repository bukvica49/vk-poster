"""Автоматика для постов ВК: славянский календарь."""
import json
from datetime import date
from pathlib import Path

_HERE = Path(__file__).parent
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

def _load_chertogs():
    p = _HERE / 'chertogs.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}

# ─── Дата → базовые номера ─────────────────────────────────
def summer_start(d: date) -> date:
    y = d.year - 1 if (d.month, d.day) < (9, 20) else d.year
    return date(y, 9, 20)

def summer_smzh(d: date) -> int:
    return summer_start(d).year + 5509

def skz(d: date) -> int:
    return ((summer_smzh(d) - SUMMER_BASE) % 144) + 1

def skl(d: date) -> int:
    return ((skz(d) - 1) % 16) + 1

def day_in_summer(d: date) -> int:
    return (d - summer_start(d)).days + 1

# ─── Формулы из таблицы Числобога ──────────────────────────
def element_number(d: date) -> int:
    return ((skz(d) - 1) // 2) % 9 + 1

# Границы Чертогов Сварожьего Круга (1 Рамхатъ = день 1)
# Сумма: 22+22+21+22+22+24+25+25+23+22+23+22+23+22+24+23 = 365
CHERTOG_STARTS = [1, 23, 45, 66, 88, 110, 134, 159, 184,
                  207, 229, 252, 274, 297, 319, 343]

def chertog_number(d: date) -> int:
    """Номер Чертога (1..16) по Сварожьему Кругу (день в лѣте)."""
    day = day_in_summer(d)
    n = 16
    for i, s in enumerate(CHERTOG_STARTS):
        if day >= s:
            n = i + 1
        else:
            break
    return n

def krugolyet_number(d: date) -> int:
    return skl(d)

# ─── Сборка info ───────────────────────────────────────────
def build_info(d: date) -> list[str]:
    s   = skz(d)
    sl  = skl(d)
    dds = day_in_summer(d)
    sd  = summer_start(d)

    en = element_number(d)
    e_name, e_color = ELEMENTS[en]
    k_name = KRUGOLETY[krugolyet_number(d)]

    chn = chertog_number(d)
    ch = _load_chertogs().get(str(chn), {})
    ch_name   = ch.get('name',   '?')
    ch_patron = ch.get('patron', '?')
    ch_tree   = ch.get('tree',   '?')

    return [
        f"Лѣто в Круге Жизни: {s}/144",
        f"Лѣто в круге Лѣт: {sl}/16",
        f"Круголѣт: {k_name}",
        f"Чертог: {ch_name}",
        f"Дата начала лѣта: {sd.strftime('%d.%m.%Y')}",
        f"Номер дня в лѣте: {dds}/365",
        f"Стихия: {e_name}",
        f"Покровитель: {ch_patron}",
        f"Цвет: {e_color}",
        f"Дерево: {ch_tree}",
    ]
