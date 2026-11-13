(function () {
  'use strict';
  const KEY = 'vp-prefs';
  let prefs = JSON.parse(localStorage.getItem(KEY) || '{}');
  const save = () => localStorage.setItem(KEY, JSON.stringify(prefs));

  const css = document.createElement('style');
  css.textContent = `
    .vp-topbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 16px;padding:12px 14px;background:#fff;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
    html[data-theme="dark"] .vp-topbar{background:#1e1e28}
    .vp-search-input{flex:1 1 260px;min-width:180px;padding:8px 12px;font:inherit;font-size:14px;border:1px solid #d4d4d8;border-radius:8px;background:#fff;color:inherit}
    html[data-theme="dark"] .vp-search-input{background:#12121a;border-color:#3a3a48;color:#e5e5ee}
    .vp-search-count{font-size:12px;color:#666;white-space:nowrap}
    html[data-theme="dark"] .vp-search-count{color:#9a9aad}
    .vp-icon-btn{width:38px;height:38px;font-size:18px;cursor:pointer;border:1px solid #d4d4d8;border-radius:8px;background:#f8f8fa;display:inline-flex;align-items:center;justify-content:center}
    html[data-theme="dark"] .vp-icon-btn{background:#262632;border-color:#3a3a48;color:#e5e5ee}
    .vp-icon-btn:hover{background:#eef;transform:translateY(-1px)}
    .vp-settings-panel{background:#fff;border:1px solid #ddd;border-radius:10px;padding:16px;margin-bottom:16px;box-shadow:0 4px 16px rgba(0,0,0,.08);max-width:820px}
    html[data-theme="dark"] .vp-settings-panel{background:#1e1e28;border-color:#3a3a48;color:#e5e5ee}
    .vp-settings-panel h3{margin:0 0 12px;font-size:16px}
    .vp-row{display:block;margin:10px 0;font-size:14px}
    .vp-btn{padding:6px 12px;border:1px solid #d4d4d8;border-radius:6px;background:#f8f8fa;cursor:pointer;font:inherit;margin-right:6px}
    html[data-theme="dark"] .vp-btn{background:#262632;border-color:#3a3a48;color:#e5e5ee}
    .vp-btn:hover{background:#eef}
    .vp-bg-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(72px,1fr));gap:8px;margin:8px 0;max-height:260px;overflow-y:auto;padding:2px}
    .vp-bg-tile{aspect-ratio:1;border-radius:8px;border:2px solid transparent;background-size:cover;background-position:center;cursor:pointer;padding:0;min-height:60px;background-color:#eee}
    .vp-bg-tile.active{border-color:#2563eb;box-shadow:0 0 0 2px #2563eb33}
    .vp-bg-tile.vp-bg-none{display:flex;align-items:center;justify-content:center;font-size:20px;color:#999;background:#fafafa}
    .vp-bg-overlay{position:fixed;inset:0;z-index:-1;background-size:cover;background-position:center;background-attachment:fixed;opacity:.22;pointer-events:none}
    .vp-toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(20px);padding:10px 20px;background:#333;color:#fff;border-radius:8px;font-size:14px;opacity:0;pointer-events:none;transition:all .25s;z-index:9999}
    .vp-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
    .vp-toast.ok{background:#2a7a3a}.vp-toast.err{background:#c33}
    html[data-theme="dark"] body{background:#121218;color:#e5e5ee}
    html[data-theme="dark"] .card,html[data-theme="dark"] .toolbar{background:#1e1e28;color:#e5e5ee}
  `;
  document.head.appendChild(css);

  const MONTHS = ['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь'];
  const MONTHS_SHORT = MONTHS.map(m => m.slice(0, 3));
  function expandDate(when) {
    const m = when.match(/(\d{2})\.(\d{2})\.(\d{4})/);
    if (!m) return when;
    const [, d, mo, y] = m;
    const i = parseInt(mo, 10) - 1;
    const full = MONTHS[i] || '', s = MONTHS_SHORT[i] || '';
    return [when,`${d}.${mo}`,`${d}.${mo}.${y}`,`${mo}.${d}`,`${y}-${mo}-${d}`,y,full,s,`${d} ${s}`,`${d} ${full}`].join(' ');
  }
  function cardIndex(card) {
    if (card.dataset.vpIdx !== undefined) return card.dataset.vpIdx;
    const when = card.querySelector('.when')?.textContent || '';
    const slug = card.querySelector('[data-slug]')?.dataset.slug || '';
    const h2 = card.querySelector('h2')?.textContent || '';
    const body = card.querySelector('.meta')?.textContent || '';
    const text = (h2+' '+body+' '+slug+' '+expandDate(when)+' '+card.textContent).toLowerCase();
    card.dataset.vpIdx = text; return text;
  }
  function doFilter(q) {
    const cards = document.querySelectorAll('.card');
    const s = q.trim().toLowerCase(); let n = 0;
    cards.forEach(card => { const m = !s || cardIndex(card).includes(s); card.style.display = m ? '' : 'none'; if (m) n++; });
    const c = document.getElementById('vp-search-count');
    if (c) c.textContent = s ? `${n} / ${cards.length}` : '';
  }
  function toast(msg, kind) {
    let t = document.getElementById('vp-toast');
    if (!t) { t = document.createElement('div'); t.id = 'vp-toast'; t.className = 'vp-toast'; document.body.appendChild(t); }
    t.textContent = msg; t.className = 'vp-toast show' + (kind ? ' ' + kind : '');
    clearTimeout(t._to); t._to = setTimeout(() => { t.className = 'vp-toast'; }, 2000);
  }
  async function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(text);
      else { const ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); }
      return true;
    } catch (e) { return false; }
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

  // ═══════════ старослав A ═══════════
  const CFG = window.VP_CONFIG || {};
  const YAT = CFG.yat || {
    "хлеб":"хлѣб","хлеба":"хлѣба","хлебом":"хлѣбом","хлебе":"хлѣбѣ",
    "лес":"лѣс","леса":"лѣса","лесу":"лѣсу","лесом":"лѣсом","лесе":"лѣсѣ","лесной":"лѣсной","лесные":"лѣсные",
    "снег":"снѣг","снега":"снѣга","снегом":"снѣгом","снегу":"снѣгу","снежный":"снѣжный",
    "ветер":"вѣтер","ветра":"вѣтра","ветром":"вѣтром","ветре":"вѣтрѣ",
    "месяц":"мѣсяц","месяца":"мѣсяца","месяцем":"мѣсяцем",
    "звезда":"звѣзда","звезды":"звѣзды","звезде":"звѣздѣ","звездой":"звѣздой","звездный":"звѣздный",
    "цвет":"цвѣт","цвета":"цвѣта","цветов":"цвѣтов","цветок":"цвѣток","цветы":"цвѣты",
    "река":"рѣка","реки":"рѣки","реке":"рѣкѣ","реку":"рѣку","рекой":"рѣкой",
    "сено":"сѣно","тело":"тѣло","тела":"тѣла","телом":"тѣлом",
    "песня":"пѣсня","песни":"пѣсни","песню":"пѣсню","петь":"пѣть","пел":"пѣл","пела":"пѣла",
    "лето":"лѣто","лета":"лѣта","летом":"лѣтом","летний":"лѣтній",
    "зверь":"звѣрь","зверя":"звѣря","зверей":"звѣрей",
    "дед":"дѣд","деда":"дѣда","деду":"дѣду","деды":"дѣды",
    "дети":"дѣти","детей":"дѣтей","детям":"дѣтям","детство":"дѣтство",
    "обед":"обѣд","обеда":"обѣда",
    "ответ":"отвѣт","ответить":"отвѣтить","ответил":"отвѣтил",
    "привет":"привѣт","совет":"совѣт","сосед":"сосѣд",
    "успех":"успѣх","успеть":"успѣть","успел":"успѣл",
    "смех":"смѣх","смеха":"смѣха","смеяться":"смѣяться","смешной":"смѣшной",
    "грех":"грѣх","греха":"грѣха","грешный":"грѣшный",
    "стрела":"стрѣла","стрелы":"стрѣлы",
    "венок":"вѣнок","венка":"вѣнка",
    "вера":"вѣра","веры":"вѣры","вере":"вѣрѣ","веру":"вѣру","верой":"вѣрой",
    "верить":"вѣрить","верю":"вѣрю","верит":"вѣрит","верят":"вѣрят","верил":"вѣрил",
    "верный":"вѣрный","верная":"вѣрная",
    "вечный":"вѣчный","вечная":"вѣчная","вечность":"вѣчность",
    "свет":"свѣт","света":"свѣта","светом":"свѣтом",
    "светлый":"свѣтлый","светлая":"свѣтлая","светлые":"свѣтлые",
    "тень":"тѣнь","тени":"тѣни",
    "делать":"дѣлать","делаю":"дѣлаю","делает":"дѣлает","делал":"дѣлал",
    "смотреть":"смотрѣть","смотрел":"смотрѣл",
    "видеть":"видѣть","видел":"видѣл",
    "треба":"трѣба","требу":"трѣбу","требы":"трѣбы",
    "обряд":"обрѧдъ","обряда":"обрѧда","обряды":"обрѧды",
    "жертва":"жертва","жертвы":"жертвы",
    "капище":"капище","капища":"капища",
    "молитва":"молитва","молитвы":"молитвы",
    "идол":"идолъ","идола":"идола","идолы":"идолы",
    "дух":"духъ","духа":"духа","духом":"духом",
    "душа":"душа","души":"души","душу":"душу","душой":"душой",
    "предки":"предки","предков":"предков","предкам":"предкам",
    "род":"родъ","рода":"рода","роду":"роду",
    "бог":"богъ","бога":"бога","богу":"богу","богом":"богом",
    "богиня":"богиня","богини":"богини","богине":"богинѣ",
    "белый":"бѣлый","белая":"бѣлая","белые":"бѣлые",
    "смелый":"смѣлый","смелая":"смѣлая",
    "целый":"цѣлый","целая":"цѣлая",
    "зрелый":"зрѣлый","спелый":"спѣлый",
    "последний":"послѣдній","последняя":"послѣдняя",
    "время":"врѣмя","времени":"врѣмени",
    "неделя":"недѣля","недели":"недѣли","неделю":"недѣлю",
    "век":"вѣкъ","века":"вѣка","веком":"вѣком",
    "иметь":"имѣть","имею":"имѣю","имеет":"имѣет","имел":"имѣл",
    "уметь":"умѣть","умею":"умѣю","умеет":"умѣет",
    "спеть":"спѣть","спел":"спѣл",
    "светить":"свѣтить","светит":"свѣтит",
    "веять":"вѣять","веет":"вѣет"
  };
  const GEN_STOP = new Set(["всего","сего","чего","него","его","того","этого","одного","самого","моего","твоего","своего","нашего","вашего","кого","никого","ничего"]);
  function slavicA(text) {
    if (!text) return '';
    text = text.replace(/[А-Яа-яЁё]+/g, w => {
      const r = YAT[w.toLowerCase()]; if (!r) return w;
      return w[0] === w[0].toUpperCase() ? r[0].toUpperCase() + r.slice(1) : r;
    });
    text = text.replace(/([А-Яа-яЁё]+)(ого|его)(?![А-Яа-яЁё])/g, (m, stem, suf) => {
      if (GEN_STOP.has(m.toLowerCase())) return m;
      return stem + (suf === 'ого' ? 'аго' : 'яго');
    });
    text = text.replace(/([Ии])(?=[аеиоуыэюяёАЕИОУЫЭЮЯЁйЙ])/g, (_, c) => c === 'И' ? 'І' : 'і');
    text = text.replace(/[А-Яа-яЁё]+/g, w => {
      if (w.length < 2) return w;
      if (w === w.toUpperCase()) return w;
      const last = w[w.length - 1];
      if ('ьйъЬЙЪаеёиоуыэюяАЕЁИОУЫЭЮЯ'.includes(last)) return w;
      return w + 'ъ';
    });
    return text;
  }

  // ═══════════ старослав Б ═══════════
  const SLAV_B = CFG.slav_b || {
    "город":"град","города":"града","городу":"граду","городом":"градом","городе":"градѣ",
    "голова":"глава","головы":"главы","голову":"главу","головой":"главой",
    "золото":"злато","золота":"злата",
    "болото":"блато","болота":"блата",
    "ворота":"врата","ворот":"вратъ",
    "борода":"брада","бороды":"брады",
    "корова":"крава","коровы":"краы",
    "дорога":"драга","дороги":"драги",
    "порох":"прахъ","холод":"хладъ","холода":"хлада","холодный":"хладный",
    "молодой":"младъ","молодая":"млада","молодые":"млади","молодость":"младость",
    "голод":"гладъ","голодный":"гладный",
    "сладкий":"сладкій","сладкая":"сладка",
    "молоко":"млеко","молока":"млека",
    "волосы":"власи","волос":"власъ",
    "шелом":"шлѣмъ",
    "берег":"брѣгъ","берега":"брѣга","берегу":"брѣгу",
    "серебро":"сребро","серебра":"сребра",
    "дерево":"дрѣво","дерева":"дрѣва","деревья":"дрѣва",
    "середина":"срѣдина",
    "еще":"ѥще","ещё":"ѥще",
    "один":"ѥдинъ","одна":"ѥдина","одно":"ѥдино","одни":"ѥдини",
    "он":"ѡнъ","она":"ѡна","оно":"ѡно","они":"ѡни",
    "это":"сѥ","этот":"съ","эта":"сі","эти":"сіи",
    "все":"вьси","всё":"вьсѥ","вся":"вьсıа",
    "человек":"чловѣкъ","человека":"чловѣка","люди":"людиѥ","людей":"людии",
    "день":"дьнь","дня":"дьне","дни":"дьни",
    "ночь":"ношть","ночи":"ношти",
    "сын":"сынъ","брат":"братръ","сестра":"сестра",
    "отец":"отьць","отца":"отьца",
    "мать":"мати","матери":"матере",
    "дочь":"дъшти","дочери":"дъштере",
    "говорить":"глаголати","говорит":"глаголеть","говорил":"глаголалъ","сказать":"рещи","сказал":"рече",
    "мочь":"мощи","могу":"могу","может":"можеть","мог":"моглъ",
    "хочу":"хоштѫ","хочет":"хоштеть","хотел":"хотѣлъ",
    "дать":"дати","дает":"даеть","дал":"далъ",
    "идти":"ити","идет":"идеть","шел":"шьлъ",
    "знать":"вѣдѣти","знает":"вѣсть","знал":"вѣдѣлъ"
  };
  function slavicB(text) {
    if (!text) return '';
    text = slavicA(text);
    text = text.replace(/[А-Яа-яЁё]+/g, w => {
      const r = SLAV_B[w.toLowerCase()]; if (!r) return w;
      return w[0] === w[0].toUpperCase() ? r[0].toUpperCase() + r.slice(1) : r;
    });
    text = text.replace(/я/g, 'ѧ').replace(/Я/g, 'Ѩ');
    text = text.replace(/ю/g, 'ѭ').replace(/Ю/g, 'Ѭ');
    text = text.replace(/у/g, 'оу').replace(/У/g, 'Оу');
    return text;
  }

  // ═══════════ старослав В (AI) ═══════════
  function getAiEndpoint() { return localStorage.getItem('vp-ai-endpoint') || ''; }
  function setAiEndpoint(url) { if (url) localStorage.setItem('vp-ai-endpoint', url); else localStorage.removeItem('vp-ai-endpoint'); }
  async function slavicC(text) {
    const url = getAiEndpoint();
    if (!url) throw new Error('URL AI-сервера не настроен');
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
    if (!r.ok) throw new Error((await r.text()) || `HTTP ${r.status}`);
    const data = await r.json();
    return data.result || data.text || '';
  }

  // ═══════════ формат + шаблон ═══════════
  function smartHeaders(lines) {
    const isEmojiStart = /^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}•●★☆▪▫—→☀☾☽]/u;
    const isSeparator = s => /^(---|\*\*\*|===|___|\s*[─═━]{3,}\s*)$/.test(s);
    const isCaps = s => {
      const letters = s.replace(/[^А-Яа-яЁёA-Za-z]/g, '');
      if (letters.length < 3) return false;
      const caps = s.replace(/[^А-ЯЁA-Z]/g, '');
      return caps.length >= 2 && caps.length / letters.length >= 0.8;
    };
    const endsColon = s => /[:：]$/.test(s) && s.length < 60;
    const isolated = new Array(lines.length).fill(false);
    for (let i = 0; i < lines.length; i++) {
      const prev = i === 0 ? '' : lines[i-1];
      const nxt  = i === lines.length - 1 ? '' : lines[i+1];
      if (!prev && !nxt && lines[i]) isolated[i] = true;
    }
    let inFireBlock = false;
    for (let i = 0; i < lines.length; i++) {
      const l = lines[i]; if (!l) continue;
      if (isSeparator(l)) { inFireBlock = false; continue; }
      if (isEmojiStart.test(l)) continue;
      if (l.startsWith('•')) continue;
      if (l.startsWith('**')) continue;
      const header = isCaps(l) || endsColon(l) || isolated[i];
      if (!header) continue;
      if (!inFireBlock) { lines[i] = '🔥 ' + l + ' 🔥'; inFireBlock = true; }
      // последующие заголовки блока — без обёртки
    }
  }

  function smartEmoji(lines, repeat) {
    repeat = Math.max(1, Math.min(5, repeat || 1));
    const RULES = [
      {re: /(внимани|важно|осторожн)/i, em: '⚠️', pr: 100},
      {re: /(закон|устав|запрещ|правил)/i, em: '📜', pr: 90},
      {re: /(нельзя|избегай|остерег)/i, em: '❌', pr: 90},
      {re: /(совет|рекоменд|лучше)/i, em: '💡', pr: 80},
      {re: /(бог|богин|молитв|обряд|покровител)/i, em: '🕯', pr: 80},
      {re: /(дерев|лес|природ)/i, em: '🌳', pr: 70},
      {re: /(праздн|славь|велича|поздравл)/i, em: '🎉', pr: 70},
      {re: /(хлеб|пир|блюд|трапез)/i, em: '🍞', pr: 70},
      {re: /(когда|врем|срок|час)/i, em: '⏰', pr: 60},
      {re: /(делай|выполн|исполн)/i, em: '✅', pr: 50},
      {re: /\?\s*$/, em: '❓', pr: 40},
    ];
    for (let i = 0; i < lines.length; i++) {
      const l = lines[i]; if (!l) continue;
      if (/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}•●★🔥]/u.test(l)) continue;
      if (l.startsWith('***') || l.startsWith('**')) continue;
      let best = null;
      for (const r of RULES) if (r.re.test(l) && (!best || r.pr > best.pr)) best = r;
      if (best) { const _em = best.em.repeat(repeat); lines[i] = _em + ' ' + l; }
    }
  }

  function formatForVK(text, opts) {
    opts = opts || {};
    const raw = text.replace(/\r\n/g, '\n');
    const lines = raw.split('\n').map(l => l.replace(/[ \t]+/g, ' ').trim());
    const out = []; let empties = 0;
    for (const l of lines) {
      if (!l) { empties++; continue; }
      if (empties > 0) out.push(''); empties = 0;
      out.push(l);
    }
    for (let i = 0; i < out.length; i++) {
      if (/^[-–—*]\s+/.test(out[i])) out[i] = '• ' + out[i].replace(/^[-–—*]\s+/, '');
    }
    if (opts.smartHeaders) smartHeaders(out);
    if (opts.smartEmoji)   smartEmoji(out, opts.emojiRepeat);
    return out.join('\n').trim();
  }

  function stripEmoji(text) {
    if (!text) return { text: '', count: 0 };
    const RE = /[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2300}-\u{23FF}\u{2B00}-\u{2BFF}\u{FE00}-\u{FE0F}\u{200D}\u{20E3}\u{E0020}-\u{E007F}]/gu;
    const UNIT = /[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2300}-\u{23FF}\u{2B00}-\u{2BFF}]/gu;
    const count = (text.match(UNIT) || []).length;
    const cleaned = text
      .replace(RE, '')
      .replace(/[ \t]{2,}/g, ' ')
      .replace(/[ \t]+$/gm, '')
      .replace(/^[ \t]+/gm, '')
      .replace(/\n{3,}/g, '\n\n')
      .replace(/^\n+|\n+$/g, '');
    return { text: cleaned, count };
  }

  function stripLinks(text) {
    if (!text) return { text: '', count: 0 };
    let count = 0;
    const TLD = 'ru|рф|com|org|net|io|su|uk|de|fr|info|biz|me|tv|co|site|online|store|app|dev|xyz|pro|club|live|news|blog|shop|top';
    const RE_DOMAIN = new RegExp(
      '(?<![\\w@])(?:[a-zа-яё0-9][a-zа-яё0-9-]*\\.)+(?:' + TLD + ')(?:\\/[^\\s]*)?\\b',
      'giu'
    );
    const cleaned = text
      .replace(/\[[^\]]*\]\([^)]+\)/gu, () => { count++; return ''; })
      .replace(/https?:\/\/[^\s<>"'()[\]{}]+/giu, () => { count++; return ''; })
      .replace(RE_DOMAIN, () => { count++; return ''; })
      .replace(/[ \t]{2,}/g, ' ')
      .replace(/[ \t]+$/gm, '')
      .replace(/^[ \t]+/gm, '')
      .replace(/\n{3,}/g, '\n\n')
      .replace(/^\n+|\n+$/g, '');
    return { text: cleaned, count };
  }

  function captureTemplate(text) {
    const blocks = text.split(/\n\s*\n/).map(b => b.trim()).filter(Boolean);
    return blocks.map(b => {
      if (!b.includes('\n') && /^\*\*.+\*\*$/.test(b)) return 'title';
      if (/^[•\-–—*]\s+/m.test(b)) return 'list';
      return 'para';
    });
  }
  function applyTemplate(src, pattern) {
    let parts = src.split(/\n\s*\n/).map(b => b.trim()).filter(Boolean);
    if (parts.length === 1) parts = src.split(/\n+/).map(s => s.trim()).filter(Boolean);
    const out = [];
    parts.forEach((part, i) => {
      const type = i < pattern.length ? pattern[i] : 'para';
      if (type === 'title') out.push('**' + part.replace(/^\*\*|\*\*$/g, '') + '**');
      else if (type === 'list') {
        const lines = part.split('\n').map(l => l.trim()).filter(Boolean);
        out.push(lines.map(l => '• ' + l.replace(/^[•\-–—*]\s+/, '')).join('\n'));
      } else out.push(part);
    });
    return out.join('\n\n');
  }
  function getTemplate() { return prefs.template || null; }
  function setTemplate(tpl) { prefs.template = tpl; save(); }
  function clearTemplate() { delete prefs.template; save(); }

  const EMOJI = CFG.emoji || {
    "Природа":["☀️","🌙","⭐","🌊","🌲","🌿","🌸","❄️","🔥","💧","🌾","☁️","🌄","🌅"],
    "Обряд":["🕯","🙏","🔮","📿","🗿","🧿","🥖","🪔","☦","✠"],
    "Праздник":["🎉","🎊","✨","🎁","🥂","🍷","🎈","🎆","🎇"],
    "Тотем":["🐺","🐻","🦅","🐎","🦌","🐍","🦉","🐗","🐢","🦢"],
    "Еда":["🍯","🥖","🍲","🥧","🍵","🍞","🧀","🍎","🍇","🥛"],
    "Эмоции":["😊","🙂","😌","🤗","🕊","💫","🌠","💖","🌟"]
  };
  const SYMBOLS = CFG.symbols || {
    "Звёзды":["✦","✧","✨","⭐","★","☆","✶","✷","✸","✹","✺"],
    "Линии":["─","━","═","║","•","·","◦","▸","▹","●","○","◆","◇","▪","▫"],
    "Рамки":["「","」","『","』","❝","❞","╭","╮","╰","╯","【","】"],
    "Стрелки":["→","←","↑","↓","⇒","⇐","↔","⇔","➤","➜","➔","➢"],
    "Галочки":["✓","✔","✗","✘","☑","☐","☒"],
    "Обряд":["☀","☾","☽","🕯","⛧","⊕","✠","☦","🜂","🜁","🜃","🜄"],
    "Прочее":["§","¶","№","°","′","″","‰","†","‡","⌘","™","©","®"]
  };

  // ═══════════ POPUP ═══════════
  function openEditorWindow() {
    if (window._vpEditorWin && !window._vpEditorWin.closed) {
      let _broken = false, _reason = '';
      try {
        const _doc = window._vpEditorWin.document;
        const _href = window._vpEditorWin.location.href;
        if (!_doc || !_doc.documentElement || !_href || _href.startsWith('about:')) { _broken = true; _reason = 'about:blank'; }
        else if (_doc.getElementById('vp-boot')) { _broken = true; _reason = 'stuck at #vp-boot'; }
        else if (_href.indexOf('blob:') === 0 && !_doc.documentElement.hasAttribute('data-vp-editor-ready')) { _broken = true; _reason = 'blob dead'; }
        else if (!_doc.documentElement.hasAttribute('data-vp-editor-ready')) { _broken = true; _reason = 'no ready marker'; }
      } catch(e) { _broken = true; _reason = 'exception: ' + (e && e.message || e); }
      if (!_broken) {
        try { window._vpEditorWin.focus(); return; } catch(e) { _broken = true; _reason = 'focus fail'; }
      }
      console.warn('[vp] попап сломан (' + _reason + ') — переоткрываю');
      try { window._vpEditorWin.close(); } catch(e){}
      window._vpEditorWin = null;
    }
    let saved = { w: 1000, h: 900 };
    try { saved = Object.assign(saved, JSON.parse(localStorage.getItem('vp-ed-size') || '{}')); } catch(e) {}
    const ww = Math.max(600, Math.min(Number(saved.w) || 1000, 2400));
    const hh = Math.max(500, Math.min(Number(saved.h) || 900, 1600));
    let feats = `width=${ww},height=${hh},menubar=no,toolbar=no,location=no,status=no`;
    // Позиция — только если она РЕАЛЬНО видна на текущем экране
    try {
      if (typeof saved.x === 'number' && typeof saved.y === 'number' && isFinite(saved.x) && isFinite(saved.y)) {
        const scrW = window.screen.availWidth  || 1920;
        const scrH = window.screen.availHeight || 1080;
        const scrL = typeof window.screen.availLeft === 'number' ? window.screen.availLeft : 0;
        const scrT = typeof window.screen.availTop  === 'number' ? window.screen.availTop  : 0;
        const margin = 80;
        const inX = saved.x >= scrL - margin && saved.x <= scrL + scrW - margin;
        const inY = saved.y >= scrT - margin && saved.y <= scrT + scrH - margin;
        if (inX && inY) {
          // Браузер игнорирует left=0,top=0 — воспринимает как "не задано".
          // Поэтому 0 заменяем на 1 (разница невидима глазу).
          const px = Math.round(saved.x); const py = Math.round(saved.y);
          const fx = px === 0 ? 1 : px;
          const fy = py === 0 ? 1 : py;
          feats += `,left=${fx},top=${fy}`;
        } else {
          console.info('[vp] позиция вне экрана, открываю по центру');
        }
      }
    } catch(e) { console.warn('[vp] позиция:', e); }
    const w = window.open('', 'vp-editor', feats);

    // 1) Хак для 0/0: браузер игнорирует left=0,top=0 — шлём 1
    // 2) Двигаем окно через moveTo чтобы обойти WM
    if (w && typeof saved.x === 'number' && typeof saved.y === 'number'
        && isFinite(saved.x) && isFinite(saved.y)) {
      const _mx = Math.round(saved.x), _my = Math.round(saved.y);
      [50, 300, 900, 1500].forEach(ms => setTimeout(() => {
        try { if (w && !w.closed) w.moveTo(_mx, _my); } catch(e) {}
      }, ms));
    }

    // WM-независимая попытка: двигаем окно после создания
    if (w && typeof saved.x === 'number' && isFinite(saved.x)
        && typeof saved.y === 'number' && isFinite(saved.y)) {
      const _mx = Math.round(saved.x), _my = Math.round(saved.y);
      [50, 300, 900].forEach(ms => setTimeout(() => {
        try { if (w && !w.closed) w.moveTo(_mx, _my); } catch(e) {}
      }, ms));
    }
    if (!w) { toast('Разреши всплывающие окна для этого сайта', 'err'); return; }
    window._vpEditorWin = w;

    const html = `<!doctype html><html lang="ru" data-theme="light"><head><meta charset="utf-8">
<title>✍ Редактор текста для ВК</title>
<style>
  :root{--bg-main:#f5f5f7;--bg-panel:#f8f8fa;--bg-field:#fff;--fg-main:#111;--fg-muted:#666;--border:#d4d4d8;--overlay:rgba(245,245,247,.85);--accent:#2563eb}
  :root[data-theme="dark"]{--bg-main:#121218;--bg-panel:#262632;--bg-field:#12121a;--fg-main:#e5e5ee;--fg-muted:#9a9aad;--border:#3a3a48;--overlay:rgba(18,18,24,.85);--accent:#4a7ddb}
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  body{font-family:system-ui,-apple-system,sans-serif;padding:16px 16px 100px;color:var(--fg-main);min-height:100vh;max-width:960px;margin:0 auto;position:relative;background:transparent}
  body::before{content:'';position:fixed;inset:0;z-index:-1;background-image:var(--bg-image,none);background-size:cover;background-position:center;background-color:var(--bg-main)}
  body::after{content:'';position:fixed;inset:0;z-index:-1;background:var(--overlay);display:none}
  body.has-bg::after{display:block}
  .hdr{display:flex;justify-content:space-between;align-items:center;gap:8px;margin:0 0 10px}
  .hdr h1{font-size:18px;margin:0}
  .hdr-btns{display:flex;gap:6px}
  .icon-btn{width:36px;height:36px;font-size:16px;cursor:pointer;border:1px solid var(--border);border-radius:8px;background:var(--bg-panel);color:var(--fg-main);display:inline-flex;align-items:center;justify-content:center;transition:all .12s}
  .icon-btn:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
  .bg-panel{background:var(--bg-panel);border:1px solid var(--border);border-radius:10px;padding:12px;margin:0 0 12px;box-shadow:0 4px 16px rgba(0,0,0,.08)}
  .bg-panel-title{font-weight:600;font-size:13px;margin-bottom:8px}
  .bg-preview{height:80px;border-radius:8px;border:1px solid var(--border);background:var(--bg-field);background-size:cover;background-position:center;display:flex;align-items:center;justify-content:center;color:var(--fg-muted);font-size:12px;margin-bottom:8px}
  .hint{color:var(--fg-muted);font-size:12px;margin-bottom:12px}
  .label{display:block;font-weight:600;font-size:13px;margin:10px 0 4px;color:var(--fg-main)}
  .field{width:100%;padding:10px 12px;font:inherit;font-size:14px;line-height:1.55;border:1px solid var(--border);border-radius:8px;background:var(--bg-field);color:var(--fg-main);resize:vertical;font-family:ui-monospace,monospace;min-height:140px}
  .field:focus{outline:2px solid #2563eb33;border-color:var(--accent)}
  .btns{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
  .btn{padding:8px 14px;border:1px solid var(--border);border-radius:8px;background:var(--bg-panel);cursor:pointer;font:inherit;font-size:13px;color:var(--fg-main);transition:all .12s}
  .btn:hover{background:var(--accent);color:#fff;border-color:var(--accent);transform:translateY(-1px)}
  .btn:disabled{opacity:.5;cursor:wait;transform:none}
  .btn.primary{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
  .btn.slav-a{background:#fff7e6;border-color:#d4a574;color:#8a5a2a}
  .btn.slav-a:hover{background:#f7e8c8;color:#8a5a2a;border-color:#d4a574}
  .btn.slav-b{background:#f0e6ff;border-color:#a07dd4;color:#5a2a8a}
  .btn.slav-b:hover{background:#e0ccff;color:#5a2a8a;border-color:#a07dd4}
  .btn.slav-c{background:#e6f7ff;border-color:#74a4d4;color:#2a5a8a}
  .btn.slav-c:hover{background:#cce8ff;color:#2a5a8a;border-color:#74a4d4}
  :root[data-theme="dark"] .btn.slav-a{background:#3a2f1a;border-color:#8a6a3a;color:#f0d8a8}
  :root[data-theme="dark"] .btn.slav-a:hover{background:#4a3f2a;color:#f0d8a8;border-color:#8a6a3a}
  :root[data-theme="dark"] .btn.slav-b{background:#2a1f3a;border-color:#7a5aa4;color:#d8c8f0}
  :root[data-theme="dark"] .btn.slav-b:hover{background:#3a2f4a;color:#d8c8f0;border-color:#7a5aa4}
  :root[data-theme="dark"] .btn.slav-c{background:#1a2a3a;border-color:#5a7aa4;color:#c8d8f0}
  :root[data-theme="dark"] .btn.slav-c:hover{background:#2a3a4a;color:#c8d8f0;border-color:#5a7aa4}
  .picker{display:grid;grid-template-columns:repeat(auto-fill,minmax(38px,1fr));gap:4px;margin:8px 0;padding:8px;background:var(--bg-panel);border:1px solid var(--border);border-radius:8px;max-height:200px;overflow-y:auto}
  .picker button{width:100%;aspect-ratio:1;font-size:18px;cursor:pointer;border:1px solid var(--border);border-radius:6px;background:var(--bg-field);color:var(--fg-main);display:flex;align-items:center;justify-content:center;padding:0}
  .picker button:hover{background:var(--accent);color:#fff;transform:translateY(-1px)}
  .picker-tabs{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0}
  .picker-tabs button{padding:4px 10px;font-size:12px;border-radius:20px;border:1px solid var(--border);background:var(--bg-panel);cursor:pointer;font-family:inherit;color:var(--fg-main)}
  .picker-tabs button.active{background:var(--accent);color:#fff;border-color:var(--accent)}
  .picker-empty{grid-column:1/-1;text-align:center;font-size:12px;color:var(--fg-muted);padding:16px 8px;line-height:1.4}
  .toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(20px);padding:10px 20px;background:#333;color:#fff;border-radius:8px;font-size:14px;opacity:0;pointer-events:none;transition:all .25s;z-index:9999}
  .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
  .toast.ok{background:#2a7a3a}.toast.err{background:#c33}
  .footer{display:flex;justify-content:space-between;align-items:center;margin-top:12px;font-size:12px;color:var(--fg-muted)}
  .tpl-box{background:var(--bg-panel);border:1px dashed var(--accent);border-radius:10px;padding:12px;margin-top:16px}
  .tpl-status{font-size:12px;color:var(--fg-muted);margin-bottom:6px}
  .tpl-pattern{display:inline-block;padding:2px 8px;background:var(--accent);color:#fff;border-radius:4px;font-family:ui-monospace,monospace;font-size:11px;margin-left:6px}

  .field-wrap{position:relative;margin-bottom:8px}
  .field-wrap .field{margin-bottom:0;padding-right:70px}
  .field-actions{position:absolute;top:6px;right:6px;display:flex;gap:4px;z-index:2;opacity:.55;transition:opacity .15s}
  .field-wrap:hover .field-actions,.field-wrap:focus-within .field-actions{opacity:1}
  .icon-btn-sm{padding:3px 8px;font-size:14px;line-height:1;border:1px solid var(--border);border-radius:5px;background:var(--bg-panel);color:var(--fg-main);cursor:pointer;font-family:inherit;transition:background .12s}
  .icon-btn-sm:hover{background:var(--accent);color:#fff;border-color:var(--accent)}

  /* ── Fit-to-window layout (попап) ── */
  html, body { height: 100dvh; overflow: hidden; }
  body {
    display: flex;
    flex-direction: column;
    padding: 10px 14px;
    margin: 0;
    min-height: 0;
    max-width: none;
  }
  body::before, body::after { z-index: -1; }
  .hdr, .hint, .btns, .footer, .tpl-box, .label, .bg-panel, #picker {
    flex-shrink: 0;
  }
  #picker:not([data-vp-open]) { display: none !important; }
  .hdr            { margin-bottom: 6px; }
  .hint           { margin-bottom: 6px; font-size: 11px; }
  .label          { margin: 6px 0 4px; font-size: 12px; }
  .btns           { margin: 6px 0; }
  .btns .btn      { padding: 6px 10px; font-size: 12px; }
  .footer         { margin-top: 6px; font-size: 11px; }
  .tpl-box        { margin-top: 8px; padding: 8px 10px; }
  .tpl-box h3     { font-size: 13px; margin: 0 0 4px; }
  .tpl-box .hint  { font-size: 11px; }

  .field-wrap {
    flex: 1 1 0;
    min-height: 90px;
    display: flex;
    flex-direction: column;
    margin-bottom: 6px;
  }
  .field-wrap .field {
    flex: 1 1 0;
    min-height: 0;
    width: 100%;
    resize: none;
  }

  #picker  { max-height: 30vh; overflow-y: auto; }
  .picker  { max-height: calc(30vh - 42px); margin: 0; }
  .bg-panel{ max-height: 32vh; overflow-y: auto; }

  @media (max-height: 560px) {
    .hint, .footer, .tpl-box .hint { display: none; }
    .btns .btn      { padding: 4px 8px; font-size: 11px; }
    .field-wrap     { min-height: 60px; }
    .tpl-box        { padding: 6px 8px; }
    .hdr h1         { font-size: 15px; }
    .icon-btn       { width: 30px; height: 30px; font-size: 14px; }
  }

  /* ── Compact controls v2 ── */
  .hdr              { margin: 0 0 3px; }
  .hdr h1           { font-size: 14px; line-height: 1.2; }
  .hdr-btns         { gap: 3px; }
  .hdr-btns .icon-btn { width: 26px; height: 26px; font-size: 12px; border-radius: 6px; }

  .hint             { font-size: 10px; margin: 0 0 2px; line-height: 1.25; }

  .label            { margin: 1px 0 1px; font-size: 11px; }

  .btns             { margin: 2px 0; gap: 3px; }
  .btns .btn        { padding: 2px 7px; font-size: 11px; line-height: 1.25; border-radius: 5px; }
  .btns .btn:hover  { transform: none; }

  .field-wrap       { min-height: 55px; margin-bottom: 3px; }
  .field-wrap .field { padding: 6px 10px; font-size: 13px; line-height: 1.45; }

  .footer           { margin-top: 2px; font-size: 10px; }

  .tpl-box          { margin-top: 3px; padding: 3px 8px 4px; }
  .tpl-box h3       { font-size: 11px; margin: 0 0 2px; }
  .tpl-box .hint    { font-size: 10px; line-height: 1.25; }
  .tpl-status       { font-size: 10px; margin-bottom: 2px; }

  @media (max-height: 680px) {
    .hint, .tpl-box .hint { display: none; }
  }

  /* ── Compact v3: toggle-шаблон + адаптивные кнопки ── */
  .btns               { gap: 3px; margin: 2px 0; align-items: stretch; }
  .btns > *           { flex: 0 1 auto; min-height: 22px; }
  .btns .btn          { padding: 2px 7px; font-size: 11px; line-height: 1.2;
                        border-radius: 5px; white-space: nowrap;
                        overflow: hidden; text-overflow: ellipsis;
                        display: inline-flex; align-items: center; justify-content: center; }
  .btns label         { padding: 2px 6px; font-size: 11px; }

  .tpl-box            { display: none; }
  .tpl-box.open       { display: block; padding: 4px 8px 5px; margin-top: 4px; }
  .tpl-box.open h3    { font-size: 11px; margin: 0 0 2px; }
  .tpl-box.open .hint { font-size: 10px; margin-top: 2px; }

  /* ── Compact v4: узкое окно → кнопки в одну строку ── */
  @media (max-width: 640px) {
    .btns            { gap: 2px; }
    .btns .btn       { padding: 2px 5px; font-size: 10px; }
    .btns .icon-btn,
    .btns .btn:hover { transform: none; }
  }
  @media (max-width: 520px) {
    .btns .btn       { padding: 2px 4px; font-size: 9.5px; letter-spacing: -.1px; }
  }

  /* ── Compact v5: пикер — плотнее сетка и шрифт ── */
  .picker {
    grid-template-columns: repeat(auto-fill, minmax(24px, 1fr));
    gap: 2px;
    padding: 4px;
  }
  .picker button {
    font-size: 13px;
    border-radius: 4px;
    border-width: 1px;
  }
  .picker-tabs button { padding: 2px 8px; font-size: 11px; }
  @media (max-width: 520px) {
    .picker { grid-template-columns: repeat(auto-fill, minmax(22px, 1fr)); }
    .picker button { font-size: 12px; }
  }
</style></head><body>
<div class="hdr">
  <h1>✍ Редактор текста для ВК</h1>
  <div class="hdr-btns">
    <button class="icon-btn" id="btn-theme" title="Переключить тему">🌙</button>
    <button class="icon-btn" id="btn-bg" title="Фон редактора">🖼</button>
    <button class="icon-btn" id="btn-tpl" title="Шаблон оформления">📿</button>
  </div>
</div>
<div class="bg-panel" id="bg-panel" style="display:none">
  <div class="bg-panel-title">🖼 Фон редактора</div>
  <div class="bg-preview" id="bg-preview">Фон не выбран</div>
  <div class="btns" style="margin:0">
    <button class="btn" id="bg-upload">⬆ Загрузить</button>
    <button class="btn" id="bg-reset">↺ Убрать фон</button>
    <button class="btn" id="bg-close">✕ Закрыть</button>
  </div>
</div>
<div class="hint">Вставь текст → нажми кнопку → результат ниже → «Скопировать».</div>
<label class="label">Введи или вставь текст:</label>
<div class="field-wrap">
  <textarea id="src" class="field" rows="7" placeholder="Вставь сюда текст поста..."></textarea>
  <div class="field-actions">
    <button type="button" class="icon-btn-sm" data-act="strip-emoji" id="btn-strip-emoji" title="Убрать эмодзи">🚫</button>
    <button type="button" class="icon-btn-sm" data-act="strip-links" id="btn-strip-links" title="Убрать ссылки">🔗</button>
    <button type="button" class="icon-btn-sm" data-act="copy-src" title="Копировать">📋</button>
    <button type="button" class="icon-btn-sm" data-act="clear-src" title="Очистить">🗑</button>
  </div>
</div>
<div class="btns">
  <button class="btn" data-act="format">🎨 Оформить для ВК</button>
  <button class="btn slav-a" data-act="slav-a">🕯 Дореформенный</button>
  <button class="btn slav-b" data-act="slav-b">🏛 Древній</button>
  <button class="btn slav-c" data-act="slav-c">✨ AI старослав</button>
  <button class="btn" data-act="emoji">😊 Эмодзи</button>
  <button class="btn" data-act="symbols">✳ Символы</button>
</div>
<div id="picker" style="display:none"><div class="picker-tabs" id="tabs"></div><div class="picker" id="grid"></div></div>
<label class="label">Готовый текст:</label>
<div class="field-wrap">
  <textarea id="dst" class="field" rows="10" placeholder="Здесь появится результат..."></textarea>
  <div class="field-actions">
    <button type="button" class="icon-btn-sm" data-act="copy-dst" title="Копировать">📋</button>
    <button type="button" class="icon-btn-sm" data-act="clear-dst" title="Очистить">🗑</button>
  </div>
</div>
<div class="btns">
  
  <button class="btn" id="btn-variant">🔄 Вид: 🔥 Классика</button>
  <button class="btn" data-act="to-src">↺ Из результата → во ввод</button>
  
</div>
<div class="footer"><span>Пост сохраняй в PagesCMS отдельно.</span><span id="counter">0 симв.</span></div>
<div class="tpl-box">
  <h3 style="margin-top:0">📿 Шаблон оформления</h3>
  <div class="tpl-status">Текущий: <span id="tpl-status">не задан</span></div>
  <div class="btns" style="margin:8px 0">
    <button class="btn" data-act="tpl-save">🔒 Запомнить из верхнего поля</button>
    <button class="btn" data-act="tpl-apply">📿 По шаблону</button>
    <button class="btn" data-act="tpl-clear">✖ Забыть шаблон</button>
    <label style="display:inline-flex;align-items:center;gap:6px;padding:6px 10px;font-size:12px;opacity:.85;user-select:none;cursor:pointer">
      <input type="checkbox" id="confirm-clear" style="margin:0;cursor:pointer">Подтверждать очистку
    </label>
  </div>
  <div class="hint" style="margin:0"><b>Как:</b> вставь <b>уже оформленный</b> пост в верхнее поле → «🔒 Запомнить». Поле очистится. Потом вставь <b>сырой</b> текст → «📿 По шаблону» → результат внизу.</div>
</div>
<div class="toast" id="toast"></div>
<script>
(function(){
  const H = window.opener && window.opener._vpHelp;
  if (!H) { document.body.innerHTML = '<p style="color:#c33;padding:20px;font:16px sans-serif">Ошибка: нет доступа к родителю. Открой редактор с главной страницы.</p>'; return; }
  const $ = id => document.getElementById(id);
  const src=$('src'), dst=$('dst'), picker=$('picker'), tabs=$('tabs'), grid=$('grid');
  let _undo = null;
  function _syncStripButtons() {
    const be = document.getElementById('btn-strip-emoji');
    const bl = document.getElementById('btn-strip-links');
    const ue = _undo && _undo.kind === 'emoji';
    const ul = _undo && _undo.kind === 'links';
    if (be) { be.textContent = ue ? '↩️' : '🚫'; be.title = ue ? 'Вернуть эмодзи' : 'Убрать эмодзи'; }
    if (bl) { bl.textContent = ul ? '↩️' : '🔗'; bl.title = ul ? 'Вернуть ссылки' : 'Убрать ссылки'; }
  }
  src.addEventListener('input', () => { if (_undo) { _undo = null; _syncStripButtons(); } });

  // — vp: последнее активное поле (#src/#dst) для вставки из палитры
  let _vpLastField = src;
  [src, dst].forEach(el => {
    if (!el) return;
    el.addEventListener('focus', () => { _vpLastField = el; });
    el.addEventListener('click', () => { _vpLastField = el; });
  });
  const toastEl=$('toast'), counter=$('counter');
  function toast(m,k){ toastEl.textContent=m; toastEl.className='toast show'+(k?' '+k:''); clearTimeout(toastEl._to); toastEl._to=setTimeout(()=>{toastEl.className='toast'},2200); }
  function insertAtCursor(ta,text){ const s=ta.selectionStart,e=ta.selectionEnd; ta.value=ta.value.slice(0,s)+text+ta.value.slice(e); ta.selectionStart=ta.selectionEnd=s+text.length; ta.focus(); }
  function updateCounter(){ counter.textContent=(dst.value.length||0)+' симв.'; }
  dst.addEventListener('input', updateCounter);

  // ============ ТЕМА ============
  function getTheme(){ try { const s=localStorage.getItem('vp-ed-theme'); if (s) return s; const m=JSON.parse(localStorage.getItem('vp-prefs')||'{}'); return m.theme||'light'; } catch(e) { return 'light'; } }
  function setTheme(t){ try { localStorage.setItem('vp-ed-theme', t); } catch(e) {} applyTheme(); }
  function applyTheme(){ const t=getTheme(); document.documentElement.dataset.theme=t; const b=$('btn-theme'); if (b) b.textContent = t==='dark'?'☀️':'🌙'; }

  // ============ ФОН ============
  function getBg(){ try { const s=localStorage.getItem('vp-ed-bg'); if (s!==null) return s; const m=JSON.parse(localStorage.getItem('vp-prefs')||'{}'); return m.background||''; } catch(e) { return ''; } }
  function setBg(url){ try { localStorage.setItem('vp-ed-bg', url || ''); } catch(e) {} applyBg(); }
  function applyBg(){ const bg=getBg(); if (bg){ document.body.style.setProperty('--bg-image', 'url("'+bg+'")'); document.body.classList.add('has-bg'); } else { document.body.style.setProperty('--bg-image', 'none'); document.body.classList.remove('has-bg'); } renderBgPreview(); }
  function renderBgPreview(){ const el=$('bg-preview'); if (!el) return; const bg=getBg(); if (bg){ el.style.backgroundImage='url("'+bg+'")'; el.textContent=''; } else { el.style.backgroundImage=''; el.textContent='Фон не выбран'; } }

  // ============ РАЗМЕР ============
  function savePos(){
    try {
      const d = { w: Math.round(window.outerWidth || 1000), h: Math.round(window.outerHeight || 900) };
      const sx = (typeof window.screenX === 'number') ? window.screenX : window.screenLeft;
      const sy = (typeof window.screenY === 'number') ? window.screenY : window.screenTop;
      if (typeof sx === 'number' && isFinite(sx)) d.x = Math.round(sx);
      if (typeof sy === 'number' && isFinite(sy)) d.y = Math.round(sy);
      localStorage.setItem('vp-ed-size', JSON.stringify(d));
    } catch(e) {}
  }
  let _szT;
  window.addEventListener('resize', () => { clearTimeout(_szT); _szT = setTimeout(savePos, 350); });
  window.addEventListener('beforeunload', savePos);
  window.addEventListener('pagehide', savePos);

  // ============ КНОПКИ ШАПКИ ============
  $('btn-theme').addEventListener('click', () => setTheme(getTheme()==='dark'?'light':'dark'));
  $('btn-bg').addEventListener('click', () => { const p=$('bg-panel'); p.style.display = p.style.display==='none'?'':'none'; });
  $('bg-close').addEventListener('click', () => { $('bg-panel').style.display='none'; });
  $('bg-upload').addEventListener('click', () => {
    const inp=document.createElement('input'); inp.type='file'; inp.accept='image/*';
    inp.addEventListener('change', () => {
      const f=inp.files[0]; if (!f) return;
      if (f.size>4*1024*1024){ alert('Файл больше 4 МБ'); return; }
      const r=new FileReader();
      r.onload=()=>{ setBg(r.result); toast('Фон установлен','ok'); };
      r.readAsDataURL(f);
    });
    inp.click();
  });
  $('bg-reset').addEventListener('click', () => { setBg(''); toast('Фон убран','ok'); });

  // ============ ШАБЛОН ============
  function refreshTpl(){ const tpl=H.getTemplate(); const el=$('tpl-status'); if (!tpl){ el.textContent='не задан'; return; } el.innerHTML = tpl.pattern.map(p=>'<span class="tpl-pattern">'+p+'</span>').join(' '); }
  refreshTpl();

  // гарантированно скрыть палитру при открытии попапа (2-й слой — CSS #picker:not([data-vp-open]))
  try { if (picker) { picker.removeAttribute('data-vp-open'); picker.style.display = 'none'; } } catch(e){}

  // ============ ОСНОВНЫЕ КНОПКИ ============
  const _cc = document.getElementById('confirm-clear');
if (_cc) {
  _cc.checked = localStorage.getItem('vk_confirm_clear') !== '0';
  _cc.addEventListener('change', () => localStorage.setItem('vk_confirm_clear', _cc.checked ? '1' : '0'));
}
  // ═══════════ ПРЕСЕТЫ ВИДА (🔄 Вид) ═══════════
  const FORMAT_PRESETS = [
    {id:'classic', icon:'🔥',   name:'Классика',     opts:{smartHeaders:true,  smartEmoji:true,  emojiRepeat:1}},
    {id:'triple',  icon:'🔥✨', name:'Эмодзи ×3',    opts:{smartHeaders:true,  smartEmoji:true,  emojiRepeat:3}},
    {id:'minimal', icon:'🔥·',  name:'Минимум',       opts:{smartHeaders:true,  smartEmoji:false, emojiRepeat:1}},
    {id:'emoji',   icon:'😊',   name:'Только эмодзи', opts:{smartHeaders:false, smartEmoji:true,  emojiRepeat:1}},
    {id:'plain',   icon:'📄',   name:'Без обработки', opts:{smartHeaders:false, smartEmoji:false, emojiRepeat:1}},
  ];
  let _presetIdx = 0;
  try { const s = parseInt(localStorage.getItem('vp-format-preset')||'0',10); if (s >= 0 && s < FORMAT_PRESETS.length) _presetIdx = s; } catch(e){}
  function _setVariantBtnLabel(){ const btn = document.getElementById('btn-variant'); if (!btn) return; const p = FORMAT_PRESETS[_presetIdx]; btn.textContent = '🔄 Вид: ' + p.icon + ' ' + p.name; }
  function applyCurrentPreset(){ if (!src.value.trim()) { toast('Введи текст','err'); return; } const p = FORMAT_PRESETS[_presetIdx]; dst.value = H.formatForVK(src.value, p.opts); updateCounter(); _setVariantBtnLabel(); toast('Вид: ' + p.name, 'ok'); }
  function cyclePreset(){ _presetIdx = (_presetIdx + 1) % FORMAT_PRESETS.length; try { localStorage.setItem('vp-format-preset', String(_presetIdx)); } catch(e){} applyCurrentPreset(); }
  (function initVariantBtn(){ const btn = document.getElementById('btn-variant'); if (!btn) { console.warn('[variant] кнопка не найдена'); return; } btn.addEventListener('click', cyclePreset); _setVariantBtnLabel(); })();

document.querySelectorAll('[data-act]').forEach(b => {
    b.addEventListener('click', async () => {
      const act = b.dataset.act;
      try {
        if (act === 'format') { applyCurrentPreset(); }
        else if (act === 'slav-a') { if (!src.value.trim()){toast('Введи текст','err');return;} dst.value=H.slavicA(src.value); updateCounter(); toast('А','ok'); }
        else if (act === 'slav-b') { if (!src.value.trim()){toast('Введи текст','err');return;} dst.value=H.slavicB(src.value); updateCounter(); toast('Б','ok'); }
        else if (act === 'slav-c') {
          if (!src.value.trim()){toast('Введи текст','err');return;}
          if (!H.getAiEndpoint()) {
            const url = prompt('URL AI-сервера (Cloudflare Worker).\\nПример: https://vk-slavic.you.workers.dev/slavic\\n\\nПусто — отмена.');
            if (!url) return; H.setAiEndpoint(url.trim()); toast('URL AI сохранён','ok');
          }
          b.disabled=true; const old=b.textContent; b.textContent='✨ Думаю...';
          try { dst.value=await H.slavicC(src.value); updateCounter(); toast('В','ok'); }
          catch(e) { toast('AI error: '+e.message,'err'); }
          finally { b.disabled=false; b.textContent=old; }
        }
        else if (act === 'strip-emoji') {
          if (!src.value.trim()) { toast('Введи текст','err'); return; }
          if (_undo && _undo.kind === 'emoji' && src.value === _undo.after) {
            src.value = _undo.before; _undo = null; _syncStripButtons();
            toast('Эмодзи возвращены','ok'); return;
          }
          const _r = H.stripEmoji(src.value);
          if (_r.count === 0) { toast('Эмодзи не найдены',''); return; }
          _undo = { kind: 'emoji', before: src.value, after: _r.text };
          src.value = _r.text; _syncStripButtons();
          toast('Убрано эмодзи: ' + _r.count, 'ok');
        }
        else if (act === 'strip-links') {
          if (!src.value.trim()) { toast('Введи текст','err'); return; }
          if (_undo && _undo.kind === 'links' && src.value === _undo.after) {
            src.value = _undo.before; _undo = null; _syncStripButtons();
            toast('Ссылки возвращены','ok'); return;
          }
          const _r = H.stripLinks(src.value);
          if (_r.count === 0) { toast('Ссылки не найдены',''); return; }
          _undo = { kind: 'links', before: src.value, after: _r.text };
          src.value = _r.text; _syncStripButtons();
          toast('Убрано ссылок: ' + _r.count, 'ok');
        }
        else if (act === 'emoji' || act === 'symbols') { window._vpPickerMode = act; const c = act==='emoji'?H.EMOJI:H.SYMBOLS; picker.setAttribute('data-vp-open','1'); picker.style.display=''; renderPickerTabs(c); }
        else if (act === 'copy-src' || act === 'copy-dst') {
          const ta = act === 'copy-src' ? src : dst;
          if (!ta.value) { toast('Пусто','err'); return; }
          let ok = false, _cerr = '';
          // 1) execCommand ПЕРВЫМ — надёжнее в about:blank-попапе
          try {
            const _t = document.createElement('textarea');
            _t.value = ta.value;
            _t.style.position = 'fixed'; _t.style.opacity = '0'; _t.style.left = '-9999px';
            document.body.appendChild(_t); _t.focus(); _t.select();
            ok = document.execCommand('copy');
            document.body.removeChild(_t);
            if (!ok) _cerr += 'execCommand=false';
          } catch(e) { _cerr += 'execCommand:' + (e && e.message || e); }
          // 2) нативный API
          if (!ok) {
            try {
              if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(ta.value); ok = true;
              } else { _cerr += ' | no clipboard'; }
            } catch(e) { _cerr += ' | clipboard:' + (e && e.message || e); }
          }
          // 3) через opener (последний шанс)
          if (!ok && typeof H !== 'undefined' && H && typeof H.copyText === 'function') {
            try { ok = await H.copyText(ta.value); } catch(e) { _cerr += ' | opener:' + (e && e.message || e); }
          }
          if (window.console) console.log('[copy]', act, 'ok=', ok, 'err=', _cerr);
          toast(ok ? '✓ Скопировано' : ('❌ ' + (_cerr || 'H false').slice(-120)), ok ? 'ok' : 'err');
        }
        else if (act === 'clear-src' || act === 'clear-dst') {
          const _w = b && b.closest ? b.closest('.field-wrap') : null;
          const _dt = _w && _w.querySelector('textarea');
          const target = _dt || document.getElementById(act === 'clear-src' ? 'src' : 'dst') ||
                         (act === 'clear-src' ? src : dst);
          if (!target) { toast('Поле не найдено','err'); return; }
          if (!target.value) { toast('Пусто','err'); return; }
          const _chk = document.getElementById('confirm-clear');
          if (!_chk || _chk.checked) {
            const _label = act === 'clear-src' ? 'ВЕРХНЕЕ' : 'НИЖНЕЕ';
            if (!confirm('Очистить ' + _label + ' поле?')) return;
          }
          target.value = '';
          try { if (act === 'clear-src') { picker.style.display = 'none'; target.focus(); } else { updateCounter(); } } catch(e){}
          toast(act === 'clear-src' ? 'Верхнее очищено' : 'Нижнее очищено', 'ok');
        }
        else if (act === 'to-src') { if (!dst.value.trim()){toast('Сначала оформи','err');return;} src.value=dst.value; dst.value=''; updateCounter(); }
        
        else if (act === 'tpl-save') {
          if (!src.value.trim()){toast('Вставь оформленный пример','err');return;}
          const pattern = H.captureTemplate(src.value);
          H.setTemplate({ pattern, example: src.value });
          src.value=''; dst.value=''; updateCounter(); refreshTpl();
          toast('✓ Шаблон: ' + pattern.join(' → '),'ok');
        }
        else if (act === 'tpl-apply') {
          const tpl=H.getTemplate(); if (!tpl){toast('Шаблон не задан','err');return;}
          if (!src.value.trim()){toast('Введи текст','err');return;}
          dst.value = H.applyTemplate(src.value, tpl.pattern); updateCounter(); toast('По шаблону','ok');
        }
        else if (act === 'tpl-clear') { H.clearTemplate(); refreshTpl(); toast('Шаблон забыт','ok'); }
      } catch(e) { toast('Ошибка: '+e.message,'err'); console.error(e); }
    });
  });

  function _vpRecentKey(){ return 'vp-ed-recent-' + (window._vpPickerMode === 'symbols' ? 'symbols' : 'emoji'); }
  function getRecent(){ try { return JSON.parse(localStorage.getItem(_vpRecentKey()) || '[]'); } catch(e){ return []; } }
  function trackRecent(ch){
    try {
      const cur = getRecent();
      const next = [ch, ...cur.filter(x => x !== ch)].slice(0, 24);
      localStorage.setItem(_vpRecentKey(), JSON.stringify(next));
    } catch(e){ console.warn('[vp] recent:', e); }
  }
  function renderPickerTabs(catalog){ tabs.innerHTML=''; grid.innerHTML='';
    // ★ Часто — всегда первая и активная
    const rb = document.createElement('button'); rb.type='button'; rb.textContent='★ Часто';
    rb.addEventListener('click', ()=>{ tabs.querySelectorAll('button').forEach(x=>x.classList.remove('active')); rb.classList.add('active'); renderPickerGrid(getRecent()); });
    tabs.appendChild(rb); rb.classList.add('active'); renderPickerGrid(getRecent());
    // Остальные категории — без auto-active
    Object.keys(catalog).forEach((cat)=>{
      const b=document.createElement('button'); b.type='button'; b.textContent=cat;
      b.addEventListener('click', ()=>{ tabs.querySelectorAll('button').forEach(x=>x.classList.remove('active')); b.classList.add('active'); renderPickerGrid(catalog[cat]); });
      tabs.appendChild(b);
    });
  }
  function renderPickerGrid(chars){ grid.innerHTML='';
    if (!chars || !chars.length) {
      const d = document.createElement('div'); d.className = 'picker-empty';
      d.textContent = 'Кликайте на эмодзи/символы — они появятся здесь';
      grid.appendChild(d); return;
    }
    chars.forEach(ch=>{ const b=document.createElement('button'); b.type='button'; b.textContent=ch; b.addEventListener('mousedown', e=>e.preventDefault()); b.addEventListener('click', ()=>{ const _tgt = _vpLastField || src; insertAtCursor(_tgt,ch); trackRecent(ch); toast('Вставлено: '+ch); }); grid.appendChild(b); });
  }

  applyTheme(); applyBg();

  // Toggle-close пикера по повторному клику 😊 / ✳
  try {
    const _pk = document.getElementById('picker');
    if (_pk) {
      document.addEventListener('click', function (e) {
        const _t = e.target;
        if (!_t || !_t.closest) return;
        const _btn = _t.closest('[data-act="emoji"], [data-act="symbols"]');
        if (!_btn) return;
        const _want = _btn.dataset.act;
        const _open = getComputedStyle(_pk).display !== 'none';
        if (_open && window._vpPickerMode === _want) {
          _pk.style.display = 'none';
          window._vpPickerMode = null;
          e.stopImmediatePropagation();
          e.preventDefault();
          console.log('[vp] picker closed via toggle');
        } else {
          window._vpPickerMode = _want;
        }
      }, true);
    }
  } catch (e) { console.warn('[vp] picker toggle:', e); }

  // Toggle блока шаблона
  try {
    const _bt = document.getElementById('btn-tpl');
    const _tb = document.querySelector('.tpl-box');
    if (_bt && _tb) {
      if (localStorage.getItem('vp_tpl_open') === '1') _tb.classList.add('open');
      _bt.addEventListener('click', function () {
        _tb.classList.toggle('open');
        localStorage.setItem('vp_tpl_open', _tb.classList.contains('open') ? '1' : '0');
      });
    }
  } catch (e) { console.warn('[vp] tpl-toggle:', e); }

  src.focus();
  try { document.documentElement.setAttribute('data-vp-editor-ready','1'); } catch(e){}
})();
<\/script></body></html>`;

    // Bulletproof: HTML в LS + статический editor.html (переживает ⟳ после reload главной)
    (function _launch() {
      try { localStorage.setItem('vp_editor_html', html); }
      catch(e) { console.warn('[vp] LS save failed:', e); }
      if (window._vpEditorBlobPrev) {
        try { URL.revokeObjectURL(window._vpEditorBlobPrev); } catch(e){}
        delete window._vpEditorBlobPrev;
      }
      const _editorUrl = new URL('editor.html', window.location.href).href;
      setTimeout(() => {
        try {
          if (!w || w.closed || !w.location) return;
          w.location.replace(_editorUrl);
        } catch (e) {
          console.error('[vp] editor nav failed, fallback to document.write:', e);
          try { w.document.open(); w.document.write(html); w.document.close(); }
          catch (e2) { console.error('[vp] fallback failed:', e2); }
        }
      }, 0);
    })();
  }

  // ---------- главное окно ----------
  function buildUI() {
    const h1 = document.querySelector('h1');
    if (!h1 || document.getElementById('vp-topbar')) return;
    const bar = document.createElement('div');
    bar.id = 'vp-topbar'; bar.className = 'vp-topbar';
    bar.innerHTML = `
      <input type="search" id="vp-search-input" class="vp-search-input" placeholder="🔍 Найти праздник...">
      <span id="vp-search-count" class="vp-search-count"></span>
      <button id="vp-editor-btn" class="vp-icon-btn" title="✍ Редактор (отдельное окно)">✍</button>
      <button id="vp-settings-btn" class="vp-icon-btn" title="Настройки">⚙️</button>`;
    h1.insertAdjacentElement('afterend', bar);
    const panel = document.createElement('div');
    panel.id = 'vp-settings-panel'; panel.className = 'vp-settings-panel'; panel.style.display = 'none';
    panel.innerHTML = `<h3>⚙️ Настройки вида</h3>
      <label class="vp-row"><input type="checkbox" id="vp-night"> 🌙 Ночной режим</label>
      <div class="vp-row"><b>🖼 Фон страницы:</b></div><div class="vp-bg-grid" id="vp-bg-grid"></div>
      <div class="vp-row"><button id="vp-bg-upload" class="vp-btn">⬆ Загрузить фон</button><button id="vp-bg-reset" class="vp-btn">↺ Убрать</button></div>`;
    bar.insertAdjacentElement('afterend', panel);

    document.getElementById('vp-search-input').addEventListener('input', e => doFilter(e.target.value));
    document.getElementById('vp-settings-btn').addEventListener('click', () => {
      panel.style.display = panel.style.display !== 'none' ? 'none' : '';
    });
    document.getElementById('vp-editor-btn').addEventListener('click', openEditorWindow);
    const night = document.getElementById('vp-night');
    night.checked = prefs.theme === 'dark';
    night.addEventListener('change', () => { prefs.theme = night.checked ? 'dark' : 'light'; save(); applyTheme(); });
    document.getElementById('vp-bg-upload').addEventListener('click', () => {
      const inp = document.createElement('input'); inp.type='file'; inp.accept='image/*';
      inp.addEventListener('change', () => {
        const f = inp.files[0]; if (!f) return;
        if (f.size > 4*1024*1024) { alert('Файл больше 4 МБ'); return; }
        const r = new FileReader();
        r.onload = () => { prefs.userBackgrounds = prefs.userBackgrounds || {}; prefs.userBackgrounds[r.result]={name:f.name,added:Date.now()}; prefs.background=r.result; save(); applyBackground(); renderBgGrid(); };
        r.readAsDataURL(f);
      });
      inp.click();
    });
    document.getElementById('vp-bg-reset').addEventListener('click', () => { delete prefs.background; save(); applyBackground(); renderBgGrid(); });
    renderBgGrid();
  }
  function renderBgGrid() {
    const grid = document.getElementById('vp-bg-grid'); if (!grid) return;
    grid.innerHTML = '';
    const none = document.createElement('button');
    none.className='vp-bg-tile vp-bg-none'; none.textContent='∅';
    if (!prefs.background) none.classList.add('active');
    none.addEventListener('click',()=>{ delete prefs.background; save(); applyBackground(); renderBgGrid(); });
    grid.appendChild(none);
    collectBackgrounds().forEach(src => {
      const b = document.createElement('button');
      b.className='vp-bg-tile'; b.style.backgroundImage=`url('${src}')`;
      if (prefs.background === src) b.classList.add('active');
      b.addEventListener('click',()=>{ prefs.background=src; save(); applyBackground(); renderBgGrid(); });
      grid.appendChild(b);
    });
  }

  window._vpHelp = {
    slavicA, slavicB, slavicC, stripEmoji, stripLinks, formatForVK,
    captureTemplate, applyTemplate, getTemplate, setTemplate, clearTemplate,
    getAiEndpoint, setAiEndpoint, EMOJI, SYMBOLS, copyText
  };

  applyTheme(); applyBackground();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => { buildUI(); doFilter(''); });
  else { buildUI(); doFilter(''); }
})();
/* ═══════════ ПЛАВАЮЩАЯ КНОПКА «НАВЕРХ» (квадрат, тема) ═══════════ */
/* Появляется при прокрутке > 300px. Квадрат, цвет подстраивается под тему. */
(function _vpInitBackToTop(){
  if (typeof window === 'undefined') return undefined;
  if (window._vpBackToTopLoaded) return undefined;
  window._vpBackToTopLoaded = true;

  function isDark(){
    try {
      var dt = document.documentElement.dataset.theme ||
               (document.body && document.body.dataset.theme);
      if (dt === 'dark') return true;
      if (dt === 'light') return false;
    } catch(e){}
    try {
      var bg = getComputedStyle(document.body).backgroundColor;
      var m = bg.match(/[\d.]+/g);
      if (m && m.length >= 3 && !(m.length >= 4 && parseFloat(m[3]) === 0)) {
        var lum = 0.2126*(+m[0]) + 0.7152*(+m[1]) + 0.0722*(+m[2]);
        return lum < 128;
      }
    } catch(e){}
    return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  }

  function paint(btn){
    var dark = isDark();
    if (dark) {
      btn.style.background = '#374151';
      btn.style.color = '#f9fafb';
      btn.style.border = '1px solid rgba(255,255,255,.18)';
      btn.style.boxShadow = '0 4px 14px rgba(0,0,0,.55)';
    } else {
      btn.style.background = '#2563eb';
      btn.style.color = '#ffffff';
      btn.style.border = '1px solid rgba(0,0,0,.06)';
      btn.style.boxShadow = '0 4px 14px rgba(37,99,235,.40)';
    }
  }

  function makeButton(){
    if (!document.body) return;
    if (document.getElementById('vp-back-to-top')) return;
    var btn = document.createElement('button');
    btn.id = 'vp-back-to-top';
    btn.type = 'button';
    btn.title = 'Наверх';
    btn.setAttribute('aria-label', 'К началу страницы');
    btn.textContent = '↑';
    btn.style.cssText = 'position:fixed;bottom:24px;right:24px;width:48px;height:48px;border-radius:10px;font-size:22px;line-height:1;padding:0;cursor:pointer;opacity:0;visibility:hidden;transition:opacity .2s,visibility .2s,background .15s,transform .15s,box-shadow .15s;z-index:9999;font-family:system-ui,-apple-system,sans-serif;display:flex;align-items:center;justify-content:center;font-weight:700;';
    paint(btn);

    btn.addEventListener('mouseenter', function(){ btn.style.transform = 'scale(1.06)'; });
    btn.addEventListener('mouseleave', function(){ btn.style.transform = 'scale(1)'; });
    btn.addEventListener('click', function(){ window.scrollTo({ top: 0, behavior: 'smooth' }); });
    document.body.appendChild(btn);

    function updateVisibility(){
      var show = (window.scrollY || window.pageYOffset || 0) > 300;
      btn.style.opacity = show ? '1' : '0';
      btn.style.visibility = show ? 'visible' : 'hidden';
    }
    window.addEventListener('scroll', updateVisibility, {passive:true});
    updateVisibility();

    try {
      var mo = new MutationObserver(function(){ paint(btn); });
      mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class'] });
      if (document.body) mo.observe(document.body, { attributes: true, attributeFilter: ['data-theme', 'class'] });
    } catch(e){}
    try {
      var mq = window.matchMedia('(prefers-color-scheme: dark)');
      if (mq.addEventListener) mq.addEventListener('change', function(){ paint(btn); });
    } catch(e){}
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', makeButton);
  else makeButton();
})();

