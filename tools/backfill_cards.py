#!/usr/bin/env python3
"""backfill_cards.py v3 — стена + перепосты; дата из шапки; дозаполнение text_md."""
import json, re, time, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import requests
import slavic_calendar as sc

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
cfg = json.load(open("config.main.json", encoding="utf-8"))
TOKEN, API, V = cfg["service_token"], "https://api.vk.com/method/", "5.199"
GROUP_ID = -int(cfg["group_id"])
KRAT = timezone(timedelta(hours=7))

def vk(method, **p):
    p.update(access_token=TOKEN, v=V)
    d = requests.post(API + method, data=p, timeout=20).json()
    if "error" in d:
        raise RuntimeError(d["error"]["error_msg"])
    return d["response"]

def walk(items):
    for it in items:
        yield it
        yield from walk(it.get("copy_history") or [])

posts, off = [], 0
while True:
    r = vk("wall.get", owner_id=GROUP_ID, count=100, offset=off)
    items = r["items"]
    if not items:
        break
    posts += items
    off += len(items)
    if off >= r["count"]:
        break
    time.sleep(0.4)
print("постов на стене:", len(posts))

def norm(s):
    s = s.lower().replace("ѣ", "е").replace("є", "е").replace("э", "е")
    return re.sub(r"(.)\1+", r"\1", s)

def canon(t):
    t = re.sub(r"[^а-яёa-z0-9 ]+", " ", t.lower())
    return re.sub(r"\s+", " ", norm(t)).strip()

stems = sorted({norm(m)[:-1]: m for m in sc.SLAVIC_MONTHS}.items(),
               key=lambda kv: -len(kv[0]))

def slavic_from_text(text):
    for line in text.splitlines():
        ln = norm(line)
        for stem, cn in stems:
            pos = ln.find(stem)
            if pos < 0:
                continue
            m = re.search(r"(\d{1,2})\s*-?\s*го?\b\s*\S*\s*$", ln[:pos])
            if m and int(m.group(1)) <= 41:
                return cn, int(m.group(1))
    return None

HEADER = re.compile(r"сего дня|лето|сороковник|смзх|с\.м\.з\.х")
TITLE_RE = re.compile(r"^(⚡|✨|🔥|☀|День|Дѣнь|ДЕНЬ|Ночь|Славление|Входъ|Чертог)")

cards, weekday_words = {}, set()
for f in Path("content/holidays").glob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    sl = d.get("slavic") or {}
    if sl.get("month") and sl.get("day"):
        cards[(sl["month"], sl["day"])] = d
    if d.get("daily") or d.get("weekday"):
        w = d.get("text", "").split()
        if w:
            weekday_words.add(w[0].strip(".,:;!?"))

def first_title(text):
    for line in (l.strip() for l in text.splitlines()):
        if not line or HEADER.search(norm(line)):
            continue
        if line.split()[0].strip(".,:;!?") in weekday_words:
            continue
        return line
    return None

made, seen, filled = [], set(), []
for src in walk(posts):
    text = (src.get("text") or "").strip()
    if not text:
        continue
    title = first_title(text)
    if not title or not TITLE_RE.match(title):
        continue
    ct = canon(title)
    # дозаполнение существующей карточки
    for d in cards.values():
        if canon(d.get("text", "")) == ct:
            changed = False
            if not (d.get("text_md") or "").strip():
                body = [l for l in text.splitlines()
                        if l.strip() and l.strip() != title
                        and not HEADER.search(norm(l))]
                if body:
                    d["text_md"] = "\n".join(body).strip()
                    changed = True
            if not d.get("vk_photo"):
                ph = [a["photo"] for a in src.get("attachments", []) if a.get("type") == "photo"]
                if ph:
                    d["vk_photo"] = f"photo{ph[0]['owner_id']}_{ph[0]['id']}"
                    changed = True
            if changed:
                Path(f"content/holidays/{d['slug']}.json").write_text(
                    json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                filled.append(d["slug"])
            break
    # создание недостающих
    sl = slavic_from_text(text)
    if not sl:
        continue
    month, day = sl
    dt = datetime.fromtimestamp(src["date"], KRAT)
    g = sc.to_gregorian(month, day, start=datetime(dt.year, 1, 1).date())
    gdate = g if g else dt.date()
    key = (month, day)
    ex = cards.get(key)
    if ex:
        if ex.get("text", "").strip() != title:
            print(f"? {gdate} {month} {day}: карточка есть, текст другой: {title[:50]!r}")
        continue
    if key in seen:
        continue
    slug = re.sub(r"[^а-яё0-9]+", "-", title.lower()).strip("-")[:40]
    ph = [a["photo"] for a in src.get("attachments", []) if a.get("type") == "photo"]
    card = {
        "slug": slug,
        "date": gdate.strftime("%m-%d"),
        "slavic": {"month": month, "day": day},
        "text": title,
        "vk_photo": f"photo{ph[0]['owner_id']}_{ph[0]['id']}" if ph else None,
        "post_time": "18:00",
    }
    p = Path(f"content/holidays/{slug}.json")
    p.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cards[key] = card
    seen.add(key)
    made.append((gdate, title, p.name))

print(f"создано карточек: {len(made)}")
for g, t, name in made:
    print("  +", g, name, "|", t[:50])
print(f"дозаполнено карточек: {len(filled)}")
for s in filled:
    print("  ~", s)
