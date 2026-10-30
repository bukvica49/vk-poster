"""Генерирует _site/index.html — превью следующих постов."""
import json, os, shutil, subprocess
from datetime import date
from pathlib import Path
from slavic_auto import build_info
import slavic_calendar

HERE = Path(__file__).parent
HOLIDAYS = HERE / 'holidays.json'
IMAGES = HERE / 'images'
OUT = HERE / '_site'

def repo_full_name():
    env = os.environ.get('GITHUB_REPOSITORY')
    if env: return env
    try:
        url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'],
            cwd=str(HERE), stderr=subprocess.DEVNULL).decode().strip()
        url = url.removesuffix('.git').rstrip('/')
        if url.startswith('git@'): return url.split(':', 1)[1]
        return '/'.join(url.split('/')[-2:])
    except Exception:
        return 'CHANGEME/CHANGEME'

def next_occurrence(m, d, today):
    cand = date(today.year, m, d)
    return cand if cand >= today else date(today.year + 1, m, d)

def build():
    OUT.mkdir(exist_ok=True)
    img_out = OUT / 'images'
    if img_out.exists(): shutil.rmtree(img_out)
    img_out.mkdir(parents=True, exist_ok=True)
    # favicon
    fav = HERE / 'favicon.svg'
    if fav.is_file(): shutil.copy2(fav, OUT / 'favicon.svg')
    if IMAGES.exists():
        for p in IMAGES.glob('*'):
            if p.is_file(): shutil.copy2(p, img_out / p.name)

    data = json.loads(HOLIDAYS.read_text(encoding='utf-8'))
    today = date.today()
    repo = repo_full_name()
    edit_url = f'https://github.com/{repo}/edit/main/holidays.json'
    upload_url = f'https://github.com/{repo}/upload/main/images'

    rows = []
    for h in data['holidays']:
        m, dd = map(int, h['date'].split('-'))
        occ = next_occurrence(m, dd, today)
        info = h.get('info') or build_info(occ)
        img_name = None
        if h.get('image'):
            p = HERE / h['image'].lstrip('/')
            if p.is_file(): img_name = p.name
        rows.append({'occ': occ, 'delta': (occ - today).days,
                     'text': h['text'], 'info': info, 'img': img_name,
                     'slavic': slavic_calendar.header(occ)})
    rows.sort(key=lambda r: r['occ'])

    cards = []
    for r in rows:
        when = r['occ'].strftime('%d.%m.%Y')
        delta = ('сегодня' if r['delta'] == 0 else 'завтра' if r['delta'] == 1
                 else f"через {r['delta']} дн.")
        img_html = (f'<img src="images/{r["img"]}" alt="">' if r['img']
                    else '<div class="no-img">нет фото</div>')
        info_html = ''.join(f'<li>{ln}</li>' for ln in r['info'])
        cards.append(f'''
    <div class="card">
      <div class="head"><div><span class="when">{when}</span> <span class="in">{delta}</span></div>
      <a class="edit" href="{edit_url}" target="_blank" rel="noopener">✎ изменить</a></div>
      <div class="body"><div class="img">{img_html}</div>
      <div class="meta"><h2>{r['text']}</h2><div class="slavic">{r['slavic']}</div><ul>{info_html}</ul></div></div>
    </div>''')

    html = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<title>VK Poster — превью</title>
<link rel="icon" type="image/svg+xml" href="favicon.svg"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 body{{font-family:system-ui,sans-serif;max-width:1000px;margin:0 auto;padding:20px;background:#f5f5f7;color:#111}}
 .toolbar{{background:#fff;border-radius:10px;padding:14px 16px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}}
 .toolbar a{{background:#2563eb;color:#fff;padding:8px 12px;border-radius:6px;text-decoration:none;font-size:13px}}
 .toolbar a.secondary{{background:#6b7280;margin-left:6px}}
 .card{{background:#fff;border-radius:10px;padding:16px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,.06)}}
 .head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:8px}}
 .when{{font-weight:600}} .in{{color:#888;font-size:13px;margin-left:6px}}
 .body{{display:grid;grid-template-columns:160px 1fr;gap:16px}}
 .img img{{width:160px;height:160px;object-fit:cover;border-radius:8px}}
 .no-img{{width:160px;height:160px;background:#eee;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#999;font-size:12px}}
 h2{{margin:0 0 8px;font-size:16px}} ul{{margin:0;padding-left:16px;font-size:13px;line-height:1.7}}
 .slavic{{margin:6px 0 10px;font-size:13px;color:#4a5568;font-style:italic;padding:4px 10px;background:#edf2f7;border-radius:4px;display:inline-block}}
 @media(max-width:600px){{.body{{grid-template-columns:1fr}}.img img,.no-img{{width:100%;height:auto;max-height:280px}}}}
</style></head><body><h1>📅 VK Poster</h1>
<div class="toolbar"><span>{len(rows)} праздников · {today.strftime('%d.%m.%Y')}</span>
<div><a href="{edit_url}">+ праздник</a><a class="secondary" href="{upload_url}">+ фото</a></div></div>
{''.join(cards)}</body></html>'''
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    print(f'✅ _site/index.html — {len(rows)} постов')

if __name__ == '__main__':
    build()
