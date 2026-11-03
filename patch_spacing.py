#!/usr/bin/env python3
"""patch_spacing.py — Ѿ подальше от С.М.З.Х. через NBSP (VK-безопасно)."""
import re
from pathlib import Path

p = Path('slavic_calendar.py')
s = p.read_text(encoding='utf-8')

NBSP = '\u00A0'
new = "s += ' Ѿ" + NBSP * 3 + "С.М.З.Х.'"

if new in s:
    print('УЖЕ применено (skip)')
    raise SystemExit(0)

m = re.search(r"s \+= ' Ѿ[^'\"]*С\.М\.З\.Х\.'", s)
if not m:
    print('❌ НЕ НАЙДЕНО — проверь вручную')
    raise SystemExit(1)

old = m.group(0)
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print(f'✔ {old!r}')
print(f'  → {new!r}')
