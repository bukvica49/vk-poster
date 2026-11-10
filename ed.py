#!/usr/bin/env python3
"""ed.py — CLI-редактор постов VK Poster. Только stdlib."""
import argparse, json, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path

HERE         = Path(__file__).resolve().parent
HOLIDAYS_DIR = HERE / 'content' / 'holidays'
IMAGES_DIR   = HERE / 'images'
PREVIEW_DIR  = HERE / '_site'
MAKE_PREVIEW = HERE / 'make_preview.py'
REQUIRED     = ('slug', 'date', 'text')

_TTY = sys.stdout.isatty()
def _c(code, s): return f'\033[{code}m{s}\033[0m' if _TTY else s
def bold(s):   return _c('1', s)
def dim(s):    return _c('2', s)
def red(s):    return _c('31', s)
def green(s):  return _c('32', s)
def yellow(s): return _c('33', s)
def cyan(s):   return _c('36', s)

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n',
                       encoding='utf-8')

def all_items():
    if not HOLIDAYS_DIR.is_dir(): return []
    out = []
    for f in sorted(HOLIDAYS_DIR.glob('*.json')):
        try:
            d = load(f)
            d['_path'] = f
            d['_stem'] = f.stem
            out.append(d)
        except Exception as e:
            print(red(f'!! {f.name}: {e}'))
    return out

def find_item(slug):
    for it in all_items():
        if it.get('slug') == slug or it['_stem'] == slug:
            return it
    return None

def save_item(it, d):
    d.pop('_path', None); d.pop('_stem', None)
    dump(it['_path'], d)

def public(d): return {k: v for k, v in d.items() if not k.startswith('_')}

try:
    from slavic_calendar import SLAVIC_MONTHS as _SLAVIC_MONTHS
except Exception:
    _SLAVIC_MONTHS = ['Рамхатъ', 'Айлѣтъ', 'Бейлѣтъ', 'Гэйлѣтъ', 'Дайлѣтъ',
                      'Элѣтъ', 'Вэйлѣтъ', 'Хэйлѣтъ', 'Тайлѣтъ']

def _fmt_sl(v):
    """{'month': 'Айлѣтъ', 'day': 25} → 'Айлїтъ 25'"""
    if not isinstance(v, dict): return None
    m, d = v.get('month'), v.get('day')
    if not (m and d): return None
    return f"{m} {d}"

def cmd_list(args):
    xs = all_items()
    if args.json:
        print(json.dumps([public(d) for d in xs], ensure_ascii=False, indent=2))
        return 0
    if not xs:
        print(dim('(пусто)')); return 0
    w_slug = max([len(it['_stem']) for it in xs] + [4])
    dates = [str(it.get('date', '')) + (('→' + str(it['date_to'])) if it.get('date_to') else '')
             for it in xs] or ['дата']
    w_date = max([len(x) for x in dates] + [4])
    w_title = min(60, max([len(it.get('text', '')) for it in xs] + [5]))
    print(bold(f'{"slug":<{w_slug}}  {"дата":<{w_date}}  title'))
    print(dim('─' * (w_slug + w_date + w_title + 6)))
    for it in xs:
        d = str(it.get('date', ''))
        if it.get('date_to'): d += '→' + str(it['date_to'])
        t = it.get('text', '')
        if len(t) > w_title: t = t[:w_title - 1] + '…'
        print(f'{it["_stem"]:<{w_slug}}  {d:<{w_date}}  {t}')
    return 0

def cmd_show(args):
    it = find_item(args.slug)
    if not it:
        print(red(f'не найден: {args.slug}')); return 1
    if args.json:
        print(json.dumps(public(it), ensure_ascii=False, indent=2)); return 0
    t = it.get('text', '')
    print(bold(t))
    print(dim('─' * max(20, len(t))))
    d = str(it.get('date', ''))
    if it.get('date_to'): d += ' → ' + str(it['date_to'])
    print(f'{cyan("slug:"):<12} {it["_stem"]}')
    print(f'{cyan("дата:"):<12} {d}')
    _s = _fmt_sl(it.get('slavic'))
    if _s: print(f'{cyan("слав.:"):<12} {_s}')
    _s = _fmt_sl(it.get('slavic_to'))
    if _s: print(f'{cyan("слав. по:"):<12} {_s}')
    if it.get('chertog'):   print(f'{cyan("чертог:"):<12} {it["chertog"]}')
    if it.get('post_time'): print(f'{cyan("время:"):<12} {str(it["post_time"]).replace("-", ":")}')
    if it.get('image'):
        img = HERE / str(it['image']).lstrip('/')
        mark = '✓' if img.exists() else '✗ НЕТ ФАЙЛА'
        print(f'{cyan("картинка:"):<12} {it["image"]}  {mark}')
    for k in sorted(public(it)):
        if k in ('slug', 'date', 'date_to', 'text', 'image', 'chertog', 'post_time',
                 'slavic', 'slavic_to'):
            continue
        print(f'{cyan(k + ":"):<12} {it[k]}')
    return 0

def cmd_find(args):
    q = args.query.lower()
    hits = [it for it in all_items()
            if q in ' '.join(str(v) for v in public(it).values()).lower()]
    if args.json:
        print(json.dumps([public(d) for d in hits], ensure_ascii=False, indent=2)); return 0
    if not hits:
        print(dim('нет совпадений')); return 0
    for it in hits:
        print(f'{green(it["_stem"]):<28} {it.get("date", "")}  {it.get("text", "")}')
    return 0

def cmd_validate(args):
    targets = all_items()
    if args.slug and args.slug != '--all':
        it = find_item(args.slug)
        if not it:
            print(red(f'не найден: {args.slug}')); return 1
        targets = [it]
    mm_dd = r'(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])'
    n_hard = n_soft = 0
    for it in targets:
        hard, soft = [], []
        for k in REQUIRED:
            if not it.get(k): hard.append(f'нет поля {k}')
        d = str(it.get('date', ''))
        if d and not re.fullmatch(mm_dd, d):
            hard.append(f'date не MM-DD: {d!r}')
        dt = it.get('date_to')
        if dt and not re.fullmatch(mm_dd, str(dt)):
            hard.append(f'date_to не MM-DD: {dt!r}')
        for sk in ('slavic', 'slavic_to'):
            sv = it.get(sk)
            if sv is None: continue
            if not isinstance(sv, dict):
                hard.append(f'{sk} не объект: {sv!r}'); continue
            m, dd = sv.get('month'), sv.get('day')
            if not m:
                hard.append(f'{sk}.month пусто')
            elif m not in _SLAVIC_MONTHS:
                hard.append(f'{sk}.month={m!r} неизв. (ожид. из 9 мес.)')
            if not isinstance(dd, int) or not (1 <= dd <= 41):
                hard.append(f'{sk}.day={dd!r} (ожид. 1..41)')
        im = it.get('image')
        if im and not (HERE / str(im).lstrip('/')).exists():
            soft.append(f'нет картинки: {im}')
        if hard:
            n_hard += 1
            print(red(f'✗ {it["_stem"]}'))
            for b in hard: print(f'   - {b}')
        elif soft:
            n_soft += 1
            print(yellow(f'⚠ {it["_stem"]}'))
            for b in soft: print(f'   - {b}')
        else:
            print(green(f'✓ {it["_stem"]}'))
    n_ok = len(targets) - n_hard - n_soft
    print(dim(f'\nИтого: {n_ok} ✓, {n_soft} ⚠, {n_hard} ✗'))
    if getattr(args, 'strict', False):
        return 0 if n_hard == 0 and n_soft == 0 else 1
    return 0 if n_hard == 0 else 1

def cmd_edit(args):
    it = find_item(args.slug)
    if not it:
        print(red(f'не найден: {args.slug}')); return 1
    p = it['_path']
    before = p.read_text(encoding='utf-8')
    editor = os.environ.get('VISUAL') or os.environ.get('EDITOR') or 'nano'
    r = subprocess.run([editor, str(p)])
    if r.returncode != 0:
        print(red(f'{editor} exit {r.returncode}')); return 1
    if p.read_text(encoding='utf-8') == before:
        print(dim('без изменений')); return 0
    try:
        d = load(p)
    except Exception as e:
        print(red(f'!! JSON битый: {e}'))
        p.write_text(before, encoding='utf-8')
        print(yellow('откатил')); return 1
    for k in REQUIRED:
        if not d.get(k):
            print(red(f'!! потеряно {k} — оставляю как было'))
            p.write_text(before, encoding='utf-8'); return 1
    print(green(f'✓ сохранено {it["_stem"]}'))
    return 0

def cmd_new(args):
    HOLIDAYS_DIR.mkdir(parents=True, exist_ok=True)
    print(bold('новый пост (* — обязательно)'))
    def ask(label, required=False):
        while True:
            try:
                v = input(f'{label}{"*" if required else ""}: ').strip()
            except (EOFError, KeyboardInterrupt):
                print(yellow('\nотменено')); raise SystemExit(0)
            if v or not required: return v
            print(red('  обязательно'))
    title = ask('text (заголовок)', required=True)
    date_ = ask('date MM-DD', required=True)
    if not re.fullmatch(r'(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])', date_):
        print(red('date должно быть MM-DD, например 11-05')); return 1
    dt = ask('date_to MM-DD (пусто = нет)')
    ct = ask('chertog (пусто = нет)')
    tm = (ask('post_time [18:00]') or '18:00').replace('-', ':')
    slug = ask('slug (a-z 0-9 дефис)', required=True)
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug):
        print(red('slug: только a-z 0-9 и дефис')); return 1
    p = HOLIDAYS_DIR / f'{slug}.json'
    if p.exists():
        print(red(f'уже есть: {p.name}')); return 1
    d = {'slug': slug, 'date': date_, 'text': title,
         'image': '', 'chertog': ct, 'post_time': tm}
    if dt: d['date_to'] = dt
    if ct:
        print(yellow('\n! chertog без slavic/slavic_to → диапазон по date_to, поплывёт в священное лїто.'))
        print(dim('  После создания — дозаполни через `ed.py edit <slug>`:'))
        print(dim('    "slavic":    {"month": "Айлїтъ",  "day": 25}'))
        print(dim('    "slavic_to": {"month": "Бейлїтъ", "day": 6}'))
    dump(p, d)
    print(green(f'✓ создано {p.relative_to(HERE)}'))
    print(dim(f'  прикрепить картинку: ed.py image {slug} <file.jpg>'))
    return 0

def cmd_image(args):
    it = find_item(args.slug)
    if not it:
        print(red(f'не найден: {args.slug}')); return 1
    src = Path(args.path)
    if not src.exists():
        print(red(f'нет файла: {src}')); return 1
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    dst = IMAGES_DIR / src.name
    if dst.exists(): print(yellow(f'!! {dst.relative_to(HERE)} уже есть — перезапишу'))
    shutil.copy2(src, dst)
    d = public(it); d['image'] = f'/images/{dst.name}'
    save_item(it, d)
    print(green(f'✓ {dst.relative_to(HERE)}  →  {d["image"]}'))
    return 0

def cmd_rm(args):
    it = find_item(args.slug)
    if not it:
        print(red(f'не найден: {args.slug}')); return 1
    p = it['_path']
    p.unlink()
    print(f'удалён {p.relative_to(HERE)}')
    if args.keep_image or not it.get('image'):
        return 0
    img = HERE / str(it['image']).lstrip('/')
    if not img.exists() or img.parent != IMAGES_DIR:
        return 0
    used = [o['_stem'] for o in all_items() if o.get('image') == it.get('image')]
    if used:
        print(yellow(f'  картинку не трогаю — на неё ссылаются: {used}'))
    else:
        img.unlink()
        print(f'  удалена картинка {img.relative_to(HERE)}')
    return 0

def cmd_preview(args):
    if not MAKE_PREVIEW.exists():
        print(red('нет make_preview.py')); return 1
    print(dim('$ python3 make_preview.py'))
    r = subprocess.run([sys.executable, str(MAKE_PREVIEW)], cwd=HERE)
    if r.returncode != 0:
        print(red(f'make_preview exit {r.returncode}')); return 1
    if not PREVIEW_DIR.is_dir():
        print(red('нет _site/')); return 1
    url = f'http://localhost:{args.port}/'
    print(green(f'✓ превью: {url}  (Ctrl+C — стоп)'))
    if not args.no_open:
        import webbrowser; webbrowser.open(url)
    try:
        subprocess.run([sys.executable, '-m', 'http.server',
                        str(args.port), '--directory', str(PREVIEW_DIR)])
    except KeyboardInterrupt:
        print(dim('\nостановлено'))
    return 0

def _git(*cmd, capture=False):
    return subprocess.run(['git', *cmd], cwd=HERE,
                          capture_output=capture, text=capture)

def cmd_publish(args):
    st = _git('status', '--porcelain', capture=True)
    if not st.stdout.strip():
        print(dim('нечего коммитить')); return 0
    if args.slug:
        it = find_item(args.slug)
        if not it:
            print(red(f'не найден: {args.slug}')); return 1
        paths = [str(it['_path'].relative_to(HERE))]
        if it.get('image'):
            img = HERE / str(it['image']).lstrip('/')
            if img.exists(): paths.append(str(img.relative_to(HERE)))
        _git('add', '--', *paths)
    else:
        _git('add', '-A', 'content/', 'images/')
    msg = args.message or (f'post: {args.slug}' if args.slug else 'posts: обновление')
    _git('commit', '-m', msg)
    _git('push', 'origin', 'main')
    return 0

def cmd_status(args):
    r = _git('status', '--short', capture=True)
    print(r.stdout.rstrip() or dim('чисто'))
    r = _git('log', '--oneline', '-5', capture=True)
    print(bold('\nпоследние коммиты:')); print(r.stdout.rstrip())
    return 0

def cmd_export(args):
    out = Path(args.out)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for src in (HOLIDAYS_DIR, IMAGES_DIR):
            if not src.is_dir(): continue
            for f in src.rglob('*'):
                if f.is_file(): z.write(f, f.relative_to(HERE))
    print(green(f'✓ {out}  ({out.stat().st_size // 1024} KB)'))
    return 0

def main(argv=None):
    ap = argparse.ArgumentParser(prog='ed.py', description='CLI-редактор постов VK Poster')
    sp = ap.add_subparsers(dest='cmd')

    p = sp.add_parser('list', help='список постов'); p.add_argument('--json', action='store_true'); p.set_defaults(fn=cmd_list)
    p = sp.add_parser('show', help='показать пост'); p.add_argument('slug'); p.add_argument('--json', action='store_true'); p.set_defaults(fn=cmd_show)
    p = sp.add_parser('find', help='поиск по всем полям'); p.add_argument('query'); p.add_argument('--json', action='store_true'); p.set_defaults(fn=cmd_find)
    p = sp.add_parser('validate', help='проверить посты'); p.add_argument('slug', nargs='?'); p.add_argument('--strict', action='store_true', help='⚠ тоже считать ошибкой'); p.set_defaults(fn=cmd_validate)
    p = sp.add_parser('edit', help='правка JSON в $EDITOR'); p.add_argument('slug'); p.set_defaults(fn=cmd_edit)
    p = sp.add_parser('new', help='новый пост (интерактивно)'); p.set_defaults(fn=cmd_new)
    p = sp.add_parser('image', help='прикрепить картинку'); p.add_argument('slug'); p.add_argument('path'); p.set_defaults(fn=cmd_image)
    p = sp.add_parser('rm', help='удалить пост'); p.add_argument('slug'); p.add_argument('--keep-image', action='store_true'); p.set_defaults(fn=cmd_rm)
    p = sp.add_parser('preview', help='собрать _site и поднять http.server')
    p.add_argument('--port', type=int, default=8765); p.add_argument('--no-open', action='store_true'); p.set_defaults(fn=cmd_preview)
    p = sp.add_parser('publish', help='git add/commit/push')
    p.add_argument('slug', nargs='?'); p.add_argument('-m', '--message'); p.set_defaults(fn=cmd_publish)
    p = sp.add_parser('status', help='git status + log'); p.set_defaults(fn=cmd_status)
    p = sp.add_parser('export', help='zip content/ + images/'); p.add_argument('out', nargs='?', default='vk-poster-backup.zip'); p.set_defaults(fn=cmd_export)

    args = ap.parse_args(argv)
    if not getattr(args, 'fn', None):
        ap.print_help(); return 0
    return args.fn(args)

if __name__ == '__main__':
    sys.exit(main())
