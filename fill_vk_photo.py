#!/usr/bin/env python3
# fill_vk_photo.py v2 — автозаполнение vk_photo:
#   праздники  — матч по полному названию карточки в тексте поста;
#   дни недели (daily) — матч по первому слову с нормализацией ятов
#   (Вторник ≈ Вторнiкъ, Тритейник ≈ Тритєїнiкъ).
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

# посты со стены: текст + первое фото (новые первыми)
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

YAT = {"ё": "е", "ѣ": "е", "ъ": "", "i": "и", "і": "и", "ї": "и", "є": "е",
       "ꙗ": "я", "ѧ": "я", "ѫ": "у", "ѵ": "в", "ѳ": "ф", "ꙋ": "у"}

def norm_txt(s):
    s = s.lower()
    for a, b in YAT.items():
        s = s.replace(a, b)
    return s

def first_word(s):
    m = re.search(r"[^\W\d_]+", s)  # первое слово, эмодзи и цифры пропускаем
    return norm_txt(m.group(0)) if m else ""

def norm(val):
    """Из значения vk_photo достаём канонический ID (или ''), если это URL/ID."""
    if not val:
        return ""
    m = re.search(r"photo-?\d+_\d+", urllib.parse.unquote(str(val)))
    return m.group(0) if m else ""

def find_post_full(title):
    t = norm_txt(title)
    for text, ph_id in posts:
        if ph_id and t in norm_txt(text):
            return ph_id
    return ""

def find_post_daily(title):
    w = first_word(title)
    if len(w) < 4:
        return ""
    stem = w[:4]  # основа дня: у всех дней недели первые 4 буквы уникальны
    for text, ph_id in posts:
        if not ph_id:
            continue
        pw = first_word(text)
        if len(pw) >= 4 and pw[:4] == stem:
            return ph_id
    return ""

matched, missed, skipped = 0, 0, 0
for jf in sorted((HERE / "content" / "holidays").glob("*.json")):
    d = json.loads(jf.read_text(encoding="utf-8"))
    title = d.get("text", "")
    daily = bool(d.get("daily"))
    cur = norm(d.get("vk_photo", ""))
    if cur and cur in {p for _, p in posts}:
        skipped += 1
        print(f"  ✓ уже вписан постовый ID: {title} ({cur})")
        continue
    pid = find_post_daily(title) if daily else find_post_full(title)
    tag = "день недели" if daily else "праздник"
    if pid:
        matched += 1
        print(f"  → [{tag}] {title}: {cur or '—'}  ⇒  {pid}")
        if not DRY:
            d["vk_photo"] = pid
            jf.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        missed += 1
        print(f"  ? [{tag}] пост не найден: {title}  ({jf.name})")

print(f"итого: вписано {matched}, уже было {skipped}, не найдено {missed}"
      + (" (dry-run)" if DRY else ""))
