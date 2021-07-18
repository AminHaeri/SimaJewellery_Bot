import json
import os
import constants as consts
import requests
import telebot
import datetime, pytz
from telebot import types
from dotenv import load_dotenv
from dateutil import parser
from persiantools.jdatetime import JalaliDateTime
from persiantools import digits

load_dotenv()

API_URL = 'https://call16.tgju.org/ajax.json?2021071622-20210716230060-LkhfJvGIxwKp8Wa6k9Ti'
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode=None)
mesghal = {
    'uprate': consts.MESGHAL_UPRATE,
    'downrate': consts.MESGHAL_DOWNRATE
}
emoji = '\U000026C4'


def fetch_finance_data():
    response = requests.get(API_URL)
    json_response = response.json()
    return json_response


def convert_currency_int(currency):
    return int(currency.replace(',', ''))


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


def extract_mesghal(finance_object):
    mesghal_object = finance_object['current'][consts.MESGHAL_TEXT]
    return {
        'p': convert_currency_int(mesghal_object['p']),
        'uprate': convert_currency_int(mesghal_object['p']) + mesghal['uprate'],
        'downrate': convert_currency_int(mesghal_object['p']) - mesghal['downrate'],
        'time': convert_date_jalili(parser.parse(mesghal_object['ts']))
    }


def string_mesghal(mesghal_object):
    currency = {
        'p': convert_int_currency(mesghal_object['p']),
        'uprate': convert_int_currency(mesghal_object['uprate']),
        'downrate': convert_int_currency(mesghal_object['downrate'])
    }
    return f"{consts.EMOJI_BANK} <b>{consts.MESGHAL_MSG_FA}</b>                                   " \
           f"{consts.EMPTY_TRICK}\n\n" \
           f"{consts.EMOJI_BLACK_SPADE} #{consts.MESGHAL_BUY_FA}: <b>{convert_digit_en_fa(currency['downrate'])}</b>\n\n" \
           f"{consts.EMOJI_BLACK_CLUB} #{consts.MESGHAL_SELL_FA}: <b>{convert_digit_en_fa(currency['uprate'])}</b>\n\n\n\n" \
           f"{consts.EMOJI_CLOCK_FACE_TWO} <b>{consts.MESGHAL_TIME_FA}:</b> " \
           f"{get_jalili_format(mesghal_object['time'], True, True)}\n\n" \
           f"{consts.EMPTY_TRICK}"


def fetch_string():
    return string_mesghal(extract_mesghal(fetch_finance_data()))


@bot.message_handler(commands=['fetch'])
def fetch_command(message):
    response_string = fetch_string()
    print(response_string)
    bot.send_message(chat_id=consts.CHANNEL_ID, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['testFetch'])
def fetch_command(message):
    response_string = fetch_string()
    bot.reply_to(message, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['getPrefs'])
def get_prefs(message):
    prefs = f"<b>Mesghal</b>\n" \
            f"{'uprate:' : <10}{convert_digit_en_fa(mesghal['uprate']) : >15}\n" \
            f"{'downrate:' : <10} {convert_digit_en_fa(mesghal['downrate']) : >10}"

    bot.reply_to(message, prefs, parse_mode='HTML')


@bot.message_handler(commands=['setMeshgalUprate'])
def set_mesghal_uprate_request(message):
    msg = bot.reply_to(message, f"Please enter the integer value of the uprate for mesghal")
    bot.register_next_step_handler(msg, set_mesghal_uprate)


def set_mesghal_uprate(message):
    uprate = message.text
    if not uprate.isdigit():
        msg = bot.reply_to(message, f"Mesghal uprate should a be number. Enter that again:")
        bot.register_next_step_handler(msg, set_mesghal_uprate)
        return

    uprate = int(uprate)
    if uprate < 0:
        msg = bot.reply_to(message, f"Mesghal uprate should a be a positive number. Enter that again:")
        bot.register_next_step_handler(msg, set_mesghal_uprate)
        return

    mesghal['uprate'] = uprate
    bot.reply_to(message, f"Mesghal uprate successfully changed to : {mesghal['uprate']}")


bot.polling(none_stop=True)
