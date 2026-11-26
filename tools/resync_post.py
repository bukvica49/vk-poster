#!/usr/bin/env python3
"""resync_post.py — «обновить пост после редактирования».
Перезаливает отложенные посты VK из свежего JSON. Групповой токен, юзер-токен не нужен.
wall.edit групповому токену недоступен → удаляем старый пост и создаём заново (wall.post с publish_date).
Запуск: python3 tools/resync_post.py 2026-12-04 [ещё даты…]  |  --all (все будущие)"""
import json, sys
from datetime import date, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(Path(__file__).parent))
import poster
from schedule_posts import build_message, pick_attach, find_h, vk, GROUP_ID

STATE = poster.STATE_FILE

def main():
    args = sys.argv[1:]
    all_flag = "--all" in args
    dates = [a for a in args if not a.startswith("--")]
    st = json.loads(STATE.read_text(encoding="utf-8"))
    sched = st.get("scheduled", {})
    if not sched:
        print("в state нет scheduled — прогони доливку, чтобы посты запомнились с ID")
        return
    now_ts = datetime.now().timestamp()
    updated = failed = skipped = 0
    touched_keys = []
    for key, meta in sorted(sched.items()):
        d_iso, text = key.split("|", 1)
        if not all_flag and d_iso not in dates:
            continue
        if meta.get("publish", 0) <= now_ts:
            skipped += 1
            continue  # пост уже вышел/выходит — не трогаем
        d = date.fromisoformat(d_iso)
        h = find_h(text, (meta.get("image") or "").strip() or None)
        message = build_message(d, text, h, [])
        attach = pick_attach(h, message)
        # Шаг 1: попробовать честное редактирование (вдруг VK однажды разрешит)
        try:
            vk("wall.edit", owner_id=-abs(GROUP_ID), post_id=meta["post_id"],
               message=message, publish_date=meta["publish"], attachments=attach or "")
            print(f"✓ {d_iso} «{text[:40]}» обновлён (edit)")
            updated += 1
            touched_keys.append(key)
            continue
        except Exception as e_edit:
            if "authorization" not in str(e_edit).lower() and "access" not in str(e_edit).lower():
                failed += 1
                print(f"  ✗ {d_iso} «{text[:40]}»: {e_edit}")
                continue
        # Шаг 2: фолбэк — удалить и создать заново
        try:
            vk("wall.delete", owner_id=-abs(GROUP_ID), post_id=meta["post_id"])
            data = dict(owner_id=-abs(GROUP_ID), from_group=1,
                        message=message, publish_date=meta["publish"])
            if attach:
                data["attachments"] = attach
            pid = vk("wall.post", **data).get("post_id")
            meta["post_id"] = pid
            touched_keys.append(key)
            print(f"✓ {d_iso} «{text[:40]}» пересоздан (delete+post, новый id {pid})")
            updated += 1
        except Exception as e_repost:
            failed += 1
            print(f"  ✗ {d_iso} «{text[:40]}»: пересоздание не удалось: {e_repost}")
            # самопочинка: убрать мёртвый ключ — следующая доливка пересоздаст пост
            st["posted"] = [k for k in st.get("posted", []) if k != key]
            st["scheduled"] = {k: v for k, v in sched.items() if k != key}
            print(f"    ↻ ключ вычищен из state — перезапусти schedule_posts.py, пост вернётся")
    if touched_keys:
        STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"state обновлён ({len(touched_keys)} записей)")
    print(f"\nИтог: обновлено {updated}, пропущено {skipped}, ошибок {failed}")

if __name__ == "__main__":
    main()
