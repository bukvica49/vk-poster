# -*- coding: utf-8 -*-
"""card_days.py — генератор карточек «Дни недели» (9 дней).

Геометрия по эталону (старая карточка den-dnya-2.png):
  - верхняя плашка:   y 3.9%..47.9%, буквица + подпись «буквица — Имя»
  - зазор ~25 px
  - нижняя плашка:    y 50.3%..96.1% (внизу остаётся полоса чистого фото ~4%)
  - заголовок у верхнего края плашки (центр ~56.7%), ниже — покровитель (опц.)
  - пустое место под текстом — до нижнего края плашки

Запуск:
  python3 card_days.py          # все 9 дней
  python3 card_days.py 2 5      # только дни 2 и 5
  python3 card_days.py --no-pokrovitel   # без строки «Покровитель дня»
"""
import re, sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
BG_DIR = HERE / 'images' / 'den-dnya' / 'фон'
OUT_DIR = HERE / 'images' / 'den-dnya'

SIZE = 1024
PLATE_FILL = (18, 20, 18, 92)        # тёмная полупрозрачная плашка
GOLD = (232, 184, 75)
ORANGE = (232, 150, 60)
WHITE = (245, 245, 240)
RADIUS = 28

ORDINALS = ['первый', 'второй', 'третий', 'четвёртый', 'пятый',
            'шестой', 'седьмой', 'восьмой', 'девятый']

GLYPHS = {'Азъ': 'А', 'Вѣди': 'В', 'Глаголи': 'Г', 'Добро': 'Д',
          'Есть': 'Е', 'Зело': 'Ѕ', 'Земля': 'З', 'Иже': 'И',
          'Ижеи': 'И', 'Како': 'К', 'Люди': 'Л', 'Мыслете': 'М'}

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
    psb, psr = path('PT Sans:bold'), path('PT Serif:bold')
    return dict(title=_font('PTSans-Bold', 52),
                cap=_font('PTSans-Bold', 34),
                glyph=ImageFont.truetype(psr, 280) if psr else _font('DejaVuSerif-Bold', 280))

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
    pokr = m.group(1).strip() if m else ''
    return name, bukv, pokr

def find_bg(bukv, n):
    for stem in (bukv, f'den-dnya-{n}'):
        if not stem: continue
        for ext in ('.jpg', '.jpeg', '.png', '.JPG', '.PNG'):
            p = BG_DIR / (stem + ext)
            if p.is_file(): return p
    files = sorted(BG_DIR.glob('*')) if BG_DIR.is_dir() else []
    return files[0] if files else None

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
    # верхняя плашка
    dr.rounded_rectangle([x0, 40, x1, 490], RADIUS, fill=PLATE_FILL)
    # нижняя плашка: 50.3%..96.1% — как на эталоне, снизу полоса чистого фото
    dr.rounded_rectangle([x0, 515, x1, 984], RADIUS, fill=PLATE_FILL)
    img = Image.alpha_composite(bg.convert('RGBA'), ov)
    dr = ImageDraw.Draw(img)

    # буквица
    glyph = GLYPHS.get(bukv, (bukv or name)[:1])
    bb = dr.textbbox((0, 0), glyph, font=F['glyph'])
    gw, gh = bb[2] - bb[0], bb[3] - bb[1]
    gx, gy = (SIZE - gw)//2 - bb[0], 250 - gh//2 - bb[1]
    dr.text((gx + 4, gy + 5), glyph, font=F['glyph'], fill=(0, 0, 0, 110))
    dr.text((gx, gy), glyph, font=F['glyph'], fill=GOLD + (255,))

    # подпись буквицы
    cap = f'буквица — {bukv}' if bukv else ''
    if cap:
        bb = dr.textbbox((0, 0), cap, font=F['cap'])
        dr.text(((SIZE - bb[2] + bb[0])//2 - bb[0], 448 - (bb[3]-bb[1])//2 - bb[1]),
                cap, font=F['cap'], fill=ORANGE + (255,))

    # заголовок — у верхнего края нижней плашки (центр ~56.7%)
    title = f'{name} — {ordinal} день'
    bb = dr.textbbox((0, 0), title, font=F['title'])
    dr.text(((SIZE - bb[2] + bb[0])//2 - bb[0], 580 - (bb[3]-bb[1])//2 - bb[1]),
            title, font=F['title'], fill=WHITE + (255,))

    # покровитель — опционально
    if with_pokrovitel and pokrovitel:
        bb = dr.textbbox((0, 0), pokrovitel, font=F['cap'])
        dr.text(((SIZE - bb[2] + bb[0])//2 - bb[0], 652 - (bb[3]-bb[1])//2 - bb[1]),
                pokrovitel, font=F['cap'], fill=ORANGE + (255,))

    img.convert('RGB').save(out_path, 'PNG')
    print('✅', out_path)

def main(argv):
    with_pokr = '--no-pokrovitel' not in argv
    nums = [int(a) for a in argv if a.isdigit()] or list(range(9))
    for n in nums:
        name, bukv, pokr = day_data(n)
        bg = find_bg(bukv, n)
        if not bg:
            print(f'⚠ день {n}: нет фона, пропущен'); continue
        render_card(bg, name, ORDINALS[n], bukv, pokr,
                    OUT_DIR / f'den-dnya-{n}.png', with_pokrovitel=with_pokr)

if __name__ == '__main__':
    main(sys.argv[1:])
