#!/usr/bin/env python3
"""Показать отложку группы VK (только чтение). Запуск: python3 tools/vk_queue_view.py
Токен: групповой из config.main.json. Если VK не пускает его к wall.get —
разово: VK_USER_TOKEN=... python3 tools/vk_queue_view.py (юзер-токен в файлы не пишем)."""
import json, os, sys, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

_cfg = json.load(open("config.main.json", encoding="utf-8"))
TOKEN = str(_cfg.get("token") or "")
if not TOKEN or "ВСТАВЬ" in TOKEN or "ОПЦИОНАЛЬНО" in TOKEN:
    TOKEN = ""
if not TOKEN:
    sys.exit("нет группового токена в config.main.json")
ENV_USER = os.environ.get("VK_USER_TOKEN", "")
API = "https://api.vk.com/method/"
OWNER = -200796423

def call(method, **params):
    params.update({"access_token": TOKEN, "v": "5.199"})
    r = json.load(urllib.request.urlopen(
        API + method, urllib.parse.urlencode(params).encode(), timeout=15))
    return (r.get("response"), r.get("error"))

resp, err = call("wall.get", owner_id=OWNER, filter="postponed", count=100)
if err and err.get("error_code") in (15, 27, 204):
    if not ENV_USER:
        sys.exit("групповой токен не пускает к wall.get. Варианты:\n"
                 "  1) глянуть очередь в VK: Управление → Отложенные;\n"
                 "  2) разово: VK_USER_TOKEN=… python3 tools/vk_queue_view.py")
    TOKEN = ENV_USER
    resp, err = call("wall.get", owner_id=OWNER, filter="postponed", count=100)
if err:
    sys.exit(f"ошибка VK {err.get('error_code')}: {err.get('error_msg', '')}")

TZ = timezone(timedelta(hours=7))
print("в отложке:", len(resp["items"]))
for it in resp["items"]:
    t = datetime.fromtimestamp(it["date"], TZ)
    print(f'  id={it["id"]}  {t:%d.%m %H:%M}  {(it["text"] or "")[:60]}')
