#!/usr/bin/env python3
"""schedule_posts.py — доливка окна отложки VK на N дней вперёд.
Групповой токен; юзер-токен не используется.
Запуск: python3 tools/schedule_posts.py [--days=30] [--dry]
Успешно запланированные посты фиксируются в state["posted"], чтобы poster их не задублировал."""
import json, re, sys, time
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path
import requests

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))          # чтобы импортировать poster из корня
import poster
import slavic_calendar
import slavic_auto

CONFIG = poster.CONFIG
GROUP_ID = CONFIG["group_id"]
TOKEN = CONFIG["token"]                # групповой
if "ВСТАВЬ" in str(TOKEN) or "ОПЦИОНАЛЬНО" in str(TOKEN):
    print("В config.main.json плейсхолдер вместо токена — выходим."); sys.exit(2)

API = "https://api.vk.com/method/"
DRY = "--dry" in sys.argv
DAYS = next((int(a.split("=", 1)[1]) for a in sys.argv if a.startswith("--days=")), 30)

def vk(method, **params):
    params.update({"access_token": TOKEN, "v": "5.199"})
    r = requests.post(API + method, data=params, timeout=60).json()
    if "error" in r:
        raise RuntimeError(f"{method}: {r['error'].get('error_msg')}")
    return r["response"]

def fetch_postponed():
    out, offset = [], 0
    while True:
        r = vk("wall.get", owner_id=-abs(GROUP_ID), filter="postponed", count=100, offset=offset)
        items = r.get("items", [])
        out.extend(items)
        if len(items) < 100: break
        offset += 100
        time.sleep(0.4)
    return out

def find_h(text, image_path):
    _img = image_path.name if image_path else None
    for hd in poster._load_holidays_dicts():
        if hd.get("text") != text:
            continue
        rel = (hd.get("image") or "").strip()
        name = rel.rsplit("/", 1)[-1] if rel else None
        if _img and name == _img: return hd
        if not _img and not name: return hd
    return None

def build_message(today_d, text, h, info):
    info_auto, info_manual = list(info or []), []
    if h:
        try:
            post_t = h.get("post_time") or "19:00"
            _auto = slavic_auto.build_info(poster.post_slavic_date(today_d, post_t),
                                           chertog=bool(h.get("chertog")))
            _manual = poster._resolve_manual_info(h)
            info = _auto + _manual
            info_auto, info_manual = _auto, _manual
        except Exception as e:
            print(f"  ⚠ info: {e}", file=sys.stderr)
    head = []
    if today_d:
        _block, _range_to = None, None
        if h:
            try:
                _block, _range_to = slavic_auto.chertog_block_for(h, today_d)
            except Exception:
                pass
        try:
            head.append(slavic_calendar.header_full(
                today_d, add_smzh=CONFIG.get("add_krug"),
                range_to=_range_to, chertog_block=_block))
        except Exception:
            pass
    parts = []
    if text and text.strip():
        parts.append(poster._fuse_title(text, today_d))
    parts.extend(head)
    if info_auto: parts.append("\n".join(info_auto))
    tm = h.get("text_md") if h else None
    if tm:
        try: parts.append(poster.md_to_vk(tm))
        except Exception: parts.append(tm)
    if info_manual: parts.append("\n".join(info_manual))
    return "\n\n".join(parts)

def pick_attach(h, message):
    m = re.search(r"photo-?\d+_\d+", str((h.get("vk_photo") if h else "") or ""))
    if m: return m.group(0)
    pm = BASE / "photo_map.json"
    if pm.exists():
        for k, v in json.loads(pm.read_text(encoding="utf-8")).get("map", {}).items():
            if not k.startswith("_") and k in message:
                return v
    return None

def main():
    try:
        postponed = [] if DRY else fetch_postponed()
    except Exception as e:
        print(f"⚠ отложка VK недоступна групповому токену ({e}) — дедуп по state и стене")
        postponed = []
    today0 = date.today()
    added = skipped = errors = 0
    new_keys = []
    new_sched = {}
    for i in range(DAYS):
        d = today0 + timedelta(days=i)
        items = sorted(poster.holidays_today(d) + poster.daily_items(d),
                       key=poster._post_sort_key)
        if not items:
            continue
        _slot_used = set()
        for text, image_path, info in items:
            key = f"{d.isoformat()}|{text}"
            if key in poster.load_state().get("posted", []):
                skipped += 1; continue
            h = find_h(text, image_path)
            post_hh, post_mm = 19, 0   # дни недели и посты без post_time — на 19:00
            if h:
                pt = (h.get("post_time") or "").strip().replace("-", ":")
                if pt and ":" in pt:
                    try:
                        a, b = pt.split(":", 1); post_hh, post_mm = int(a), int(b)
                    except Exception:
                        pass
            pub = datetime.combine(d, dtime(post_hh, post_mm))
            while pub in _slot_used:
                pub += timedelta(minutes=30)
            _slot_used.add(pub)
            sk = pub.strftime("%H:%M")
            pos = (pub - datetime.combine(d, dtime(post_hh, post_mm))) // timedelta(minutes=30)
            if pub <= datetime.now() + timedelta(minutes=15):
                skipped += 1; continue   # время прошло — сегодняшний слот ведёт постер
            head_txt = text.strip()[:60]
            if any(p.get("text", "").strip().startswith(head_txt)
                   and datetime.fromtimestamp(p["date"]).date() == d
                   for p in postponed):
                skipped += 1; new_keys.append(key); continue
            message = build_message(d, text, h, info)
            attach = pick_attach(h, message)
            if DRY:
                print(f"[dry] {d} {pub:%H:%M} «{text[:40]}» фото={attach or '-'}")
                continue
            try:
                data = dict(owner_id=-abs(GROUP_ID), from_group=1, message=message,
                            publish_date=int(pub.timestamp()))
                if attach: data["attachments"] = attach
                pid = vk("wall.post", **data).get("post_id")
                print(f"✓ {d} {pub:%H:%M} «{text[:40]}»")
                new_keys.append(key)
                new_sched[key] = {"post_id": pid, "publish": int(pub.timestamp()),
                                  "image": image_path.name if image_path else ""}
                added += 1
                time.sleep(1.0)
            except Exception as e:
                if "already scheduled" in str(e):
                    skipped += 1
                    new_keys.append(key)   # слот занят: пост уже висит в отложке
                    print(f"  = {d} «{text[:40]}» уже стоит в отложке (слот занят)")
                    continue
                errors += 1
                print(f"  ✗ {d} «{text[:40]}»: {e}", file=sys.stderr)
                time.sleep(3.0)
    if not DRY and new_keys:
        st = poster.load_state()
        st["posted"] = sorted(set(st.get("posted", [])) | set(new_keys))
        st.setdefault("scheduled", {}).update(new_sched)
        poster.save_state(st)
    print(f"\nИтог: в отложку {added}, уже есть/пропущено {skipped}, ошибок {errors}")

if __name__ == "__main__":
    main()
