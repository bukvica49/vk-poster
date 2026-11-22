from pathlib import Path
import sys, re
p = Path("poster.py")
s = p.read_text(encoding="utf-8")
old = '_resolve_image(img) if img else None'
if old not in s:
    # возможно чуть иная формулировка — найти все вызовы _resolve_image
    for i, line in enumerate(s.splitlines(), 1):
        if "_resolve_image" in line:
            print(f"{i}: {line}")
    sys.exit(1)
s = s.replace(old, '(BASE / img.lstrip("/")) if img else None')
p.write_text(s, encoding="utf-8")
print("poster.py: фикс _resolve_image(img->строка) OK")
