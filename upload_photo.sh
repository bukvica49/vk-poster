#!/usr/bin/env bash
# upload_photo.sh — залить фото с компьютера в images/ и запушить в GitHub
#
# Использование:
#   ./upload_photo.sh <slug> <путь-к-файлу>
#
# Примеры:
#   ./upload_photo.sh chertog-shchuki ~/Downloads/щука.jpg
#   ./upload_photo.sh chertog-lebedy  ~/Pictures/лебедь.png

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ $# -ne 2 ]]; then
    echo "Использование: $0 <slug> <путь-к-файлу>"
    echo
    echo "Пример:  $0 chertog-shchuki ~/Downloads/щука.jpg"
    echo
    echo "Доступные чертоги:"
    for f in content/holidays/chertog-*.json; do
        slug=$(python3 -c "import json;print(json.load(open('$f'))['slug'])")
        img=$(python3 -c "import json;d=json.load(open('$f'));print(d.get('image','—'))")
        printf "  %-28s → %s\n" "$slug" "$img"
    done
    exit 1
fi

SLUG="$1"
SRC="$2"

[[ -f "$SRC" ]] || { echo "✗ Нет файла: $SRC"; exit 1; }
JSON="content/holidays/${SLUG}.json"
[[ -f "$JSON" ]] || { echo "✗ Нет JSON: $JSON (проверь slug)"; exit 1; }

IMG=$(python3 -c "import json;print(json.load(open('$JSON')).get('image',''))")
[[ -n "$IMG" ]] || { echo "✗ В $JSON нет поля 'image'"; exit 1; }

REL="${IMG#/}"           # /images/Щука.jpg → images/Щука.jpg
DEST="$(pwd)/$REL"
EXT_SRC="${SRC##*.}"
EXT_DST="${REL##*.}"

if [[ "${EXT_SRC,,}" != "${EXT_DST,,}" ]]; then
    echo "⚠ Расширение меняется: .$EXT_SRC → .$EXT_DST"
    read -rp "  Продолжить? [y/N] " ans
    [[ "$ans" =~ ^[Yy]$ ]] || { echo "Отменено"; exit 1; }
    if command -v convert >/dev/null 2>&1; then
        convert "$SRC" -quality 92 "$DEST"
    else
        cp "$SRC" "$DEST"
    fi
else
    cp "$SRC" "$DEST"
fi

echo "✓ $SRC → $REL ($(du -h "$DEST" | cut -f1))"

git add "$REL"
if git diff --cached --quiet; then
    echo "⚠ Файл не изменился (уже в git) — коммит не нужен"
else
    git commit -m "add photo for $SLUG ($(basename "$REL"))"
    git push origin main
    echo "✓ Запушено в GitHub"
fi

echo
echo "── Проверка:"
DATE=$(python3 -c "import json;print(json.load(open('$JSON'))['date'])")
YEAR=$(date +%Y)
for y in "$YEAR" $((YEAR+1)); do
    OUT=$(python3 poster.py --dry-run --date "$y-${DATE}" 2>/dev/null | grep "фото:" | tail -1 || true)
    [[ -n "$OUT" ]] && { echo "  $y-$DATE: $OUT"; break; }
done
