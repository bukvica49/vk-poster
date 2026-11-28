#!/usr/bin/env python3
"""Показать отложку группы VK: дата, время, начало текста.
Запуск: python3 tools/vk_queue_view.py
Токен: как в остальном проекте (vk_token.txt или правкой константы)."""
import json, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

TOKEN = open("vk_token.txt").read().strip()
API = "https://api.vk.com/method/"
p = dict(owner_id=-200796423, filter="postponed", count=100,
         access_token=TOKEN, v="5.199")
r = json.load(urllib.request.urlopen(
    API + "wall.get", urllib.parse.urlencode(p).encode(), timeout=15))["response"]
TZ = timezone(timedelta(hours=7))
print("в отложке:", len(r["items"]))
for it in r["items"]:
    t = datetime.fromtimestamp(it["date"], TZ)
    print(f'  id={it["id"]}  {t:%d.%m %H:%M}  {(it["text"] or "")[:60]}')
