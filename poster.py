#!/usr/bin/env python3
# ~/vk-poster/poster.py — автопостер с картинками
import json
import sys
from datetime import date, datetime, time
from pathlib import Path
import requests
import slavic_calendar
from md_to_vk import md_to_vk    # Круголет Числобога

BASE      = Path(__file__).resolve().parent
_cfg_name = next((a for a in sys.argv[1:]
                  if a.endswith(".json") and a not in ("holidays.json",)), "config.main.json")
CONFIG    = json.loads((BASE / _cfg_name).read_text(encoding="utf-8"))
STATE_FILE = BASE / f"state-{CONFIG['group_id']}.json"
HOLIDAYS   = BASE / "holidays.json"
API        = "https://api.vk.com/method/"


# ─── праздники из holidays.json ─────────────────────────────────

from datetime import timedelta


def _load_holidays_dicts():
    """Сырые dict'ы из content/holidays/*.json (fallback: holidays.json)."""
    hd = BASE / "content" / "holidays"
    if hd.is_dir():
        items = []
        for f in sorted(hd.glob("*.json")):
            try:
                items.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
        if items:
            return items
    data = json.loads(HOLIDAYS.read_text(encoding="utf-8"))
    return data["holidays"]


def _slavic_parse(gr_date):
    """'ВТОРНИКЪ · 40 Рамхатъ · Лѣто 7535' -> (40, 'Рамхатъ', 7535)"""
    try:
        h = slavic_calendar.header(gr_date)
    except Exception:
        return None
    parts = h.split(" · ")
    if len(parts) < 3:
        return None
    try:
        dm = parts[1].split(" ")
        leto = int(parts[2].replace("Лѣто ", "").replace("Лето ", "").strip())
        return (int(dm[0]), dm[1] if len(dm) > 1 else "", leto)
    except (ValueError, IndexError):
        return None


def slavic_to_gregorian(year, slavic_month, slavic_day):
    """Gregorian-дата в указанном году, где Slavic = (месяц, день)."""
    cur, end = date(year, 1, 1), date(year, 12, 31)
    while cur <= end:
        p = _slavic_parse(cur)
        if p and p[0] == slavic_day and p[1] == slavic_month:
            return cur
        cur += timedelta(days=1)
    return None


def _holiday_date(h, year):
    """Дата праздника в году: slavic -> reverse, иначе date."""
    sl = h.get("slavic")
    if sl and sl.get("month") and sl.get("day"):
        d = slavic_to_gregorian(year, sl["month"], sl["day"])
        if d is not None:
            return d
    try:
        mm, dd = h["date"].split("-")
        return date(year, int(mm), int(dd))
    except (KeyError, ValueError, AttributeError):
        return None


def _build_info_safe(d, chertog=False):
    try:
        from slavic_auto import build_info
        return build_info(d, chertog=chertog)
    except Exception:
        return []


def _resolve_image(h):
    img = h.get("image")
    return (BASE / img.lstrip("/")) if img else None


def _resolve_manual_info(h):
    manual = h.get("info") or []
    if isinstance(manual, str):
        manual = [manual]
    return [s.strip() for s in manual]


def load_holidays():
    """Backward-compat: (m, d, text, img, info) для текущего/следующего года."""
    today = slavic_calendar.today_krat()
    out = []
    for h in _load_holidays_dicts():
        d_this = _holiday_date(h, today.year)
        if d_this is None or d_this < today:
            d_this = _holiday_date(h, today.year + 1)
        if d_this is None:
            continue
        out.append((d_this.month, d_this.day, h["text"],
                    _resolve_image(h),
                    _build_info_safe(d_this + timedelta(days=1)) + _resolve_manual_info(h)))
    return out


def summer_from_smzh(d: date) -> int:
    if (d.month, d.day) < (9, 20):
        return d.year + 5508
    return d.year + 5509


def holidays_for_year(year: int):
    """Все праздники указанного года, отсортированные по дате."""
    rows = []
    for h in _load_holidays_dicts():
        d = _holiday_date(h, year)
        if d is None or d.year != year:
            continue
        rows.append((d, h["text"],
                     _resolve_image(h),
                     _build_info_safe(d + timedelta(days=1)) + _resolve_manual_info(h)))
    return sorted(rows)


def holidays_today(today=None):
    today = today or slavic_calendar.slavic_now()
    return [(t, i, info) for d, t, i, info in holidays_for_year(today.year) if d == today]


# ─── VK API ─────────────────────────────────────────────────────
def upload_photo(token, group_id, filepath):
    """Загружает фото в альбом группы → возвращает 'photo-XXX_YYY' или None."""
    if not filepath or not filepath.exists():
        return None

    # 1. адрес загрузки
    r = requests.post(API + "photos.getWallUploadServer", data={
        "access_token": token, "group_id": group_id, "v": "5.199",
    }, timeout=30).json()
    if "error" in r:
        e = r["error"]
        raise RuntimeError(f"getWallUploadServer {e.get('error_code')}: {e.get('error_msg')}")
    upload_url = r["response"]["upload_url"]

    # 2. залить файл
    with open(filepath, "rb") as f:
        up = requests.post(upload_url, files={"photo": f}, timeout=120).json()
    if not up.get("photo"):
        raise RuntimeError(f"upload: пустой ответ {up}")

    # 3. сохранить на стене
    r = requests.post(API + "photos.saveWallPhoto", data={
        "access_token": token, "group_id": group_id,
        "server": up["server"], "photo": up["photo"], "hash": up["hash"],
        "v": "5.199",
    }, timeout=30).json()
    if "error" in r:
        e = r["error"]
        raise RuntimeError(f"saveWallPhoto {e.get('error_code')}: {e.get('error_msg')}")
    ph = r["response"][0]
    return f"photo{ph['owner_id']}_{ph['id']}"


def post(token, group_id, message, attachments=None):
    data = {
        "access_token": token, "owner_id": -abs(group_id),
        "from_group": 1, "message": message, "v": "5.199",
    }
    if attachments:
        data["attachments"] = attachments
    r = requests.post(API + "wall.post", data=data, timeout=30).json()
    if "error" in r:
        e = r["error"]
        raise RuntimeError(f"VK error {e.get('error_code')}: {e.get('error_msg')}")
    return r["response"]["post_id"]


# ─── state ──────────────────────────────────────────────────────
def load_state():
    return json.loads(STATE_FILE.read_text(encoding="utf-8")) \
           if STATE_FILE.exists() else {"posted": []}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2, ensure_ascii=False), encoding="utf-8")


# ─── основной цикл ──────────────────────────────────────────────
def _post_sort_key(item):
    """Приоритет: «День …» → «Чертог …» → прочие (по алфавиту)."""
    t = (item[0] or '')
    if t.startswith('День ') or t.startswith('День\u00a0'):
        return (0, t)
    if 'Чертог' in t:
        return (1, t)
    return (2, t)


def main(dry_run=False, test=False, force=False, republish=False, override_date=None):
    if test:
        today_iso, today_d = None, None
        items = [("🧪 Тест: автопостер на славянском календаре настроен и постит.", None, [])]
    elif override_date:
        today_d    = date.fromisoformat(override_date)
        today_iso  = today_d.isoformat()
        items      = holidays_today(today_d)
        print(f"[override] date={today_iso}, найдено: {len(items)}")
    else:
        today_d    = slavic_calendar.slavic_now()
        today_iso  = today_d.isoformat()
        items      = holidays_today(today_d)

    if not items:
        print(f"{today_iso}: праздников нет, выходим")
        return

    state = load_state()
    items = sorted(items, key=_post_sort_key)

    from time import sleep as _sleep

    _slot_pos = {}
    _failures = []

    for text, image_path, info in items:
        key = f"{today_iso}|{text}" if today_iso else None
        if key and key in state["posted"] and not republish:
            print(f"уже постили: {key}")
            continue

        _img_name = image_path.name if image_path else None
        h = None
        for hd in _load_holidays_dicts():
            if hd.get('text') != text:
                continue
            hd_img_rel = (hd.get('image') or '').strip()
            hd_img_name = hd_img_rel.rsplit('/', 1)[-1] if hd_img_rel else None
            if _img_name and hd_img_name == _img_name:
                h = hd
                break
            if not _img_name and not hd_img_name:
                h = hd
                break
        if h is None:
            print(f"  ⚠  h не найден для «{text[:40]}» — post_time/чертог дефолтные")

        # ── пересчёт info с учётом chertog ──
        if h:
            try:
                from slavic_auto import build_info as _build_info
                _flag = bool(h.get('chertog'))
                _auto = _build_info(today_d + timedelta(days=1), chertog=_flag)
                info = _auto + _resolve_manual_info(h)
            except Exception:
                pass

        # ── post_time + slot ──
        post_hh, post_mm = 18, 0
        if h:
            _pt = (h.get("post_time") or "").strip()
            if _pt and ":" in _pt:
                try:
                    _h, _m = _pt.split(":", 1)
                    post_hh, post_mm = int(_h), int(_m)
                except Exception:
                    pass

        _slot_key = f"{post_hh:02d}:{post_mm:02d}"
        _pos = _slot_pos.get(_slot_key, 0)
        _slot_pos[_slot_key] = _pos + 1

        _now = datetime.now()
        _target_dt = None
        if today_d:
            if _now.hour >= 18:
                _start = datetime.combine(_now.date(), time(18, 0))
            else:
                _start = datetime.combine(_now.date() - timedelta(days=1), time(18, 0))
            _offset_min = (post_hh * 60 + post_mm) - (18 * 60)
            if _offset_min < 0:
                _offset_min += 24 * 60
            _target_dt = _start + timedelta(minutes=_offset_min)

        _slot_dt = _target_dt + timedelta(minutes=_pos * 10) if _target_dt else None

        if (not dry_run) and (not force) and (not override_date) and _slot_dt:
            POST_WINDOW_HOURS = 6
            if _now < _slot_dt:
                wait_s = (_slot_dt - _now).total_seconds()
                if wait_s > POST_WINDOW_HOURS * 3600:
                    print(f"  ⏳ рано (сейчас {_now:%H:%M}, слот {_slot_dt:%H:%M}, {wait_s/3600:.1f}ч) → следующий год")
                    _slot_pos[_slot_key] = _pos
                    continue
                if wait_s > 0:
                    print(f"  ⏱ ждём {wait_s:.0f}s до слота {_slot_dt:%H:%M} («{text[:40]}»)")
                    _sleep(wait_s)
                    _now = datetime.now()
            if _now > _slot_dt + timedelta(hours=POST_WINDOW_HOURS):
                print(f"  ⏭ окно {POST_WINDOW_HOURS}ч истекло (слот {_slot_dt:%H:%M}) → следующий год")
                _slot_pos[_slot_key] = _pos
                continue

        # ── шапка ──
        _tm = h.get('text_md') if h else None
        body = md_to_vk(_tm) if _tm else text
        head = []
        if today_d:
            _block, _range_to = (None, None)
            if h:
                try:
                    from slavic_auto import chertog_block_for
                    _block, _range_to = chertog_block_for(h, today_d)
                except Exception:
                    _block, _range_to = None, None
            _hl = slavic_calendar.header_full(
                today_d, add_smzh=CONFIG.get("add_krug"),
                range_to=_range_to, chertog_block=_block,
            )
            head.append(_hl)
        if info:
            head.append("\n".join(info))
        message = ("\n".join(head) + "\n\n" + body) if head else body

        if dry_run:
            if image_path:
                status = "✓" if image_path.exists() else "✗ НЕТ ФАЙЛА"
                mark = f"  [фото: {image_path.name} {status}]"
            else:
                mark = ""
            print(f"[DRY]\n{message}{mark}\n{'-' * 40}")
            continue

        try:
            attach = None
            if image_path:
                if not image_path.exists():
                    print(f"  ⚠  файл не найден: {image_path.name} → пост без фото", file=sys.stderr)
                else:
                    try:
                        upload_token = CONFIG.get("user_token") or CONFIG["token"]
                        attach = upload_photo(upload_token, CONFIG["group_id"], image_path)
                        if not attach:
                            print(f"  ⚠  upload_photo вернул None для {image_path.name} → пост без фото", file=sys.stderr)
                    except Exception as e:
                        print(f"  ⚠  фото не загрузилось ({e}) → пост без фото", file=sys.stderr)
                        attach = None

            pid = post(CONFIG["token"], CONFIG["group_id"], message, attach)
            print(f"OK post_id={pid}: «{text[:60]}» attach={attach or 'none'}")
            if key:
                state["posted"].append(key)
                save_state(state)
        except Exception as e:
            print(f"FAIL: «{text[:60]}» — {e}", file=sys.stderr)
            _failures.append((text, str(e)))
            continue

    if _failures:
        print(f"\n{len(_failures)} пост(ов) упало:", file=sys.stderr)
        for t, e in _failures:
            print(f"  ✗ {t[:60]} — {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--dry-run", action="store_true")
    _ap.add_argument("--test", action="store_true")
    _ap.add_argument("--force", action="store_true",
                     help="публиковать сейчас, игнорируя post_time (state соблюдается)")
    _ap.add_argument("--republish", action="store_true",
                     help="разрешить повторную публикацию (игнорирует state)")
    _ap.add_argument("--date", dest="override_date", default=None,
                     metavar="YYYY-MM-DD", help="эмулировать славянский день")
    _args = _ap.parse_args()
    main(dry_run=_args.dry_run, test=_args.test, force=_args.force,
         republish=_args.republish, override_date=_args.override_date)
