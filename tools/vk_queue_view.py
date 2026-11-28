#!/usr/bin/env python3
"""Показать отложку группы VK: дата, время, начало текста.
Запуск: python3 tools/vk_queue_view.py
Токен: как в остальном проекте (vk_token.txt или правкой константы)."""
import json, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

import json as _json
_budget = _json.load(open("vk_budget.json", encoding="utf-8"))
def _tokens(d):
    if isinstance(d, dict):
        for k, v in d.items():
            yield from ((k, s) for s in _tokens(v))
    elif isinstance(d, list):
        for v in d: yield from _tokens(v)
    elif isinstance(d, str) and len(d) > 30 and d.isalnum():
        yield None, d
_tok = [s for k, s in _tokens(_budget)]
TOKEN = _tok[0] if _tok else ""
if not TOKEN:
    raise SystemExit("не нашёл токен в vk_budget.json — смотри ключи шагом 1")
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
