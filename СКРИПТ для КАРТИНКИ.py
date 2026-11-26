# -*- coding: utf-8 -*-
"""СКРИПТ для КАРТИНКИ — генератор карточек «Дни недели» (9 дней).

Геометрия по эталону (старая карточка den-dnya-2.png):
  - верхняя плашка:   y 3.9%..47.9%, буквица + подпись «буквица — Имя»
  - зазор ~25 px
  - нижняя плашка:    y 50.3%..96.1% (внизу остаётся полоса чистого фото ~4%)
  - заголовок у верхнего края плашки (центр ~56.7%), ниже — покровитель (опц.)

Запуск:
  python3 "СКРИПТ для КАРТИНКИ.py"          # все 9 дней
  python3 "СКРИПТ для КАРТИНКИ.py" 2 5      # только дни 2 и 5
  python3 "СКРИПТ для КАРТИНКИ.py" --no-pokrovitel   # без строки «Покровитель дня»
"""
import re, sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
BG_DIR = HERE / 'images' / 'den-dnya' / 'фон'
OUT_DIR = HERE / 'images' / 'den-dnya'

SIZE = 1024
PLATE_ALPHA = 92   # крути: 75 — светлее, 92 — сейчас, 138 — как эталон ден.2
PLATE_FILL = (20, 20, 20, PLATE_ALPHA)
GOLD = (232, 184, 75)
ORANGE = (232, 150, 60)
WHITE = (245, 245, 240)
RADIUS = 28

ORDINALS = ['первый', 'второй', 'третий', 'четвёртый', 'пятый',
            'шестой', 'седьмой', 'восьмой', 'девятый']

GLYPHS = {'Азъ': 'А', 'Вѣди': 'В', 'Глаголи': 'Г', 'Добро': 'Д',
          'Єсть': 'Є', 'Зело': 'Ѕ', 'Земля': 'Ȥ', 'Ȥемля': 'Ȥ',
          'Иже': 'И', 'Ижеи': 'И', 'Како': 'К', 'Люди': 'Л',
          'Мыслете': 'М', 'Фита': 'Ѳ', 'Ѳита': 'Ѳ'}

# ── шрифты ──────────────────────────────────────────────────────────
def _font(name, size):
    for cand in (f'/usr/share/fonts/truetype/pt/{name}.ttf',
                 f'/usr/share/fonts/truetype/{name}.ttf'):
        p = Path(cand)
        if p.is_file():
            return ImageFont.truetype(str(p), size)
    return ImageFont.truetype('DejaVuSans-Bold.ttf', size)

def fonts():
    import subprocess
    def path(fam):
        out = subprocess.run(['fc-match', '-f', '%{file}', fam],
                             capture_output=True, text=True).stdout.strip()
        return out or None
    dser = path('DejaVu Serif:bold')
    dsb = path('DejaVu Sans:bold')
    return dict(title=_font('PTSans-Bold', 52),                 # заголовок — PT
                cap=ImageFont.truetype(dsb, 34) if dsb else _font('DejaVuSans-Bold', 34),  # подпись буквицы — DejaVu (тут живёт Ȥ)
                pokr=_font('PTSans-Bold', 34),                  # покровитель — PT, как на остальных днях
                glyph=ImageFont.truetype(dser, 280) if dser else _font('DejaVuSerif-Bold', 280))  # буквица — DejaVu Serif (Ȥ/Ѳ)

def _norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip()).casefold()

# ── данные из JSON ──────────────────────────────────────────────────
def day_data(n):
    jf = HERE / 'content' / 'holidays' / f'den-dnya-{n}.json'
    d = json.loads(jf.read_text(encoding='utf-8'))
    md = d.get('text_md', '')
    m = re.search(r'\(([^)]+)\)', md.split('\n', 1)[0])
    name = m.group(1) if m else d.get('text', '')
    m = re.search(r'Буквицы\s*«([^»]+)»', md)
    bukv = m.group(1) if m else ''
    m = re.search(r'Покровитель дня:\s*([^\n]+)', md)
    pokr = m.group(1).strip().strip('*') if m else ''
    return name, bukv, pokr

def find_bg(name, bukv, n):
    """Приоритет: имя дня → буквица → den-dnya-N → первый попавшийся (с предупреждением)."""
    files = {p.stem: p for p in BG_DIR.iterdir() if p.is_file()} if BG_DIR.is_dir() else {}
    norm = {_norm(k): v for k, v in files.items()}
    for stem in (name, bukv, f'den-dnya-{n}'):
        if not stem:
            continue
        if stem in files:
            return files[stem]
        if _norm(stem) in norm:
            return norm[_norm(stem)]
        for ext in ('.jpg', '.jpeg', '.png', '.JPG', '.PNG'):
            p = BG_DIR / (stem + ext)
            if p.is_file():
                return p
    if files:
        first = next(iter(files.values()))
        print(f'⚠ фон для «{name}» не найден, беру первый попавшийся: {first.name}')
        return first
    return None

# ── рендер ──────────────────────────────────────────────────────────
def render_card(bg_path, name, ordinal, bukv, pokrovitel, out_path,
                with_pokrovitel=True):
    F = fonts()
    bg = Image.open(bg_path).convert('RGB')
    w, h = bg.size
    side = min(w, h)
    bg = bg.crop(((w - side)//2, (h - side)//2,
                  (w - side)//2 + side, (h - side)//2 + side)).resize((SIZE, SIZE))

    ov = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    x0, x1 = 40, SIZE - 40
    dr.rounded_rectangle([x0, 40, x1, 490], RADIUS, fill=PLATE_FILL)
    dr.rounded_rectangle([x0, 515, x1, 984], RADIUS, fill=PLATE_FILL)
    img = Image.alpha_composite(bg.convert('RGBA'), ov)
    dr = ImageDraw.Draw(img)

    # буквица — DejaVu Serif Bold (PT не знает Ȥ/Ѳ)
    glyph = GLYPHS.get(bukv, (bukv or name)[:1])
    bb = dr.textbbox((0, 0), glyph, font=F['glyph'])
    gw, gh = bb[2] - bb[0], bb[3] - bb[1]
    gx, gy = (SIZE - gw)//2 - bb[0], 250 - gh//2 - bb[1]
    dr.text((gx + 4, gy + 5), glyph, font=F['glyph'], fill=(0, 0, 0, 110))
    dr.text((gx, gy), glyph, font=F['glyph'], fill=GOLD + (255,))

    # подпись буквицы — DejaVu Sans Bold, мерится и рисуется одним шрифтом
    cap = f'буквица — {glyph}{bukv[1:]}' if bukv else ''
    if cap:
        bb = dr.textbbox((0, 0), cap, font=F['cap'])
        dr.text(((SIZE - bb[2] + bb[0])//2 - bb[0], 448 - (bb[3]-bb[1])//2 - bb[1]),
                cap, font=F['cap'], fill=ORANGE + (255,))

    # заголовок — PT Sans Bold
    title = f'{name} — {ordinal} день'
    bb = dr.textbbox((0, 0), title, font=F['title'])
    dr.text(((SIZE - bb[2] + bb[0])//2 - bb[0], 580 - (bb[3]-bb[1])//2 - bb[1]),
            title, font=F['title'], fill=WHITE + (255,))

    # покровитель — PT Sans Bold, в две строки по « / »
    if with_pokrovitel and pokrovitel:
        parts = [x.strip() for x in pokrovitel.split(' / ')]
        lines = ['Покровитель дня: ' + parts[0]] + parts[1:]
        yy = 640
        for ln in lines:
            bb = dr.textbbox((0, 0), ln, font=F['pokr'])
            dr.text(((SIZE - bb[2] + bb[0])//2 - bb[0], yy - (bb[3]-bb[1])//2 - bb[1]),
                    ln, font=F['pokr'], fill=ORANGE + (255,))
            yy += 48

    img.convert('RGB').save(out_path, 'PNG')
    print('✅', out_path)

def main(argv):
    with_pokr = '--no-pokrovitel' not in argv
    nums = [int(a) for a in argv if a.isdigit()] or list(range(9))
    for n in nums:
        name, bukv, pokr = day_data(n)
        bg = find_bg(name, bukv, n)
        if not bg:
            print(f'⚠ день {n}: нет фона, пропущен'); continue
        render_card(bg, name, ORDINALS[n], bukv, pokr,
                    OUT_DIR / f'den-dnya-{n}.png', with_pokrovitel=with_pokr)

if __name__ == '__main__':
    main(sys.argv[1:])
