import os

import requests
from dateutil import parser
from dotenv import load_dotenv

import constants
import fileutils
import specialmarkets
from mathutils import *

API_URL = 'https://gateway.accessban.com/public/web-service/list/gold?format=json&limit=100&page=1'
load_dotenv()

TGJU_API_TOKEN = os.getenv('TGJU_API_TOKEN')
last_mesghal_object = None


def fetch_finance_data():
    response = requests.get(API_URL, headers={'Authorization': f'Bearer {TGJU_API_TOKEN}'})
    data = response.json()['data']
    return {data[i]['id']: data[i] for i in range(len(data))}


def extract_mesghal(finance_dict):
    [print(key, ' : ', value) for key, value in finance_dict.items()]
    mesghal_dict = finance_dict[specialmarkets.SpecialMarkets.mesghal_id]
    mesghal_object = specialmarkets.SpecialMarkets(**mesghal_dict)
    mesghal_object.sell_price += fileutils.SHARED_PREFS_OBJECT['mesghalUprate']
    mesghal_object.buy_price -= fileutils.SHARED_PREFS_OBJECT['mesghalDownrate']
    print(mesghal_object)
    return mesghal_object


def string_mesghal(mesghal_object: specialmarkets.SpecialMarkets, is_raw):
    title = f"{constants.EMOJI_BANK} <b>{specialmarkets.MESGHAL_MSG_FA}</b>                                   " \
            f"{constants.EMPTY_TRICK}\n\n"

    raw = f"{constants.EMOJI_MONEY_BAG} #{specialmarkets.MESGHAL_RAW_FA}: " \
          f"<b>{convert_digit_en_fa(convert_int_currency(mesghal_object.price))}</b>\n\n"

    rates = f"{constants.EMOJI_BLACK_CLUB} #{specialmarkets.MESGHAL_SELL_FA}: " \
            f"<b>{convert_digit_en_fa(convert_int_currency(mesghal_object.sell_price))}</b>\n\n"\
            f"{constants.EMOJI_BLACK_SPADE} #{specialmarkets.MESGHAL_BUY_FA}: " \
            f"<b>{convert_digit_en_fa(convert_int_currency(mesghal_object.buy_price))}</b>\n\n\n\n" \

    time = f"{constants.EMOJI_CLOCK_FACE_TWO} <b>{specialmarkets.MESGHAL_TIME_FA}:</b> " \
           f"{get_jalili_format(convert_date_jalili(mesghal_object.updated_at), True, True)}\n\n" \
           f"{constants.EMPTY_TRICK}"

    return title + (raw if is_raw else '') + rates + time


def check_fetch_updated(mesghal_object):
    global last_mesghal_object
    if fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges']:
        if last_mesghal_object is not None and last_mesghal_object['p'] == mesghal_object['p']:
            return False

        last_mesghal_object = mesghal_object

    return True
