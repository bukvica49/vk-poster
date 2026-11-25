#!/usr/bin/env python3
# fill_vk_photo.py — матчинг вышедших постов → карточки праздников, автозаполнение vk_photo.
# Запуск: python3 fill_vk_photo.py --dry-run   (показать пары, ничего не писать)
#         python3 fill_vk_photo.py             (вписать ID в карточки)
import json, re, sys, urllib.request, urllib.parse, pathlib

HERE = pathlib.Path(__file__).parent
cfg = json.load(open(HERE / "config.main.json", encoding="utf-8"))
tok = cfg.get("service_token") or cfg.get("group_token") or cfg.get("token")
GROUP = -200796423
DRY = "--dry-run" in sys.argv

def call(method, **params):
    q = urllib.parse.urlencode({**params, "access_token": tok, "v": "5.199"})
    return json.loads(urllib.request.urlopen(
        f"https://api.vk.com/method/{method}", q.encode(), timeout=15).read())

# 1) посты со стены: текст + первое фото
posts = []
offset = 0
for _ in range(40):
    r = call("wall.get", owner_id=GROUP, count=100, offset=offset)
    if "error" in r:
        print("wall.get ERROR:", r["error"]["error_code"]); break
    items = r["response"]["items"]
    if not items:
        break
    for it in items:
        ph_id = ""
        for att in (it.get("attachments") or []):
            if att.get("type") == "photo":
                ph = att["photo"]
                ph_id = f"photo-{abs(ph['owner_id'])}_{ph['id']}"
                break
        posts.append((it.get("text", ""), ph_id))
    offset += len(items)
print(f"постов со стены: {len(posts)}")

def norm(val):
    """Из значения vk_photo достаём канонический ID (или ''), если это URL/ID."""
    if not val:
        return ""
    m = re.search(r"photo-?\d+_\d+", urllib.parse.unquote(str(val)))
    return m.group(0) if m else ""

def find_post(title):
    t = title.lower()
    for text, ph_id in posts:
        if ph_id and t in text.lower():
            return ph_id
    return ""

# 2) карточки
matched, missed, skipped = 0, 0, 0
for jf in sorted((HERE / "content" / "holidays").glob("*.json")):
    d = json.loads(jf.read_text(encoding="utf-8"))
    title = d.get("text", "")
    if d.get("daily"):
        continue
    cur = norm(d.get("vk_photo", ""))
    if cur and cur in {p for _, p in posts}:
        skipped += 1
        print(f"  ✓ уже вписан постовый ID: {title} ({cur})")
        continue
    pid = find_post(title)
    if pid:
        matched += 1
        print(f"  → {title}: {cur or '—'}  ⇒  {pid}")
        if not DRY:
            d["vk_photo"] = pid
            jf.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        missed += 1
        print(f"  ? пост не найден: {title}")

print(f"итого: вписано {matched}, уже было {skipped}, не найдено {missed}"
      + (" (dry-run)" if DRY else ""))
