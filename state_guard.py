#!/usr/bin/env python3
"""Guard state: если state сломан — восстановить из .bak; если валиден — обновить .bak."""
import json, shutil, sys
from pathlib import Path

STATE = Path("state-200796423.json")
BAK   = Path("state-200796423.bak.json")

def valid(p: Path) -> bool:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"✗ {p.name}: {e}")
        return False
    pub = d.get("posted")
    if not isinstance(pub, list) or not all(isinstance(k, str) for k in pub):
        print(f"✗ {p.name}: 'posted' не список строк")
        return False
    return True

if not STATE.exists():
    if BAK.exists():
        shutil.copy(BAK, STATE)
        print("✓ state отсутствовал — восстановлен из .bak")
    else:
        sys.exit("✗ нет ни state, ни .bak — требуется ручное вмешательство")

if valid(STATE):
    shutil.copy(STATE, BAK)
    n = len(json.loads(STATE.read_text(encoding="utf-8"))["posted"])
    print(f"✓ state валиден ({n} ключей), .bak обновлён")
else:
    if BAK.exists() and valid(BAK):
        shutil.copy(BAK, STATE)
        print("✓ state сломан — восстановлен из .bak")
    else:
        sys.exit("✗ state сломан, .bak нет/сломан — требуется ручное вмешательство")
