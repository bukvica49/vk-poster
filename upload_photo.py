#!/usr/bin/env python3
# Заливает картинку в альбом группы через group-токен и сразу печатает ID + URL.
# Запуск: python3 upload_photo.py путь/к/картинке.jpg
import json, urllib.request, urllib.parse, uuid, sys, pathlib

cfg = json.load(open("config.main.json", encoding="utf-8"))
gtok = cfg.get("token")
GROUP_ID = 200796423        # положительный, без минуса
ALBUM_ID = None             # загрузка на стену — альбом не нужен

def call(method, **params):
    q = urllib.parse.urlencode({**params, "access_token": gtok, "v": "5.199"})
    return json.loads(urllib.request.urlopen(
        f"https://api.vk.com/method/{method}", q.encode(), timeout=20).read())

# 1. адрес загрузки
r = call("photos.getWallUploadServer", group_id=GROUP_ID)
if "error" in r: sys.exit(f"ERROR getUploadServer: {r['error']['error_code']} — {r['error']['error_msg']}")
up = r["response"]["upload_url"]

# 2. сама загрузка файла
data = pathlib.Path(sys.argv[1]).read_bytes()
b = uuid.uuid4().hex
body = (f'--{b}\r\nContent-Disposition: form-data; name="file1"; filename="{sys.argv[1]}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n").encode() + data + f"\r\n--{b}--\r\n".encode()
resp = json.loads(urllib.request.urlopen(urllib.request.Request(
    up, body, {"Content-Type": f"multipart/form-data; boundary={b}"}), timeout=60).read())
if "error" in resp: sys.exit(f"ERROR upload: {resp.get('error', resp)}")

# 3. сохранение в альбом — здесь ВК отдаёт готовые размеры и URL
r = call("photos.saveWallPhoto", group_id=GROUP_ID,
         server=resp["server"], photo=resp["photo"], hash=resp["hash"])
if "error" in r: sys.exit(f"ERROR save: {r['error']['error_code']} — {r['error']['error_msg']}")
ph = r["response"][0]
best = max(ph["sizes"], key=lambda s: s.get("width", 0) or 0)
print(f"vk_photo: photo-{abs(ph['owner_id'])}_{ph['id']}")
print(f"url:      {best['url']}")
