#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-}" in
  photo)
    NAME="${2:?usage: tools.sh photo <Name> <file>}"
    SRC="${3:?usage: tools.sh photo <Name> <file>}"
    [ -f "$SRC" ] || { echo "❌ нет файла: $SRC"; exit 1; }
    EXT="${SRC##*.}"
    DST="images/${NAME}.${EXT}"
    cp "$SRC" "$DST"
    for old in images/${NAME}.jpeg images/${NAME}.jpg images/${NAME}.png; do
      [ -f "$old" ] && [ "$old" != "$DST" ] && git rm -q "$old" || true
    done
    python3 - <<PYEOF
import json, re, pathlib
p = pathlib.Path("holidays.json")
d = json.loads(p.read_text(encoding="utf-8"))
n = len(re.findall(r'(?i)"?name"?\s*:\s*"[^"]*${NAME}[^"]*"', p.read_text(encoding="utf-8")))
p.write_text(p.read_text(encoding="utf-8").replace("/images/${NAME}.jpeg", "/images/${NAME}.${EXT}").replace("/images/${NAME}.jpg", "/images/${NAME}.${EXT}").replace("/images/${NAME}.png", "/images/${NAME}.${EXT}"), encoding="utf-8")
PYEOF
    python3 make_preview.py >/dev/null
    git add -A
    git commit -m "images: ${NAME} → ${EXT}" || echo "(no changes)"
    git push
    echo "✅ через 1-2 мин: https://bukvica49.github.io/vk-poster/"
    ;;
  attach)
    python3 attach_photo.py "${2:?post_id}" "${3:?file}"
    ;;
  rebuild)
    python3 make_preview.py
    git add _site
    git commit -m "rebuild site" || echo "(no changes)"
    git push
    ;;
  status)
    git status --short
    ;;
  *)
    echo "usage:"
    echo "  ./tools.sh photo <Name> <file>      # заменить фото + rebuild + push"
    echo "  ./tools.sh attach <post_id> <file>  # фото к VK-посту"
    echo "  ./tools.sh rebuild                  # пересобрать сайт + push"
    echo "  ./tools.sh status                   # что не закоммичено"
    ;;
esac
