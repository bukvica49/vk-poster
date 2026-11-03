#!/usr/bin/env python3
"""Fix: убрать margin-left:auto (no-op на inline) + uniform button styles."""
from pathlib import Path

MP = Path(__file__).parent / 'make_preview.py'

def main():
    src = MP.read_text(encoding='utf-8')

    # 1. Убрать style="margin-left:auto" (на inline <a> это no-op и ломает 6px из .secondary)
    old = ('<a class="secondary" style="margin-left:auto" '
           'href="https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays/new"')
    new = ('<a class="secondary" '
           'href="https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays/new"')
    if old in src:
        src = src.replace(old, new, 1)
        print('  ✓ margin-left:auto убран')
    else:
        print('  - margin-left:auto не найден (уже чисто)')

    # 2. uniform button styles: inline-flex + min-height → все кнопки одной высоты
    if '/* toolbar-uniform */' in src:
        print('  - uniform CSS уже стоит')
    else:
        old_css = ('.toolbar a{background:#2563eb;color:#fff;padding:8px 12px;'
                   'border-radius:6px;text-decoration:none;font-size:13px}')
        new_css = ('.toolbar a{background:#2563eb;color:#fff;padding:0 14px;'
                   'border-radius:6px;text-decoration:none;font-size:13px;'
                   'display:inline-flex;align-items:center;justify-content:center;'
                   'min-height:34px;box-sizing:border-box;line-height:1;'
                   'white-space:nowrap}/* toolbar-uniform */')
        if old_css in src:
            src = src.replace(old_css, new_css, 1)
            print('  ✓ uniform CSS применён (inline-flex, min-height:34px)')
        else:
            print('  ! старый .toolbar a не найден — проверь вручную')

    MP.write_text(src, encoding='utf-8')
    print('OK: toolbar-fix применён')

if __name__ == '__main__':
    main()
