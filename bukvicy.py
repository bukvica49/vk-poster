"""bukvicy.py — кириллическая цифирь (буквицы).

Древнерусская система счисления. Значения:
  А=1 В=2 Г=3 Д=4 Е=5 Ѕ=6 З=7 И=8 Ѳ=9
  І=10 К=20 Л=30 М=40 Н=50 Ѯ=60 О=70 П=80 Ч=90
  Р=100 С=200 Т=300 У=400 Ф=500 Х=600 Ѱ=700 Ѡ=800 Ц=900
  ҂ (U+0482) — тысячный знак перед цифрой тысяч

Порядок: от старшего к младшему.
  13    -> "ІГ"        (10+3)
  7535  -> "҂ЗФЛЕ"     (7000+500+30+5)
  2026  -> "҂ВКЅ"      (2000+20+6)

Без титла — как принято в современной записи «Лѣто ҂ЗФЛЕ».
"""

ONES     = {1:'А', 2:'В', 3:'Г', 4:'Д', 5:'Е', 6:'Ѕ', 7:'З', 8:'И', 9:'Ѳ'}
TENS     = {1:'І', 2:'К', 3:'Л', 4:'М', 5:'Н', 6:'Ѯ', 7:'О', 8:'П', 9:'Ч'}
HUNDREDS = {1:'Р', 2:'С', 3:'Т', 4:'У', 5:'Ф', 6:'Х', 7:'Ѱ', 8:'Ѡ', 9:'Ц'}

TYSYACHA = '\u0482'   # ҂  тысячный знак
TITLO    = '\u0483'   # ҃  комбинируемое титло


def to_bukvicy(n: int, titlo: bool = False) -> str:
    """Return Cyrillic numeral for n (1..9999).

    titlo=False (по умолчанию) — без титла, как в «҂ЗФЛЕ».
    titlo=True — с титлом над последней буквой.
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f'positive integer expected, got {n!r}')
    if n >= 10000:
        raise ValueError('only 1..9999 supported (тьма/легион не нужны)')

    thousands, rest = divmod(n, 1000)
    hundreds, rest  = divmod(rest, 100)
    tens, ones      = divmod(rest, 10)

    out = []
    if thousands: out.append(TYSYACHA + ONES[thousands])
    if hundreds:  out.append(HUNDREDS[hundreds])
    if tens:      out.append(TENS[tens])
    if ones:      out.append(ONES[ones])

    s = ''.join(out)
    if titlo:
        s = s + TITLO
    return s


if __name__ == '__main__':
    for n in (1, 4, 13, 16, 18, 51, 100, 700, 2026, 7535):
        print(f'{n:>5}  {to_bukvicy(n):<10}  (с титлом: {to_bukvicy(n, titlo=True)})')
