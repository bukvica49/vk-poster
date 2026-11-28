#!/usr/bin/env python3
"""fill_tail.py — точечная доливка перечисленных праздников в отложку ВК.
Групповой токен; юзер-токен не используется. Запуск: python3 tools/fill_tail.py [--dry]
После заливки чистит state, чтобы ежедневный режим не задублировал."""
import sys, time
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path
import requests

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tools"))
import schedule_posts as sp
import poster

DRY = "--dry" in sys.argv
END = date(2026, 12, 27)   # Осьмiца 27.12 уже в отложке — её не трогаем

WANT = [
    "День Даждьбога и Марены",
    "День Марьяны и Марены",
    "Входъ въ Чертогъ Ворона",
    "День Успокоения",
    "День Перемен, Коляда",
    "День Спасителя РАСЫ",
]

def is_want(text):
    t = text.strip().lstrip("⚡ ")
    return any(t == w or t.startswith(w) for w in WANT)

def vk(method, **params):
    params.update({"access_token": sp.TOKEN, "v": "5.199"})
    for attempt in range(4):
        r = requests.post("https://api.vk.com/method/" + method, data=params, timeout=60).json()
        if "error" not in r:
            return r["response"]
        msg = r["error"].get("error_msg", "")
        if "flood" in msg.lower():
            wait = 3 + attempt * 3
            print(f"  флуд-контроль, ждём {wait}с…"); time.sleep(wait); continue
        raise RuntimeError(f"{method}: {msg}")
    raise RuntimeError("флуд-контроль не прошёл за 4 попытки")

def main():
    st = poster.load_state()
    new_keys, new_sched = [], {}
    n = 0
    d = date.today()
    while d <= END:
        items = sorted(poster.holidays_today(d) + poster.daily_items(d),
                       key=poster._post_sort_key)
        slot_pos = {}
        for text, image_path, info in items:
            if not is_want(text):
                continue
            key = f"{d.isoformat()}|{text}"
            if key in st.get("posted", []):
                print(f"  = {d} «{text[:45]}» уже в posted — пропускаю"); continue
            h = sp.find_h(text, image_path)
            post_hh, post_mm = 18, 0
            if h:
                pt = (h.get("post_time") or "").strip().replace("-", ":")
                if pt and ":" in pt:
                    a, b = pt.split(":", 1); post_hh, post_mm = int(a), int(b)
            sk = f"{post_hh:02d}:{post_mm:02d}"
            pos = slot_pos.get(sk, 0); slot_pos[sk] = pos + 1
            pub = datetime.combine(d, dtime(post_hh, post_mm)) + timedelta(minutes=pos * 30)
            if pub <= datetime.now() + timedelta(minutes=15):
                print(f"  ! {d} «{text[:45]}» слот уже прошёл ({pub:%H:%M}) — пропускаю"); continue
            message = sp.build_message(d, text, h, info)
            attach = sp.pick_attach(h, message)
            if DRY:
                print(f"[dry] {d} {pub:%H:%M} «{text[:45]}» фото={attach or '-'}")
                continue
            data = dict(owner_id=-abs(sp.GROUP_ID), from_group=1, message=message,
                        publish_date=int(pub.timestamp()))
            if attach:
                data["attachments"] = attach
            ok = False
            for shift in range(0, 6):          # до +150 минут, если слот занят
                try:
                    data2 = dict(data)
                    data2["publish_date"] = int(pub.timestamp()) + shift*1800
                    pid = vk("wall.post", **data2).get("post_id")
                    print(f"✓ {d} {(pub + timedelta(minutes=shift*30)):%H:%M} «{text[:45]}» → post_id {pid}")
                    new_keys.append(key)
                    new_sched[key] = {"post_id": pid, "publish": int(pub.timestamp()) + shift*1800,
                                      "image": image_path.name if image_path else ""}
                    n += 1
                    ok = True
                    time.sleep(1.0)
                    break
                except Exception as e:
                    if "already scheduled" in str(e):
                        print(f"  слот {d} {(pub + timedelta(minutes=shift*30)):%H:%M} занят — сдвиг на 30 мин")
                        time.sleep(0.5); continue
                    raise
            if not ok:
                print(f"  ✗ {d} «{text[:45]}»: свободного слота не нашлось", file=sys.stderr)
                time.sleep(3.0)
        d += timedelta(days=1)

    if DRY:
        print(f"\n[dry] найдено к заливке: {n}")
        return
    if new_keys:                       # инкрементально: что залили — то и в state
        _st = poster.load_state()
        _st["posted"] = sorted(set(_st.get("posted", [])) | set(new_keys))
        _st.setdefault("scheduled", {}).update(new_sched)
        poster.save_state(_st)
    print(f"\nИтог: залито {n}. state уже записан инкрементально.")
