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
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding='utf-8'))
    if isinstance(data, list):
        return {str(i + 1): c for i, c in enumerate(data) if isinstance(c, dict)}
    if not isinstance(data, dict):
        return {}
    for key in ('chertogs', 'items', 'data'):
        inner = data.get(key)
        if isinstance(inner, dict) and inner:
            return {k: v for k, v in inner.items() if isinstance(v, dict)}
        if isinstance(inner, list) and inner:
            return {str(i + 1): c for i, c in enumerate(inner) if isinstance(c, dict)}
    return {k: v for k, v in data.items() if isinstance(v, dict)}

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
def build_info(d: date, chertog: bool = False) -> list[str]:
    s  = skz(d)
    sl = skl(d)
    k_name = KRUGOLETY[krugolyet_number(d)]
    en = element_number(d)
    e_name, e_color = ELEMENTS[en]

    chn = chertog_number(d)
    ch  = _load_chertogs().get(str(chn), {})
    ch_name   = ch.get('name_gen', ch.get('name', '?'))
    ch_patron = ch.get('patron', '?')
    ch_tree   = ch.get('tree',   '?')
    pol       = ch.get('pol', 'ж')

    if ',' in ch_patron:
        title = 'Боги-Покровители'
    elif pol == 'м':
        title = 'Богъ-Покровитель'
    else:
        title = 'Богиня-Покровительница'

    out = []
    if not chertog:
        out.append(f"⚡ Чертог {ch_name} – {title} {ch_patron} ⚡")
        out.append(f"🌳 Священное Древо: {ch_tree}.")
    out += [
        f"● {sl}-є Лѣтъ (из 16-ти) в Крɣгє лѣтъ;",
        f"● {s}-є Лѣтъ (из 144-х) в Крɣгє Жизни;",
        f"● Круголѣт: {k_name};",
        f"● Стихия: {e_name};",
        f"● Цвет: {e_color}.",
    ]
    return out


def _find_chertog(needle):
    """Ищет чертог по name / name_gen / slug / номеру."""
    d = _load_chertogs()
    if not d or not needle:
        return None
    s = str(needle).strip()
    if s.isdigit():
        return d.get(s) or d.get(str(int(s)))
    if s.startswith('chertog-'):
        for v in d.values():
            if isinstance(v, dict) and v.get('slug') == s:
                return v
    for v in d.values():
        if not isinstance(v, dict):
            continue
        if s == (v.get('name') or '') or s == (v.get('name_gen') or ''):
            return v
    s_low = s.lower()
    for v in d.values():
        if not isinstance(v, dict):
            continue
        if s_low and s_low in (v.get('name') or '').lower():
            return v
    return None


def chertog_block_for(h: dict, fire_date):
    """Если у праздника есть 'chertog' → (chertog_block, range_to).
    range_to — fire-дата окончания Чертога (по полю date_to).
    """
    needle = (h.get('chertog') or '').strip()
    if not needle:
        return None, None
    ch = _find_chertog(needle)
    if not ch:
        return None, None
    block = {
        'title_line': h.get('text', '⚡ Входъ въ Чертогъ ⚡'),
        'patron': ch.get('patron', '?'),
        'pol':    ch.get('pol', 'ж'),
        'tree':   ch.get('tree', '?'),
        'totem':  ch.get('name', '?'),
    }
    dt_str = h.get('date_to')
    range_to = None
    if dt_str:
        mm, dd = map(int, dt_str.split('-'))
        range_to = date(fire_date.year, mm, dd)
        if (mm, dd) < (fire_date.month, fire_date.day):
            range_to = date(fire_date.year + 1, mm, dd)
    return block, range_to
