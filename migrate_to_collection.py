#!/usr/bin/env python3
"""Одноразовая миграция holidays.json → content/holidays/*.json"""
import json, re, shutil, sys
from pathlib import Path

BASE = Path(__file__).parent
SRC  = BASE / 'holidays.json'
OUT  = BASE / 'content' / 'holidays'

TRANS = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z',
    'и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r',
    'с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch',
    'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
    'ѣ':'e','Ѣ':'E','і':'i','І':'I','ѳ':'f','Ѳ':'F','ѵ':'i','Ѵ':'I',
}

def slugify(text):
    out = []
    for ch in text.lower():
        if ch in TRANS: out.append(TRANS[ch])
        elif ch.isascii() and ch.isalnum(): out.append(ch)
        elif ch in ' -_,.;:!?—–…«»""''\n\t':  out.append('-')
    slug = re.sub(r'-+', '-', ''.join(out)).strip('-')[:80]
    return slug or 'holiday'

def main():
    force = '--force' in sys.argv
    if not SRC.exists():
        print(f'❌ {SRC} не найден'); sys.exit(1)
    data = json.loads(SRC.read_text(encoding='utf-8'))
    items = data['holidays'] if isinstance(data, dict) and 'holidays' in data else data

    OUT.mkdir(parents=True, exist_ok=True)
    used, w, s = set(), 0, 0
    for i, h in enumerate(items, 1):
        if 'text' not in h:
            print(f'  ⚠️  #{i} без text — пропуск'); continue
        base = slugify(h['text']) or f'holiday-{i:03d}'
        slug, n = base, 2
        while slug in used:
            slug = f'{base}-{n}'; n += 1
        used.add(slug)
        h_out = dict(h); h_out['slug'] = slug
        dst = OUT / f'{slug}.json'
        if dst.exists() and not force:
            print(f'  ⏭  {dst.name}'); s += 1
        else:
            dst.write_text(json.dumps(h_out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(f'  ✅ {slug}.json  ← {h["text"][:55].replace(chr(10), " ")}')
            w += 1

    bak = BASE / 'holidays.json.bak'
    if not bak.exists():
        shutil.copy2(SRC, bak); print(f'\n💾 holidays.json → holidays.json.bak')

    print(f'\n📊 записано: {w}, пропущено: {s}')
    print(f'   в {OUT}: {len(list(OUT.glob("*.json")))} файлов')

if __name__ == '__main__':
    main()
