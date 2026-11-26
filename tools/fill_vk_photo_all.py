#!/usr/bin/env python3
"""fill_vk_photo_all.py — дозаливает фото в альбом группы для карточек без VK-ID.
Запуск: python3 tools/fill_vk_photo_all.py [--dry]"""
import json, re, sys, time
from pathlib import Path
import requests

BASE = Path(__file__).resolve().parents[1]
CFG_FILE = BASE / "config.main.json"
DRY = "--dry" in sys.argv

cfg = json.loads(CFG_FILE.read_text(encoding="utf-8"))
GROUP_ID = cfg.get("group_id") or cfg.get("group")
TOKEN = cfg.get("user_token") or cfg.get("token")
assert GROUP_ID and TOKEN, "нет group_id или токена в config.main.json"
API = "https://api.vk.com/method/"

def vk(method, **params):
    params.update({"access_token": TOKEN, "v": "5.199"})
    r = requests.post(API + method, data=params, timeout=60).json()
    if "error" in r:
        raise RuntimeError(f"{method}: {r['error'].get('error_msg')}")
    return r["response"]

def upload_photo(path: Path) -> str:
    up = vk("photos.getWallUploadServer", group_id=GROUP_ID)
    with open(path, "rb") as fh:
        upl = requests.post(up["upload_url"], files={"photo": fh}, timeout=180).json()
    save = vk("photos.saveWallPhoto", group_id=GROUP_ID,
              photo=upl["photo"], server=upl["server"], hash=upl["hash"])
    p = save[0]
    return f"photo{p['owner_id']}_{p['id']}"

changed, failed = [], []
for f in sorted((BASE / "content/holidays").glob("*.json")):
    h = json.loads(f.read_text(encoding="utf-8"))
    vp = (h.get("vk_photo") or "").strip()

    if vp.startswith("photo-"):
        continue  # уже неубиваема
    if vp.startswith("http"):
        m = re.search(r"photo(-?\d+_\d+)", vp)
        if m:
            h["vk_photo"] = "photo" + m.group(1)
            h.pop("photo_failed", None)
            changed.append(f.name)
            print(f"✓ {f.name}: URL → {h['vk_photo']}")
        else:
            failed.append((f.name, "в URL нет photo-ID"))
        continue
    img = h.get("image")
    if not img:
        continue  # текстовая карточка — норм
    p = BASE / img.lstrip("/")
    if not p.exists():
        failed.append((f.name, f"файла нет: {img}"))
        continue
    if DRY:
        print(f"[dry] {f.name}: загрузить {p.name}")
        continue
    try:
        pid = upload_photo(p)
        h["vk_photo"] = pid
        h.pop("photo_failed", None)
        f.write_text(json.dumps(h, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed.append(f.name)
        print(f"✓ {f.name} → {pid}")
        time.sleep(1.5)
    except Exception as e:
        failed.append((f.name, str(e)))

for f in (BASE / "content/holidays").glob("*.json"):   # фиксируем правки URL-карточек
    if not DRY:
        pass

print(f"\nИтог: обновлено {len(changed)}, ошибок {len(failed)}")
for name, err in failed:
    print(f"  ✗ {name}: {err}")
