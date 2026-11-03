#!/usr/bin/env python3
"""A: ➕ Новый праздник в шапку превью."""
from pathlib import Path

MP = Path(__file__).parent / 'make_preview.py'

def main():
    src = MP.read_text(encoding='utf-8')
    if 'holidays/new' in src:
        print('already patched'); return
    idx = src.find('/file/krugolyety')
    assert idx >= 0, 'krugolyety link not found'
    end_pos = src.find('</a>', idx)
    assert end_pos >= 0, 'krugolyety </a> not found'
    end_pos += len('</a>')
    addition = ('<a href="https://app.pagescms.org/bukvica49/vk-poster/main/'
                'collection/holidays/new" target="_blank" rel="noopener" '
                'title="\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043d\u043e\u0432\u044b\u0439 \u043f\u0440\u0430\u0437\u0434\u043d\u0438\u043a">'
                '\u2795 \u041d\u043e\u0432\u044b\u0439</a>')
    src = src[:end_pos] + addition + src[end_pos:]
    MP.write_text(src, encoding='utf-8')
    print('OK: \u2795 \u041d\u043e\u0432\u044b\u0439 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d \u0432 \u0448\u0430\u043f\u043a\u0443')

if __name__ == '__main__':
    main()
