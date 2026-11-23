import json, time, pathlib, functools

BUDGET_FILE = pathlib.Path("vk_budget.json")
DAILY_LIMIT = 40
QUIET_SEC = 3600
FLOOD_CODES = (6, 9, 29)

class VkQuiet(Exception):
    pass

def _load():
    try:
        return json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
    except:
        return {}

def _save(d):
    BUDGET_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2))

def guard(fn):
    @functools.wraps(fn)
    def wrapper(method, *a, **kw):
        d = _load()
        today = time.strftime("%Y-%m-%d")
        if d.get("day") != today:
            d = {"day": today, "count": 0, "quiet_until": 0}
        now = time.time()
        if now < d.get("quiet_until", 0):
            raise VkQuiet("тихий час")
        if d["count"] >= DAILY_LIMIT:
            raise VkQuiet("дневной лимит")
        d["count"] += 1
        _save(d)
        return fn(method, *a, **kw)
    return wrapper
