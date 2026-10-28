#!/usr/bin/env python3
# ~/vk-poster/poster.py — автопостер с картинками
import json
import sys
from datetime import date
from pathlib import Path
import requests
import slavic_calendar    # Круголет Числобога

BASE      = Path(__file__).resolve().parent
_cfg_name = next((a for a in sys.argv[1:]
                  if a.endswith(".json") and a not in ("holidays.json",)), "config.test.json")
CONFIG    = json.loads((BASE / _cfg_name).read_text(encoding="utf-8"))
STATE_FILE = BASE / f"state-{CONFIG['group_id']}.json"
HOLIDAYS   = BASE / "holidays.json"
API        = "https://api.vk.com/method/"


# ─── праздники из holidays.json ─────────────────────────────────

from datetime import timedelta


def _load_holidays_dicts():
    """Сырые dict'ы из holidays.json."""
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


def _build_info_safe(d):
    try:
        from slavic_auto import build_info
        return build_info(d)
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
    today = date.today()
    out = []
    for h in _load_holidays_dicts():
        d_this = _holiday_date(h, today.year)
        if d_this is None or d_this < today:
            d_this = _holiday_date(h, today.year + 1)
        if d_this is None:
            continue
        out.append((d_this.month, d_this.day, h["text"],
                    _resolve_image(h),
                    _build_info_safe(d_this) + _resolve_manual_info(h)))
    return out


def summer_from_smzh(d: date) -> int:
    if (d.month, d.day) < (9, 21):
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
                     _build_info_safe(d) + _resolve_manual_info(h)))
    return sorted(rows)


def holidays_today(today=None):
    today = today or date.today()
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
def main(dry_run=False, test=False):
    if test:
        today_iso, today_d = None, None
        items = [("🧪 Тест: автопостер на славянском календаре настроен и постит.", None, [])]
    else:
        today_d    = date.today()
        today_iso  = today_d.isoformat()
        items      = holidays_today(today_d)

    if not items:
        print(f"{today_iso}: праздников нет, выходим")
        return

    state = load_state()
    for text, image_path, info in items:
        key = f"{today_iso}|{text[:40]}" if today_iso else None
        if key and key in state["posted"]:
            print(f"уже постили: {key}")
            continue
        message = text
        if today_d:
            message += f"\n{slavic_calendar.header(today_d)}"
        if today_d and CONFIG.get("add_krug"):
            message += f"\n\nЛето {summer_from_smzh(today_d)} от С.М.З.Х."
        if info:
            message += "\n" + "\n".join(info)

        if dry_run:
            mark = f"  [фото: {image_path.name}]" if image_path else ""
            print(f"[DRY]\n{message}{mark}\n{'-' * 40}")
            continue

        try:
            try:
                attach = upload_photo(CONFIG["token"], CONFIG["group_id"], image_path) if image_path else None
            except Exception as e:
                print(f"WARN фото не загружено, постим текстом: {e}", file=sys.stderr)
                attach = None
            pid = post(CONFIG["token"], CONFIG["group_id"], message, attach)
            print(f"OK post_id={pid}: «{text[:60]}»")
            if key:
                state["posted"].append(key)
                save_state(state)
        except Exception as e:
            print(f"FAIL: {e}", file=sys.stderr)


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv, test="--test" in sys.argv)
