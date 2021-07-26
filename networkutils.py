import os

import requests
from dotenv import load_dotenv

import fileutils
import specialmarkets

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
    mesghal_dict = finance_dict[specialmarkets.Mesghal.MESGHAL_ID]

    mesghal_dict['sell_rate'] = fileutils.SHARED_PREFS_OBJECT['mesghalSellRate']
    mesghal_dict['buy_rate'] = fileutils.SHARED_PREFS_OBJECT['mesghalBuyRate']

    mesghal_object = specialmarkets.Mesghal(**mesghal_dict)
    return mesghal_object


def check_fetch_updated(mesghal_object):
    global last_mesghal_object
    if fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges']:
        if last_mesghal_object is not None and last_mesghal_object['p'] == mesghal_object['p']:
            return False

        last_mesghal_object = mesghal_object

    return True
