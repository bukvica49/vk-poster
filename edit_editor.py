#!/usr/bin/env python3
"""Правка редактора ВК через терминал.

Примеры:
  python3 edit_editor.py list                     # показать всё
  python3 edit_editor.py emoji-add Обряд 🪬 🔯    # +эмодзи в категорию
  python3 edit_editor.py emoji-remove 🌟          # -эмодзи
  python3 edit_editor.py yat-add ведро вѣдро      # +слово в старослав A
  python3 edit_editor.py slavb-add голубь голѫбь  # +слово в старослав Б
  python3 edit_editor.py build                    # пересобрать _site/ локально
  python3 edit_editor.py push "добавил эмодзи"    # git commit + push
"""
import json, sys, subprocess, argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG  = ROOT / 'config' / 'editor'

def load(name):
    p = CFG / f'{name}.json'
    return json.loads(p.read_text('utf-8')) if p.is_file() else {}

def save(name, data):
    p = CFG / f'{name}.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(f'✅ {p.relative_to(ROOT)}')

# ── emoji / symbols: категории ──
def cat_add(name, category, chars):
    d = load(name)
    d.setdefault(category, [])
    for c in chars:
        if c not in d[category]: d[category].append(c)
    save(name, d)

def cat_remove(name, chars):
    d = load(name); removed = 0
    for cat in d:
        for c in chars:
            if c in d[cat]: d[cat].remove(c); removed += 1
    save(name, d)
    print(f'Удалено вхождений: {removed}')

def cat_list(name):
    d = load(name)
    for cat, chars in d.items():
        print(f'\n[{cat}]  ({len(chars)}):  ' + ' '.join(chars))
    print()

# ── yat / slav_b: словари ──
def dict_add(name, pairs):
    d = load(name); added = 0
    for i in range(0, len(pairs), 2):
        if i + 1 >= len(pairs):
            print(f'⚠ пропущено (без пары): {pairs[i]}'); continue
        k, v = pairs[i], pairs[i+1]
        if d.get(k) == v: print(f'= уже есть: {k}'); continue
        d[k] = v; added += 1; print(f'+ {k} → {v}')
    save(name, d); print(f'Добавлено: {added}')

def dict_remove(name, words):
    d = load(name); removed = 0
    for w in words:
        if w in d: del d[w]; removed += 1; print(f'- {w}')
    save(name, d); print(f'Удалено: {removed}')

def dict_list(name):
    d = load(name)
    print(f'\n[{name}]  ({len(d)} слов)')
    for k, v in sorted(d.items()):
        print(f'  {k} → {v}')
    print()

def dict_search(name, q):
    d = load(name)
    q = q.lower()
    hits = [(k, v) for k, v in d.items() if q in k.lower() or q in v.lower()]
    for k, v in hits: print(f'  {k} → {v}')
    print(f'\nНайдено: {len(hits)}')

# ── общие ──
def full_list(_):
    print('\n══ emoji ══');    cat_list('emoji')
    print('══ symbols ══');  cat_list('symbols')
    print('══ yat (' + str(len(load('yat'))) + ' слов) ══')
    print('══ slav_b (' + str(len(load('slav_b'))) + ' слов) ══')
    print('Для подробностей: python3 edit_editor.py yat-list | slavb-list')

def cmd_build(_):
    subprocess.run([sys.executable, 'make_preview.py'], cwd=ROOT, check=True)

def cmd_open(_):
    subprocess.run(['xdg-open', str(ROOT / '_site' / 'index.html')])

def cmd_push(args):
    msg = args.message or 'config: правка редактора'
    subprocess.run(['git', 'add', '-A'], cwd=ROOT, check=True)
    r = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, text=True)
    if not r.stdout.strip():
        print('ℹ нечего push-ить — все изменения уже в коммите'); return
    subprocess.run(['git', 'commit', '-m', msg], cwd=ROOT, check=True)
    subprocess.run(['git', 'push', 'origin', 'main'], cwd=ROOT, check=True)
    print('🚀 Отправлено')

def main():
    p = argparse.ArgumentParser(description='Правка редактора ВК через терминал')
    sp = p.add_subparsers(dest='cmd', required=True)

    sp.add_parser('list').set_defaults(func=full_list)
    sp.add_parser('build').set_defaults(func=cmd_build)
    sp.add_parser('open').set_defaults(func=cmd_open)

    x = sp.add_parser('emoji-add'); x.add_argument('category'); x.add_argument('chars', nargs='+')
    x.set_defaults(func=lambda a: cat_add('emoji', a.category, a.chars))
    x = sp.add_parser('emoji-remove'); x.add_argument('chars', nargs='+')
    x.set_defaults(func=lambda a: cat_remove('emoji', a.chars))
    sp.add_parser('emoji-list').set_defaults(func=lambda a: cat_list('emoji'))

    x = sp.add_parser('symbols-add'); x.add_argument('category'); x.add_argument('chars', nargs='+')
    x.set_defaults(func=lambda a: cat_add('symbols', a.category, a.chars))
    x = sp.add_parser('symbols-remove'); x.add_argument('chars', nargs='+')
    x.set_defaults(func=lambda a: cat_remove('symbols', a.chars))
    sp.add_parser('symbols-list').set_defaults(func=lambda a: cat_list('symbols'))

    x = sp.add_parser('yat-add'); x.add_argument('pairs', nargs='+', help='слово форма [слово форма ...]')
    x.set_defaults(func=lambda a: dict_add('yat', a.pairs))
    x = sp.add_parser('yat-remove'); x.add_argument('words', nargs='+')
    x.set_defaults(func=lambda a: dict_remove('yat', a.words))
    sp.add_parser('yat-list').set_defaults(func=lambda a: dict_list('yat'))
    x = sp.add_parser('yat-search'); x.add_argument('q')
    x.set_defaults(func=lambda a: dict_search('yat', a.q))

    x = sp.add_parser('slavb-add'); x.add_argument('pairs', nargs='+')
    x.set_defaults(func=lambda a: dict_add('slav_b', a.pairs))
    x = sp.add_parser('slavb-remove'); x.add_argument('words', nargs='+')
    x.set_defaults(func=lambda a: dict_remove('slav_b', a.words))
    sp.add_parser('slavb-list').set_defaults(func=lambda a: dict_list('slav_b'))
    x = sp.add_parser('slavb-search'); x.add_argument('q')
    x.set_defaults(func=lambda a: dict_search('slav_b', a.q))

    x = sp.add_parser('push'); x.add_argument('message', nargs='?', default=None)
    x.set_defaults(func=cmd_push)

    a = p.parse_args()
    a.func(a)

if __name__ == '__main__':
    main()
