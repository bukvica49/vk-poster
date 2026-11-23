#!/usr/bin/env python3
"""Проверка канона Круголёта Числобога.

1. Структура Лѣт: обычное = 365 (41/40 чередование), Священное (Y % 16 == 0) = 369 (все по 41).
2. Недельный инвариант: нечётные месяцы Лѣта начинаются в один день недели,
   чётные — в другой, со сдвигом ровно 5 (41 + 40 = 81 = 9 недель).

Запуск: python3 tools/check_canon.py [гражданский_год]  (по умолчанию текущий)
"""
import sys
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from calendar_engine import krugолет, to_gregorian

def scan(start_year):
    d = to_gregorian("Рамхатъ", 1, start=date(start_year, 6, 1))
    Y = krugолет(d)[0]
    days, months, starts, wd = 0, {}, {}, None
    while True:
        k = krugолет(d)
        if k[0] != Y:
            break
        months[k[1]] = months.get(k[1], 0) + 1
        days += 1
        if k[2] == 1:
            starts[k[1]] = k[3]
        d += timedelta(days=1)
    return Y, days, months, starts

def main():
    y = int(sys.argv[1]) if len(sys.argv) > 1 else date.today().year
    Y, days, months, starts = scan(y)
    errors = []

    sacred = (Y % 16 == 0)
    want_days = 369 if sacred else 365
    if days != want_days:
        errors.append(f"Лѣто {Y}: дней {days}, канон требует {want_days}")
    for m, L in months.items():
        want = 41 if sacred else (41 if m % 2 == 0 else 40)
        if L != want:
            errors.append(f"Лѣто {Y}, месяц {m}: {L} дней, канон требует {want}")

    odd = {v for k, v in starts.items() if k % 2 == 0}
    even = {v for k, v in starts.items() if k % 2 == 1}
    if len(odd) != 1 or len(even) != 1:
        errors.append(f"Лѣто {Y}: нечётные месяцы стартуют с {odd}, чётные с {even} — инвариант недель нарушен")
    elif (list(even)[0] - list(odd)[0]) % 9 != 5:
        errors.append(f"Лѣто {Y}: сдвиг чёт/нечёт = {(list(even)[0]-list(odd)[0]) % 9}, канон требует 5")

    kind = "СВЯЩЕННОЕ (369)" if sacred else "обычное (365)"
    print(f"Лѣто {Y} — {kind}: дней {days}, месяцев {len(months)}, начал: нечётные wd {odd}, чётные wd {even}")
    if errors:
        for e in errors: print("✗", e)
        sys.exit(1)
    print("✓ канон сходится")

if __name__ == "__main__":
    main()
