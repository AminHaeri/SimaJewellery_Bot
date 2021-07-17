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

load_dotenv()

API_URL = 'https://call16.tgju.org/ajax.json?2021071622-20210716230060-LkhfJvGIxwKp8Wa6k9Ti'
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode=None)


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


def get_jalili_format(dt, rtl):
    d = f"{dt.year}/{dt.month}/{dt.day}"
    t = f"{dt.hour}:{dt.minute}:{dt.second}"

    if rtl:
        return f"{t} - {d}"

    return f"{d} - {t}"


def extract_mesghal(finance_object):
    mesghal_object = finance_object['current'][consts.MESGHAL_TEXT]
    return {
        'p': convert_currency_int(mesghal_object['p']),
        'uprate': convert_currency_int(mesghal_object['p']) + consts.MESGHAL_UPRATE,
        'downrate': convert_currency_int(mesghal_object['p']) - consts.MESGHAL_DOWNRATE,
        'time': convert_date_jalili(parser.parse(mesghal_object['ts']))
    }


def string_mesghal(mesghal_object):
    currency = {
        'p': convert_int_currency(mesghal_object['p']),
        'uprate': convert_int_currency(mesghal_object['uprate']),
        'downrate': convert_int_currency(mesghal_object['downrate'])
    }
    return f"<b>{consts.MESGHAL_MSG_FA}</b>                                        <a href="">&#8204;</a>\n" \
           f"#{consts.MESGHAL_BUY_FA}: {currency['downrate']}\n" \
           f"#{consts.MESGHAL_SELL_FA}: {currency['uprate']}\n\n" \
           f"<b>{consts.MESGHAL_TIME_FA}:</b>\n" \
           f"{get_jalili_format(mesghal_object['time'], False) : >100}\n<a href="">&#8204;</a>"


@bot.message_handler(commands=['fetch'])
def fetch_command(message):
    response_string = string_mesghal(extract_mesghal(fetch_finance_data()))
    print(response_string)
    bot.send_message(chat_id='-1001598037268', text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['test'])
def test_channel(message):
    print('yes')
    bot.send_message(chat_id='@amingoldtest', text='yessssss')


bot.polling(none_stop=True)
