#!/usr/bin/env python3
"""Удалить пост со стены VK-группы с проверкой.

Примеры:
    python3 tools/vk_delete.py 2675
    python3 tools/vk_delete.py -200796423_2675
    python3 tools/vk_delete.py https://vk.com/wall-200796423_2675
    python3 tools/vk_delete.py 2675 --dry-run     # только проверить
    python3 tools/vk_delete.py 2675 --no-verify   # удалить без проверки

Exit codes:
    0 — удалено (или уже удалено)
    1 — ошибка (конфиг/сеть/VK)
    2 — пост всё ещё виден после удаления
    3 — dry-run: пост найден, готов к удалению
"""
import argparse
import json
import pathlib
import re
import sys
import time

import requests

API = "https://api.vk.com/method/"
API_V = "5.199"
DEFAULT_CONFIG = "config.main.json"


def die(msg, code=1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


def load_config(path):
    p = pathlib.Path(path)
    if not p.exists():
        die(f"config не найден: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"config не парсится: {e}")


def api_call(method, token, **params):
    """→ (response | None, error | None)"""
    try:
        r = requests.post(API + method, data={**params, "access_token": token, "v": API_V}, timeout=30)
        data = r.json()
    except Exception as e:
        return None, {"error_msg": f"сетевая ошибка: {e}"}
    if "error" in data:
        return None, data["error"]
    return data.get("response"), None


def parse_target(raw, group_fallback):
    """→ (owner_id, post_id)"""
    raw = raw.strip()
    m = re.search(r"wall(-?\d+)_(\d+)", raw)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"^(-?\d+)_(\d+)$", raw)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.match(r"^\d+$", raw)
    if m:
        if not group_fallback:
            die("не задан group_id (--group или config.group_id)")
        return -abs(int(group_fallback)), int(m.group(0))
    die(f"не понял ID: {raw!r}")


def find_in_feed(token, owner_id, post_id, max_pages=15, page_size=100):
    """Свежий wall.get — есть ли пост на стене. → (present, item, total)

    Оптимизация: id идут по убыванию; если на странице последний id < искомого
    и закрепа не видели — дальше искать бессмысленно.
    """
    offset, total, seen_pinned = 0, 0, False
    for _ in range(max_pages):
        r, err = api_call("wall.get", token, owner_id=owner_id,
                          count=page_size, offset=offset, filter="all")
        if err:
            die(f"wall.get: [{err.get('error_code')}] {err.get('error_msg')}")
        items = r.get("items") or []
        total = r.get("count", 0)
        for it in items:
            if it.get("is_pinned"):
                seen_pinned = True
            if it["id"] == post_id:
                return True, it, total
        if items and not seen_pinned and items[-1]["id"] < post_id:
            return False, None, total
        offset += len(items)
        if not items or offset >= total:
            break
    return False, None, total


def main():
    ap = argparse.ArgumentParser(
        description="Удалить пост со стены VK-группы с проверкой.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("target", help="2675 | -200796423_2675 | https://vk.com/wall-200796423_2675")
    ap.add_argument("--group", type=int, help="group_id (если target = просто цифра)")
    ap.add_argument("--config", default=DEFAULT_CONFIG, help=f"конфиг (default: {DEFAULT_CONFIG})")
    ap.add_argument("--dry-run", action="store_true", help="только проверить наличие")
    ap.add_argument("--no-verify", action="store_true", help="удалить без проверки")
    args = ap.parse_args()

    cfg = load_config(args.config)
    token = cfg.get("user_token") or cfg.get("token")
    if not token:
        die("в config нет user_token / token")

    owner_id, post_id = parse_target(args.target, args.group or cfg.get("group_id"))
    post_url = f"https://vk.com/wall{owner_id}_{post_id}"
    print(f"🎯 пост: {owner_id}_{post_id}  →  {post_url}")

    # --- dry-run ---
    if args.dry_run:
        present, item, total = find_in_feed(token, owner_id, post_id)
        if present:
            date = time.strftime("%Y-%m-%d %H:%M", time.localtime(item["date"]))
            text = (item.get("text") or "").replace("\n", " ")[:120]
            print(f"  ✅ найден (всего постов на стене: {total})")
            print(f"     дата:  {date}")
            print(f"     текст: {text}")
            sys.exit(3)
        print(f"  ⚪ не найден (всего постов на стене: {total})")
        sys.exit(0)

    # --- удаление ---
    print("🗑  wall.delete …")
    _, err = api_call("wall.delete", token, owner_id=owner_id, post_id=post_id)
    if err:
        print(f"  ⚠ VK вернул ошибку [{err.get('error_code')}]: {err.get('error_msg', '?')}")
        print("     возможно, уже удалён — проверяю …")
    else:
        print("  ✅ VK подтвердил удаление")

    if args.no_verify:
        sys.exit(0)

    # --- проверка ---
    time.sleep(2)
    print("🔍 проверка через wall.get (свежая лента, без кэша) …")
    present, item, total = find_in_feed(token, owner_id, post_id)
    if not present:
        print(f"  ✅ поста нет в ленте (всего: {total}) — удалено")
        # бонус: предупредим если getById ещё кэширует
        resp, gerr = api_call("wall.getById", token, posts=f"{owner_id}_{post_id}")
        if not gerr:
            gitems = (resp.get("items") if isinstance(resp, dict) else resp) or []
            if gitems:
                print("  ℹ  getById пока показывает пост — это кэш VK, сбросится за 5–30 мин")
        sys.exit(0)

    print(f"  ❌ пост ВСЁ ЕЩЁ в ленте (всего: {total})")
    if item:
        date = time.strftime("%Y-%m-%d %H:%M", time.localtime(item["date"]))
        print(f"     id={item['id']}  дата={date}")
    print(f"     открой в инкогнито: {post_url}")
    sys.exit(2)


if __name__ == "__main__":
    main()
