#!/usr/bin/env python3
# Резолвер vk_photo → URL через wall.get: собирает вложения постов группы в photo_urls.json.
# Запуск: python3 resolve_photo_urls.py  (после публикации постов с фото)
import json, urllib.request, urllib.parse

HERE = __import__("pathlib").Path(__file__).parent
cfg = json.load(open(HERE / "config.main.json", encoding="utf-8"))
tok = cfg.get("service_token") or cfg.get("group_token") or cfg.get("token")
GROUP = -200796423

def call(method, **params):
    q = urllib.parse.urlencode({**params, "access_token": tok, "v": "5.199"})
    return json.loads(urllib.request.urlopen(
        f"https://api.vk.com/method/{method}", q.encode(), timeout=15).read())

urls, offset, total_pages = {}, 0, 0
while total_pages < 40:  # страховка от вечного цикла
    r = call("wall.get", owner_id=GROUP, count=100, offset=offset)
    if "error" in r:
        print("wall.get ERROR:", r["error"]["error_code"]); break
    items = r["response"]["items"]
    if not items:
        break
    for it in items:
        for att in (it.get("attachments") or []):
            if att.get("type") == "photo":
                ph = att["photo"]
                best = max(ph.get("sizes", []), key=lambda s: s.get("width", 0) or 0)
                urls[f"photo-{abs(ph['owner_id'])}_{ph['id']}"] = best.get("url", "")
    offset += len(items)
    total_pages += 1

out = {"_comment": "кэш URL фото для витрины; обновлять: python3 resolve_photo_urls.py", "urls": urls}
(HERE / "photo_urls.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"resolved {len(urls)} vk_photo → photo_urls.json (посты: {offset})")


# ─── авто-чистка старых локальных картинок ───
# если у поста вписан vk_photo и URL уже найден — поле image и файл images/ больше не нужны
import sys as _sys
_dry = "--dry-run" in _sys.argv

def _wipe(obj, jf_name, dry):
    n = 0
    if isinstance(obj, dict):
        if obj.get("image") and obj.get("vk_photo") and urls.get(obj["vk_photo"]):
            img = obj.pop("image")
            f = HERE / img.lstrip("/")
            if f.exists() and not dry:
                f.unlink()
            print(f"  🗑 {img}  (из {jf_name}, vk_photo={obj['vk_photo']})")
            n += 1
        for v in obj.values():
            n += _wipe(v, jf_name, dry)
    elif isinstance(obj, list):
        for v in obj:
            n += _wipe(v, jf_name, dry)
    return n

print("чистка старых картинок" + (" (dry-run)" if _dry else ""))
_cleaned = 0
for _jf in sorted((HERE / "content" / "holidays").glob("*.json")):
    _d = json.loads(_jf.read_text(encoding="utf-8"))
    _n = _wipe(_d, _jf.name, _dry)
    if _n:
        _cleaned += _n
        if not _dry:
            _jf.write_text(json.dumps(_d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
_hj = HERE / "holidays.json"
if _hj.exists():
    _d = json.loads(_hj.read_text(encoding="utf-8"))
    _n = _wipe(_d, "holidays.json", _dry)
    if _n:
        _cleaned += _n
        if not _dry:
            _hj.write_text(json.dumps(_d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"вычищено записей: {_cleaned}" + (" (dry-run — пробный прогон)" if _dry else ""))
