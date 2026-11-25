#!/usr/bin/env python3
# Резолвер vk_photo → URL: обновляет photo_urls.json для витрины.
# Запуск: python3 resolve_photo_urls.py  (после добавления новых vk_photo в CMS)
import json, re, pathlib, urllib.request, urllib.parse

HERE = pathlib.Path(__file__).parent
cfg = json.load(open(HERE / "config.main.json", encoding="utf-8"))
tok = cfg.get("group_token") or cfg.get("token")

ids = []
for jf in sorted((HERE / "content" / "holidays").glob("*.json")):
    try:
        d = json.loads(jf.read_text(encoding="utf-8"))
    except Exception:
        continue
    m = re.search(r"photo-?\d+_\d+", str(d.get("vk_photo") or ""))
    if m and m.group(0) not in ids:
        ids.append(m.group(0))

out = {"_comment": "кэш URL фото для витрины; обновлять: python3 resolve_photo_urls.py", "urls": {}}
if ids:
    q = urllib.parse.urlencode({"photos": ",".join(ids), "access_token": tok, "v": "5.199", "extended": "0"})
    r = json.loads(urllib.request.urlopen("https://api.vk.com/method/photos.getById", q.encode(), timeout=15).read())
    resp = r.get("response") or []
    if isinstance(resp, dict):
        resp = resp.get("items", [])
    for it in resp:
        sizes = it.get("sizes") or []
        best = max(sizes, key=lambda s: s.get("width", 0) or 0) if sizes else {}
        out["urls"][f"photo-{abs(it.get('owner_id', 0))}_{it.get('id', 0)}"] = best.get("url", "")

(HERE / "photo_urls.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"resolved {len(out['urls'])}/{len(ids)} vk_photo → photo_urls.json")
