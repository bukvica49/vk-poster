# editor.html — история: мерцание тултипов

## Итог

Виноват **`MutationObserver` в `vpfit v10`**, а не CSS. Убрали — мерцание прекратилось.

## Причина

Каждое появление `.vp-tip` (показ тултипа) — DOM-мутация. Observer ловил её,
вызывал `apply('mutation')` → forced reflow → перерисовка тултипа → новая
мутация → **закрытый loop**.

- На кнопках 28×28 — не видно (paint-тайлы кнопки и тултипа разные).
- На `label[data-vp-tip]` (14×14, галочка) и `.vp-splitter` (8px, средняя линия)
  paint-тайлы совпадают → визуальное мерцание.

**«Консоль DevTools открыт → мерцание слабее»** — это был верный сигнал:
проблема в reflow/perf, не в CSS.

## Что сделано

### V42 FINAL — `mo.disconnect()`
Observer больше не вызывается. `vpfit` работает через `init / resize / click / manual`
— этого достаточно. Правка в `web/editor.html`, строка `// mo.observe(...)`.

### V43 — `vp-zombie-tip-killer-v43`
После отключения MO побочный рефлоу, который мимоходом убирал `.vp-tip` при
`mouseleave`, исчез → тултип на `.vp-splitter` мог залипнуть. Теперь на
`mousemove / mouseout / scroll` вызывается `clearOrphans()`, которая удаляет
`.vp-tip`/`.bg-panel`, если ни один `[data-vp-tip]` не в `:hover`.

## Что НЕ работало (V34–V41, удалено)

Патчи пытались CSS-ом убрать мерцание. **Ни один не попал в DOM**:
скрипт вставлял перед первым `</head>`, а в `web/editor.html` их **три**
(в JS-строках). Вставки уходили в JS-код, браузер их не парсил,
`document.getElementById('vp-v40-probe')` → `null`.

**Урок**: если print говорит «✓ применён», а `getElementById` → `null`,
файл пишется не туда. Проверять обязательно:
- `md5sum web/editor.html _site/editor.html`
- `document.getElementById('vp-...')` в DevTools Console.

## Активные ID (не трогать)

| ID | Назначение |
|---|---|
| `vp-cm-css`, `vp-cm-fit-script` | CodeMirror |
| `vp-lock-body-css` | body без скролла |
| `vp-img-*` | диалог картинки |
| `vp-layout-stab-v21` | стабилизация layout |
| `vp-tip-v22` | базовый tooltip |
| `vp-tip-pe-v33` | pointer-events:none для ::after (безвредно) |
| `vp-help-x`, `vp-boot` | help-кнопка, bootstrap |
| `vp-zombie-tip-killer-v43` | **фикс V43** |

## Как безопасно вернуть MutationObserver (если когда-то понадобится)

Не возвращать `mo.observe` напрямую. Сначала — фильтр, игнорирующий мутации
тултипа:
Иначе тот же flicker вернётся.

## Ссылки

- `git log --grep="V42 FINAL"` — фикс observer'а
- `git log --grep="V43"` — фикс зомби-тултипа
- Файл: `web/editor.html`
