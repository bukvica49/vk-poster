#!/usr/bin/env python3
"""patch_bukvicy_header.py — MONTH_DESC + header_full() + переключение poster.py.
Идемпотентно: повторный запуск ничего не сломает."""
import re
from pathlib import Path

HERE = Path(__file__).parent
SC = HERE / 'slavic_calendar.py'
PO = HERE / 'poster.py'

# ========== slavic_calendar.py ==========
src = SC.read_text(encoding='utf-8')

# 1. import
if 'from bukvicy import to_bukvicy' not in src:
    anchor = 'from zoneinfo import ZoneInfo'
    assert anchor in src, "zoneinfo import not found"
    src = src.replace(anchor, anchor + '\nfrom bukvicy import to_bukvicy', 1)
    print("  SC: + from bukvicy import to_bukvicy")

# 2. MONTH_DESC (9 описаний — точно твоя орфография)
if 'MONTH_DESC =' not in src:
    anchor = 'MONTH_LENS_SIMPLE'
    idx = src.find(anchor)
    assert idx > 0, "MONTH_LENS_SIMPLE not found"
    block = (
        "MONTH_DESC = {\n"
        "    1: 'Божественного Начала',\n"
        "    2: 'Новых Даровъ',\n"
        "    3: 'Белаго Сiяния и Покоя Мира',\n"
        "    4: 'Вьюг и Стужи',\n"
        "    5: 'Пробужденiя Природы',\n"
        "    6: 'Посева и Нареченiя',\n"
        "    7: 'Ветровъ',\n"
        "    8: 'Полученiя Даровъ Природы',\n"
        "    9: 'Завершенiя',\n"
        "}\n\n"
    )
    src = src[:idx] + block + src[idx:]
    print("  SC: + MONTH_DESC")

# 3. header_full() — рядом с header()
if 'def header_full(' not in src:
    anchor = 'return f"{SLAVIC_DAYS[wi]} · {d} {SLAVIC_MONTHS[mi]} · Лѣто {leto}"'
    assert anchor in src, "header() return not found"
    new_func = (
        anchor + "\n\n\n"
        'def header_full(dt=None, add_smzh: bool = True) -> str:\n'
        '    """Полная шапка поста с буквицами.\n'
        '    СЕДМИЦА · 13 Айлѣтъ Сороковнiкъ (Мѣсꙗцъ) Новых Даровъ · Лѣто ҂ЗФЛЕ(7535) Ѿ С.М.З.Х."""\n'
        '    if dt is None:\n'
        '        dt = datetime.now(KRAT)\n'
        '    sl = slavic_now(dt) if isinstance(dt, datetime) else dt\n'
        '    leto, mi, d, wi = krugолет(sl)\n'
        '    mn = SLAVIC_MONTHS[mi]\n'
        '    desc = MONTH_DESC[mi + 1]\n'
        '    bkv = to_bukvicy(leto)\n'
        '    s = (f"{SLAVIC_DAYS[wi]} · {d} {mn} Сороковнiкъ "\n'
        '         f"(Мѣсꙗцъ) {desc} · Лѣто {bkv}({leto})")\n'
        '    if add_smzh:\n'
        '        s += \' Ѿ С.М.З.Х.\'\n'
        '    return s'
    )
    src = src.replace(anchor, new_func, 1)
    print("  SC: + def header_full()")

SC.write_text(src, encoding='utf-8')

# ========== poster.py ==========
src = PO.read_text(encoding='utf-8')
if 'header_full' not in src:
    pat = re.compile(
        r'(\s+)_hl = slavic_calendar\.header\(today_d\)'
        r'(\n\s+if CONFIG\.get\("add_krug"\):)'
        r'(\n\s+_hl \+= "[^"]+")'
    )
    m = pat.search(src)
    assert m, "poster.py: блок не найден"
    repl = m.group(1) + '_hl = slavic_calendar.header_full(today_d, add_smzh=CONFIG.get("add_krug"))'
    src = src[:m.start()] + repl + src[m.end():]
    PO.write_text(src, encoding='utf-8')
    print("  PO: header() → header_full() (add_krug перенесён в аргумент)")
else:
    print("  PO: уже header_full (skip)")

print("OK.")
