#!/usr/bin/env python3
"""Прикрепить фото к уже опубликованному посту (wall.edit, уведомлений нет)."""
import json, sys, mimetypes
from pathlib import Path
import requests

BASE  = Path(__file__).resolve().parent
CONF  = json.loads((BASE / "config.main.json").read_text(encoding="utf-8"))
TOKEN = CONF.get("user_token") or CONF["token"]
GID   = CONF["group_id"]
API   = "https://api.vk.com/method/"
POST  = int(sys.argv[1]) if len(sys.argv) > 1 else 2663
IMG   = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None

def call(method, **p):
    r = requests.post(f"{API}{method}",
        data={**p, "access_token": TOKEN, "v": "5.199"}, timeout=30).json()
    if "error" in r:
        e = r["error"]
        raise RuntimeError(f"{method}: {e['error_code']} {e['error_msg']}")
    return r["response"]

if IMG is None:
    cands = list((BASE / "images").glob("Mir.*")) + list(BASE.glob("Mir.*"))
    if not cands:
        sys.exit("❌ не нашёл Mir.* — укажи путь вторым аргументом")
    IMG = cands[0]

if not IMG.exists():
    sys.exit(f"❌ нет файла {IMG}")

print(f"→ post {POST}, image {IMG} ({IMG.stat().st_size} bytes)")

# Предварительная диагностика токена
try:
    me = call("users.get")
    print(f"✓ token as user: {me[0].get('first_name')} {me[0].get('last_name')} (id {me[0].get('id')})")
except Exception as e:
    print(f"⚠ users.get failed: {e}")
try:
    perms = call("account.getAppPermissions")
    print(f"✓ token scopes bitmask: {perms}")
except Exception as e:
    print(f"⚠ account.getAppPermissions failed: {e}")

# Upload
srv = call("photos.getWallUploadServer", group_id=GID)
mime = mimetypes.guess_type(IMG.name)[0] or "image/jpeg"
with open(IMG, "rb") as f:
    up = requests.post(srv["upload_url"],
        files={"photo": (IMG.name, f, mime)}, timeout=120).json()
print(f"→ upload response: {up}")

if not up.get("photo"):
    print("❌ VK вернул пустое photo. Возможные причины:")
    print("   • user_token без scope 'photos'")
    print("   • токен = group-token (нужен user-token для загрузки)")
    print("   • VK временная ошибка")
    sys.exit(2)

saved = call("photos.saveWallPhoto", group_id=GID,
             server=up["server"], photo=up["photo"], hash=up["hash"])[0]
attach = f"photo{saved['owner_id']}_{saved['id']}"
print(f"✅ uploaded: {attach}")

call("wall.edit", owner_id=-GID, post_id=POST, attachments=attach)
print(f"✅ post {POST} updated: https://vk.com/wall-{GID}_{POST}")
