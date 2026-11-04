(function () {
  'use strict';
  const KEY = 'vp-prefs';
  let prefs = JSON.parse(localStorage.getItem(KEY) || '{}');
  const save = () => localStorage.setItem(KEY, JSON.stringify(prefs));

  // ---------- CSS ----------
  const css = document.createElement('style');
  css.textContent = `
    .vp-topbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 16px;padding:12px 14px;background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
    html[data-theme="dark"] .vp-topbar{background:#1e1e28}
    .vp-search-input{flex:1 1 260px;min-width:180px;padding:8px 12px;font:inherit;font-size:14px;border:1px solid #d4d4d8;border-radius:8px;background:#fff;color:inherit}
    html[data-theme="dark"] .vp-search-input{background:#12121a;border-color:#3a3a48;color:#e5e5ee}
    .vp-search-input:focus{outline:2px solid #2563eb33;border-color:#2563eb}
    .vp-search-count{font-size:12px;color:#666;white-space:nowrap}
    html[data-theme="dark"] .vp-search-count{color:#9a9aad}
    .vp-icon-btn{width:38px;height:38px;font-size:18px;cursor:pointer;border:1px solid #d4d4d8;border-radius:8px;background:#f8f8fa;display:inline-flex;align-items:center;justify-content:center}
    html[data-theme="dark"] .vp-icon-btn{background:#262632;border-color:#3a3a48;color:#e5e5ee}
    .vp-icon-btn:hover{background:#eef;transform:translateY(-1px)}
    .vp-settings-panel{background:#fff;border:1px solid #ddd;border-radius:10px;padding:16px;margin-bottom:16px;box-shadow:0 4px 16px rgba(0,0,0,.08);max-width:820px}
    html[data-theme="dark"] .vp-settings-panel{background:#1e1e28;border-color:#3a3a48;color:#e5e5ee}
    .vp-settings-panel h3{margin:0 0 12px;font-size:16px}
    .vp-row{display:block;margin:10px 0;font-size:14px}
    .vp-row label{cursor:pointer}
    .vp-hint{font-size:12px;color:#887}
    .vp-hint a{color:#4a7ddb}
    .vp-btn{padding:6px 12px;border:1px solid #d4d4d8;border-radius:6px;background:#f8f8fa;cursor:pointer;font:inherit;margin-right:6px}
    html[data-theme="dark"] .vp-btn{background:#262632;border-color:#3a3a48;color:#e5e5ee}
    .vp-btn:hover{background:#eef}
    .vp-bg-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:8px;margin:8px 0;max-height:260px;overflow-y:auto;padding:2px}
    .vp-bg-tile{aspect-ratio:1;border-radius:8px;border:2px solid transparent;background-size:cover;background-position:center;cursor:pointer;padding:0;min-height:60px;background-color:#eee}
    .vp-bg-tile.active{border-color:#2563eb;box-shadow:0 0 0 2px #2563eb33}
    .vp-bg-tile.vp-bg-none{display:flex;align-items:center;justify-content:center;font-size:20px;color:#999;background:#fafafa}
    html[data-theme="dark"] .vp-bg-tile.vp-bg-none{background:#262632;color:#6a6a80}
    .vp-bg-overlay{position:fixed;inset:0;z-index:-1;background-size:cover;background-position:center;background-attachment:fixed;opacity:.22;pointer-events:none}
    html[data-theme="dark"] .vp-bg-overlay{opacity:.14}
    html[data-theme="dark"] body{background:#121218;color:#e5e5ee}
    html[data-theme="dark"] .card,html[data-theme="dark"] .toolbar{background:#1e1e28;color:#e5e5ee}
    html[data-theme="dark"] .slavic{background:#262632;color:#b0b0c5}
    html[data-theme="dark"] .no-img{background:#262632;color:#6a6a80}
    html[data-theme="dark"] .in{color:#9a9aad}
    html[data-theme="dark"] .info-md h1,html[data-theme="dark"] .info-md h2,html[data-theme="dark"] .info-md h3{color:#d8d0ee}
    html[data-theme="dark"] .info-md code{background:#2a2a38;color:#f0a0a0}
    html[data-theme="dark"] .info-md blockquote{border-color:#4a4a5a;color:#a0a0b5}
  `;
  document.head.appendChild(css);

  // ---------- helpers ----------
  const MONTHS = ['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь'];
  const MONTHS_SHORT = MONTHS.map(m => m.slice(0, 3));

  function expandDate(when) {
    const m = when.match(/(\d{2})\.(\d{2})\.(\d{4})/);
    if (!m) return when;
    const [, d, mo, y] = m;
    const i = parseInt(mo, 10) - 1;
    const full = MONTHS[i] || '', s = MONTHS_SHORT[i] || '';
    return [when, `${d}.${mo}`, `${d}.${mo}.${y}`, `${mo}.${d}`,
            `${y}-${mo}-${d}`, y, full, s, `${d} ${s}`, `${d} ${full}`].join(' ');
  }

  function cardIndex(card) {
    if (card.dataset.vpIdx !== undefined) return card.dataset.vpIdx;
    const when = card.querySelector('.when')?.textContent || '';
    const slug = card.querySelector('[data-slug]')?.dataset.slug || '';
    const h2 = card.querySelector('h2')?.textContent || '';
    const body = card.querySelector('.meta')?.textContent || '';
    const text = (h2 + ' ' + body + ' ' + slug + ' ' + expandDate(when) + ' ' + card.textContent).toLowerCase();
    card.dataset.vpIdx = text;
    return text;
  }

  function doFilter(q) {
    const cards = document.querySelectorAll('.card');
    const s = q.trim().toLowerCase();
    let n = 0;
    cards.forEach(card => {
      const m = !s || cardIndex(card).includes(s);
      card.style.display = m ? '' : 'none';
      if (m) n++;
    });
    const c = document.getElementById('vp-search-count');
    if (c) c.textContent = s ? `${n} / ${cards.length}` : '';
  }

  function applyTheme() {
    if (prefs.theme === 'dark') document.documentElement.dataset.theme = 'dark';
    else delete document.documentElement.dataset.theme;
  }

  function applyBackground() {
    let bd = document.getElementById('vp-bg-overlay');
    if (prefs.background) {
      if (!bd) { bd = document.createElement('div'); bd.id = 'vp-bg-overlay'; bd.className = 'vp-bg-overlay'; document.body.appendChild(bd); }
      bd.style.backgroundImage = `url('${prefs.background}')`;
    } else if (bd) bd.remove();
  }

  function collectBackgrounds() {
    const s = new Set();
    document.querySelectorAll('.card img').forEach(i => { const src = i.getAttribute('src'); if (src) s.add(src); });
    Object.keys(prefs.userBackgrounds || {}).forEach(k => s.add(k));
    return Array.from(s);
  }

  // ---------- UI ----------
  function buildUI() {
    const h1 = document.querySelector('h1');
    if (!h1 || document.getElementById('vp-topbar')) return;

    const bar = document.createElement('div');
    bar.id = 'vp-topbar'; bar.className = 'vp-topbar';
    bar.innerHTML = `
      <input type="search" id="vp-search-input" class="vp-search-input"
             placeholder="🔍 Найти праздник (название, дата, slug, текст)...">
      <span id="vp-search-count" class="vp-search-count"></span>
      <button id="vp-settings-btn" class="vp-icon-btn" title="Настройки">⚙️</button>`;
    h1.insertAdjacentElement('afterend', bar);

    const panel = document.createElement('div');
    panel.id = 'vp-settings-panel'; panel.className = 'vp-settings-panel'; panel.style.display = 'none';
    panel.innerHTML = `
      <h3>⚙️ Настройки вида</h3>
      <label class="vp-row"><input type="checkbox" id="vp-night"> 🌙 Ночной режим</label>
      <div class="vp-row"><b>🖼 Фон страницы:</b></div>
      <div class="vp-bg-grid" id="vp-bg-grid"></div>
      <div class="vp-row">
        <button id="vp-bg-upload" class="vp-btn">⬆ Загрузить со своего компьютера</button>
        <button id="vp-bg-reset" class="vp-btn">↺ Убрать фон</button>
      </div>
      <div class="vp-row vp-hint">
        Свои фоны хранятся только в этом браузере. Правый клик по плитке — удалить.
        Для всех посетителей — залей в <code>images/</code> через
        <a href="https://app.pagescms.org/bukvica49/vk-poster/main/file/backgrounds" target="_blank" rel="noopener">PagesCMS</a>.
      </div>`;
    bar.insertAdjacentElement('afterend', panel);

    document.getElementById('vp-search-input').addEventListener('input', e => doFilter(e.target.value));
    document.getElementById('vp-search-input').addEventListener('keydown', e => { if (e.key === 'Escape') { e.target.value = ''; doFilter(''); } });
    document.getElementById('vp-settings-btn').addEventListener('click', () => {
      panel.style.display = panel.style.display === 'none' ? '' : 'none';
    });

    const night = document.getElementById('vp-night');
    night.checked = prefs.theme === 'dark';
    night.addEventListener('change', () => { prefs.theme = night.checked ? 'dark' : 'light'; save(); applyTheme(); });

    document.getElementById('vp-bg-upload').addEventListener('click', () => {
      const inp = document.createElement('input'); inp.type = 'file'; inp.accept = 'image/*';
      inp.addEventListener('change', () => {
        const f = inp.files[0]; if (!f) return;
        if (f.size > 4 * 1024 * 1024) { alert('Файл больше 4 МБ — уменьши.'); return; }
        const r = new FileReader();
        r.onload = () => {
          prefs.userBackgrounds = prefs.userBackgrounds || {};
          prefs.userBackgrounds[r.result] = { name: f.name, added: Date.now() };
          prefs.background = r.result; save(); applyBackground(); renderBgGrid();
        };
        r.readAsDataURL(f);
      });
      inp.click();
    });

    document.getElementById('vp-bg-reset').addEventListener('click', () => {
      delete prefs.background; save(); applyBackground(); renderBgGrid();
    });

    renderBgGrid();
  }

  function renderBgGrid() {
    const grid = document.getElementById('vp-bg-grid'); if (!grid) return;
    grid.innerHTML = '';
    const none = document.createElement('button');
    none.className = 'vp-bg-tile vp-bg-none'; none.textContent = '∅'; none.title = 'Без фона';
    if (!prefs.background) none.classList.add('active');
    none.addEventListener('click', () => { delete prefs.background; save(); applyBackground(); renderBgGrid(); });
    grid.appendChild(none);

    collectBackgrounds().forEach(src => {
      const b = document.createElement('button');
      b.className = 'vp-bg-tile';
      b.style.backgroundImage = `url('${src}')`;
      b.title = src.startsWith('data:') ? 'Локальный файл' : src;
      if (prefs.background === src) b.classList.add('active');
      b.addEventListener('click', () => { prefs.background = src; save(); applyBackground(); renderBgGrid(); });
      b.addEventListener('contextmenu', ev => {
        ev.preventDefault();
        if (src.startsWith('data:')) {
          if (confirm('Удалить этот локальный фон?')) {
            delete prefs.userBackgrounds[src];
            if (prefs.background === src) delete prefs.background;
            save(); applyBackground(); renderBgGrid();
          }
        } else alert('Этот файл из репозитория — удаляется через PagesCMS → images/');
      });
      grid.appendChild(b);
    });
  }

  applyTheme(); applyBackground();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => { buildUI(); doFilter(''); });
  else { buildUI(); doFilter(''); }
})();
