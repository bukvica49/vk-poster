"""Генерирует _site/index.html — превью следующих постов."""
import json, os, shutil, subprocess
from datetime import date, timedelta
from pathlib import Path
from slavic_auto import build_info
import slavic_calendar
from md_render import md_to_html

HERE = Path(__file__).parent
HOLIDAYS = HERE / 'holidays.json'

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
    try:
        _cfg = json.loads((HERE / 'config.main.json').read_text(encoding='utf-8'))
    except Exception:
        _cfg = {}
    add_krug = _cfg.get('add_krug', True)
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

    data = {'holidays': load_holidays()}
    today_civil = date.today()
    state_path = HERE / 'state-200796423.json'
    posted = set()
    if state_path.is_file():
        try: posted = set(json.loads(state_path.read_text(encoding='utf-8'))['posted'])
        except Exception: pass
    repo = repo_full_name()
    edit_url = f'https://github.com/{repo}/edit/main/holidays.json'
    upload_url = f'https://github.com/{repo}/upload/main/images'

    rows = []
    for h in data['holidays']:
        m, dd = map(int, h['date'].split('-'))
        occ = next_occurrence(m, dd, today_civil)
        try:
            _auto = build_info(occ)
        except Exception:
            _auto = []
        _manual = h.get('info') or []
        if isinstance(_manual, str):
            _manual = [_manual]
        info = _auto + [s.strip() for s in _manual if s.strip()]
        img_name = None
        if h.get('image'):
            p = HERE / h['image'].lstrip('/')
            if p.is_file(): img_name = p.name
        fire_civil = occ - timedelta(days=1)   # Slavic day starts 18:00 prev civil day
        key = f"{occ.isoformat()}|{h['text']}"
        rows.append({'occ': occ, 'fire_civil': fire_civil,
                     'delta': (fire_civil - today_civil).days,
                     'text': h['text'], 'info': info, 'info_md': h.get('info_md'), 'text_md': h.get('text_md'), 'img': img_name,
                     'slavic': slavic_calendar.header_full(occ, add_smzh=add_krug),
                     'posted': key in posted, 'slug': h.get('slug') or ''})
    rows.sort(key=lambda r: r['occ'])
    def card_edit_url(slug):
        """URL редактирования конкретного праздника в PagesCMS."""
        if not slug:
            return "https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays"
        import urllib.parse as _up
        p = "content/holidays/" + slug + ".json"
        return ("https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays/edit/"
                + _up.quote(p, safe=""))

    def build_post_text(r):
        """Текст, который poster.py отправит в VK (согласовано с main())."""
        head = []
        if r.get("slavic"):
            head.append(r["slavic"])
        if r.get("info"):
            head.append(chr(10).join(r["info"]))
        md = r.get("text_md") or ""
        try:
            from poster import md_to_vk as _md_to_vk
            body = _md_to_vk(md) if md else r["text"]
        except Exception:
            body = md if md else r["text"]
        return (chr(10).join(head) + chr(10) * 2 + body) if head else body

    posts_map = {}
    for _i, _r in enumerate(rows):
        _k = _r.get("slug") or f"_idx{_i}"
        posts_map[_k] = build_post_text(_r)
    posts_json = json.dumps(posts_map, ensure_ascii=False).replace("</", "<\\/")

    _warn = [x for x in rows if x.get("info_md") and not x.get("text_md")]
    if _warn:
        print(f"warn: {len(_warn)} prazdnikov s info_md no bez text_md (preview != poster)")


    cards = []
    for _idx, r in enumerate(rows):
        _key = r.get('slug') or f'_idx{_idx}'
        when = r['fire_civil'].strftime('%d.%m.%Y') + ' 18:00'
        delta = ('сегодня' if r['delta'] == 0 else 'завтра' if r['delta'] == 1
                 else f"через {r['delta']} дн." if r['delta'] > 0 else 'прошло')
        badge = (
          '<span style="background:#16a34a;color:#fff;padding:2px 8px;border-radius:4px;font-size:12px">✅ отправлено</span>'
          if r['posted'] else
          '<span style="background:#e5e7eb;color:#666;padding:2px 8px;border-radius:4px;font-size:12px">⏳ ожидает</span>')
        img_html = (f'<img src="images/{r["img"]}" alt="">' if r['img']
                    else '<div class="no-img">нет фото</div>')
        info_html = '<ul>' + ''.join(f'<li>{ln}</li>' for ln in r['info']) + '</ul>'
        desc_md = r.get('info_md') or r.get('text_md')
        if desc_md:
            info_html += f'<div class="info-md">{md_to_html(desc_md)}</div>'
        cards.append(f'''
    <div class="card">
      <div class="head"><div>{badge} <span class="when">{when}</span> <span class="in">{delta}</span></div>
        <div class="card-actions card-actions-inline">
          <a class="btn-edit" href="{card_edit_url(r.get('slug', ''))}" target="_blank" rel="noopener" title="Редактировать">✏️</a>
          <button class="btn-copy" data-slug="{_key}" onclick="copyPost(this)" title="Скопировать текст для VK">📋</button>
        </div>
      </div>
      <div class="body"><div class="img">{img_html}</div>
      <div class="meta"><h2>{r['text']}</h2><div class="slavic">{r['slavic']}</div>{info_html}</div></div>
    </div>''')


    css_extra = '''
 .card { position: relative; }
 .head { position: static; padding-right: 84px; }
 .card-actions { position: absolute; top: 8px; right: 8px; display: inline-flex; gap: 6px; z-index: 3; margin: 0; padding: 0; }
 .card-actions a, .card-actions button { width: 32px; height: 32px; padding: 0; font-size: 16px; line-height: 1; border-radius: 7px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: all .15s; border: 1px solid #d4c4a8; background: #f8f2e6; font-family: inherit; text-decoration: none; }
 .card-actions a:hover, .card-actions button:hover { transform: translateY(-1px); box-shadow: 0 2px 6px rgba(0,0,0,.15); }
 .btn-edit { color: #4a2a6a; }
 .btn-edit:hover { background: #e8dcc4; }
 .btn-copy { color: #2a3a4a; }
 .btn-copy:hover { background: #d8e4ee; }
 .btn-copy.copied { background: #4a7a4a; border-color: #4a7a4a; }
'''

    js_extra = '''
<script type="application/json" id="posts-data">__POSTS_JSON__</script>
<script>
function copyPost(btn) {
  var slug = btn.getAttribute('data-slug');
  var dataEl = document.getElementById('posts-data');
  if (!dataEl) { alert('Net dannych posta'); return; }
  var data;
  try { data = JSON.parse(dataEl.textContent); }
  catch (e) { alert('Oshibka chteniya: ' + e); return; }
  var txt = data[slug];
  if (!txt) { alert('Tekst dlya slug=' + slug + ' ne nayden'); return; }
  function ok() {
    var orig = btn.textContent;
    btn.textContent = '\u2705';
    btn.classList.add('copied');
    setTimeout(function() { btn.textContent = orig; btn.classList.remove('copied'); }, 1800);
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(txt).then(ok).catch(function(e) { alert('Oshibka: ' + e); });
  } else {
    var ta = document.createElement('textarea');
    ta.value = txt; ta.style.position = 'fixed'; ta.style.left = '-9999px';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); ok(); }
    catch (e) { alert('Kopirovanie ne podderzhivaetsya'); }
    document.body.removeChild(ta);
  }
}
</script>
'''
    js_extra = js_extra.replace('__POSTS_JSON__', posts_json)

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

.info-md {{ font-size: 0.94em; line-height: 1.55; }}
.info-md h1, .info-md h2, .info-md h3 {{ margin: 12px 0 6px; line-height: 1.25; color: #2d1a4d; }}
.info-md h1 {{ font-size: 1.4em; }}
.info-md h2 {{ font-size: 1.25em; }}
.info-md h3 {{ font-size: 1.1em; }}
.info-md p  {{ margin: 8px 0; }}
.info-md ul, .info-md ol {{ margin: 8px 0 8px 22px; padding: 0; }}
.info-md li {{ margin: 3px 0; }}
.info-md blockquote {{ border-left: 3px solid #b59; margin: 10px 0; padding: 4px 12px; color: #555; font-style: italic; }}
.info-md a {{ color: #6a3d9a; text-decoration: underline; }}
.info-md a:hover {{ color: #b06; }}
.info-md img {{ max-width: 100%; border-radius: 6px; margin: 8px 0; }}
.info-md code {{ background: #f0eef3; padding: 1px 5px; border-radius: 3px; font-size: 0.92em; color: #a30; }}
.info-md hr {{ border: none; border-top: 1px solid #ddd; margin: 12px 0; }}
{css_extra}</style></head><body><h1>📅 VK Poster</h1>
<div class="toolbar"><span>{len(rows)} праздников · {today_civil.strftime('%d.%m.%Y')}</span>
<div><a href="https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays" target="_blank" rel="noopener">📅 Праздники</a><a class="secondary" href="https://app.pagescms.org/bukvica49/vk-poster/main/file/chertogs" target="_blank" rel="noopener">🕯 Чертоги</a><a class="secondary" href="https://app.pagescms.org/bukvica49/vk-poster/main/file/krugolyety" target="_blank" rel="noopener">🌀 Круголеты</a><a class="secondary" href="https://app.pagescms.org/bukvica49/vk-poster/main/collection/holidays/new" target="_blank" rel="noopener" title="Добавить новый праздник">➕ Новый</a></div></div>
{''.join(cards)}{js_extra}</body></html>'''
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    print(f'✅ _site/index.html — {len(rows)} постов')

if __name__ == '__main__':
    build()
