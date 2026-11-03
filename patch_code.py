#!/usr/bin/env python3
"""Патчит make_preview.py + poster.py: читать content/holidays/*.json"""
import re
from pathlib import Path

BASE = Path(__file__).parent

# ═══════════ make_preview.py ═══════════
mp = BASE / 'make_preview.py'
src = mp.read_text(encoding='utf-8')

if 'content/holidays' in src:
    print('⚠️  make_preview.py уже пропатчен')
else:
    m = re.search(r'^HOLIDAYS\s*=\s*HERE\s*/\s*[\'"]holidays\.json[\'"]\s*$', src, re.M)
    if not m:
        print('❌ make_preview.py: HOLIDAYS = ... не найден'); raise SystemExit(1)

    func = '''

HOLIDAYS_DIR = HERE / 'content' / 'holidays'

def load_holidays():
    """Праздники из content/holidays/*.json (fallback: holidays.json)."""
    if HOLIDAYS_DIR.is_dir():
        items = []
        for f in HOLIDAYS_DIR.glob('*.json'):
            try:
                items.append(json.loads(f.read_text(encoding='utf-8')))
            except Exception as e:
                print(f'warn: {f.name}: {e}')
        if items:
            items.sort(key=lambda x: (x.get('date', 'ZZ'), x.get('text', '')))
            return items
    if HOLIDAYS.exists():
        return json.loads(HOLIDAYS.read_text(encoding='utf-8'))['holidays']
    return []
'''
    src = src[:m.end()] + func + src[m.end():]
    src = re.sub(
        r"data\s*=\s*json\.loads\(HOLIDAYS\.read_text\(encoding=[\"']utf-8[\"']\)\)",
        "data = {'holidays': load_holidays()}",
        src
    )
    src = src.replace(
        'app.pagescms.org/bukvica49/vk-poster/main/file/holidays',
        'app.pagescms.org/bukvica49/vk-poster/main/collection/holidays'
    )
    mp.write_text(src, encoding='utf-8')
    print('✅ make_preview.py: пропатчен')

# ═══════════ poster.py ═══════════
pp = BASE / 'poster.py'
src = pp.read_text(encoding='utf-8')

if 'content/holidays' in src:
    print('⚠️  poster.py уже пропатчен')
else:
    pat = re.compile(
        r'def _load_holidays_dicts\(\):\n'
        r'\s+"""[\s\S]*?"""\n'
        r'\s+data\s*=\s*json\.loads\(HOLIDAYS\.read_text\(encoding="utf-8"\)\)\n'
        r'\s+return data\["holidays"\]'
    )
    new = '''def _load_holidays_dicts():
    """Сырые dict'ы из content/holidays/*.json (fallback: holidays.json)."""
    hd = BASE / "content" / "holidays"
    if hd.is_dir():
        items = []
        for f in sorted(hd.glob("*.json")):
            try:
                items.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        if items:
            return items
    data = json.loads(HOLIDAYS.read_text(encoding="utf-8"))
    return data["holidays"]'''
    if not pat.search(src):
        print('❌ poster.py: паттерн _load_holidays_dicts не найден'); raise SystemExit(1)
    src = pat.sub(new, src, count=1)
    pp.write_text(src, encoding='utf-8')
    print('✅ poster.py: пропатчен')
