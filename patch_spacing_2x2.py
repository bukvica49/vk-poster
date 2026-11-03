#!/usr/bin/env python3
"""patch_spacing_2x2.py — симметричный зазор вокруг Ѿ: 2×NBSP слева + 2×NBSP справа."""
import re
from pathlib import Path

p = Path('slavic_calendar.py')
s = p.read_text(encoding='utf-8')
NBSP = '\u00A0'

new = "s += '" + NBSP * 2 + "Ѿ" + NBSP * 2 + "С.М.З.Х.'"

if new in s:
    print('УЖЕ применено (skip): 2×NBSP слева + 2×NBSP справа')
    raise SystemExit(0)

# ловим любой вариант: "s += '<что-то> Ѿ<что-то>С.М.З.Х.'"
m = re.search(r"s \+= '[^']*Ѿ[^']*С\.М\.З\.Х\.'", s)
if not m:
    print('❌ НЕ НАЙДЕНО — вручную глянь slavic_calendar.py')
    for i, line in enumerate(s.splitlines(), 1):
        if 'С.М.З.Х.' in line:
            print(f'  строка {i}: {line!r}')
    raise SystemExit(1)

old = m.group(0)
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print(f'✔ было:  {old!r}')
print(f'  стало: {new!r}')
