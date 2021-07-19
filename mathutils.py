import datetime

from persiantools import digits
from persiantools.jdatetime import JalaliDateTime


def convert_int_currency(intvalue):
    return '{:,}'.format(intvalue)


def convert_date_jalili(dt):
    return JalaliDateTime.to_jalali(
        datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))


def get_jalili_format(dt, rtl, fa):
    d = f"{dt.year}/{dt.month}/{dt.day}"
    t = f"{dt.hour}:{dt.minute}:{dt.second}"

    if fa:
        d = digits.en_to_fa(d)
        t = digits.en_to_fa(t)

    if rtl:
        return f"{t} - {d}"

    return f"{d} - {t}"


def convert_digit_en_fa(digit):
    return digits.en_to_fa(str(digit))


def convert_currency_int(currency):
    return int(currency.replace(',', ''))
