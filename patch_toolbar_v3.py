#!/usr/bin/env python3
"""v3: ➕ Новый -> class='secondary' (визуально как Чертоги/Круголеты)."""
from pathlib import Path

MP = Path(__file__).parent / 'make_preview.py'

def main():
    src = MP.read_text(encoding='utf-8')
    marker = 'class="secondary" href="https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays/new"'
    if marker in src:
        print('already v3'); return
    old = '<a href="https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays/new"'
    new = ('<a class="secondary" '
           'href="https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays/new"')
    assert old in src, '➕ Новый <a> not found'
    src = src.replace(old, new, 1)
    MP.write_text(src, encoding='utf-8')
    print('OK: ➕ Новый -> class="secondary"')

if __name__ == '__main__':
    main()
