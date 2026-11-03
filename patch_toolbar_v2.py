#!/usr/bin/env python3
"""v2: .card-actions -> правый верхний угол карточки, только иконки."""
import re
from pathlib import Path

BASE = Path(__file__).parent
MP = BASE / 'make_preview.py'

def main():
    src = MP.read_text(encoding='utf-8')

    if 'card-actions-inline' in src:
        print('already v2'); return

    # 1. Удалить старый .card-actions блок (внизу карточки)
    pat = re.compile(r'[ \t]*<div class="card-actions">.*?</div>\n', re.S)
    m = pat.search(src)
    assert m, ".card-actions block not found"
    src = src[:m.start()] + src[m.end():]

    # 2. Вставить новый блок в .head (только иконки)
    old_head = '<div class="head"><div>{badge} <span class="when">{when}</span> <span class="in">{delta}</span></div>'
    assert old_head in src, "head div not found"
    new_head = old_head + '''
        <div class="card-actions card-actions-inline">
          <a class="btn-edit" href="{card_edit_url(r.get('slug', ''))}" target="_blank" rel="noopener" title="\u0420\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c">\u270f\ufe0f</a>
          <button class="btn-copy" data-slug="{_key}" onclick="copyPost(this)" title="\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0442\u0435\u043a\u0441\u0442 \u0434\u043b\u044f VK">\U0001F4CB</button>
        </div>'''
    src = src.replace(old_head, new_head, 1)

    # 3. Заменить CSS: компактные 32x32, top-right, + padding-right у .head
    old_css = ''' .card-actions { display: flex; gap: .5rem; margin-top: .75rem; padding-top: .75rem; border-top: 1px solid #e0d4c0; }
 .card-actions a, .card-actions button { flex: 1; padding: .55rem .75rem; font-size: .85rem; border-radius: 8px; cursor: pointer; text-decoration: none; text-align: center; transition: all .15s; border: none; font-family: inherit; }
 .btn-edit { background: #f2ebe0; color: #4a2a6a; border: 1px solid #d4c4a8; }
 .btn-edit:hover { background: #e8dcc4; }
 .btn-copy { background: #2a3a4a; color: #cde; }
 .btn-copy:hover { background: #3a5a7a; }
 .btn-copy.copied { background: #4a7a4a; color: #fff; }'''

    new_css = ''' .card { position: relative; }
 .head { position: static; padding-right: 84px; }
 .card-actions { position: absolute; top: 8px; right: 8px; display: inline-flex; gap: 6px; z-index: 3; margin: 0; padding: 0; }
 .card-actions a, .card-actions button { width: 32px; height: 32px; padding: 0; font-size: 16px; line-height: 1; border-radius: 7px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: all .15s; border: 1px solid #d4c4a8; background: #f8f2e6; font-family: inherit; text-decoration: none; }
 .card-actions a:hover, .card-actions button:hover { transform: translateY(-1px); box-shadow: 0 2px 6px rgba(0,0,0,.15); }
 .btn-edit { color: #4a2a6a; }
 .btn-edit:hover { background: #e8dcc4; }
 .btn-copy { color: #2a3a4a; }
 .btn-copy:hover { background: #d8e4ee; }
 .btn-copy.copied { background: #4a7a4a; border-color: #4a7a4a; }'''

    assert old_css in src, "old css not found"
    src = src.replace(old_css, new_css, 1)

    # 4. JS: ✅ вместо ✅ Skopirovano (2 варианта — эмодзи и \u-escape)
    candidates = [
        "btn.textContent = '\\u2705 Skopirovano';",     # backslash-escape (v1 так и записал)
        "btn.textContent = '\u2705 Skopirovano';",      # реальный эмодзи
    ]
    replacement = "btn.textContent = '\\u2705';"
    for cand in candidates:
        if cand in src:
            src = src.replace(cand, replacement, 1)
            print(f'   JS match: {cand[:30]!r}...')
            break
    else:
        raise AssertionError("btn.textContent='...Skopirovano' not found in JS")

    MP.write_text(src, encoding='utf-8')
    print('OK: card-actions -> top-right (icons only)')
    print('   + .card { position: relative }')
    print('   + .head { position: static; padding-right: 84px }')
    print('   + .card-actions { absolute top:8 right:8 }')
    print('   + touch-friendly 32x32')
    print('   + ✅ on copy (1.8s)')

if __name__ == '__main__':
    main()
