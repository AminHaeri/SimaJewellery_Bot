import datetime
import os
import threading

import requests
import telebot
from dateutil import parser
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from persiantools import digits
from persiantools.jdatetime import JalaliDateTime

import constants as consts

API_URL = 'https://call16.tgju.org/ajax.json?2021071622-20210716230060-LkhfJvGIxwKp8Wa6k9Ti'
load_dotenv()

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode=None)
scheduler = BackgroundScheduler()

commands = ['fetch', 'testfetch', 'getprefs', 'setmeshgaluprate', 'setmeshgaldownrate', 'setperiodictime']
periodic_time = consts.PERIODIC_TIME
mesghal = {
    'uprate': consts.MESGHAL_UPRATE,
    'downrate': consts.MESGHAL_DOWNRATE
}


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


def fetch_finance_data():
    response = requests.get(API_URL)
    json_response = response.json()
    return json_response


def fetch_string():
    return string_mesghal(extract_mesghal(fetch_finance_data()))


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


def validate_rate(message, func):
    rate = message.text
    if not rate.isdigit():
        msg = bot.reply_to(message, f"Mesghal rate should a be number. Enter that again:")
        bot.register_next_step_handler(msg, func)
        return False

    rate = int(rate)
    if rate < 0:
        msg = bot.reply_to(message, f"Mesghal rate should a be a positive number. Enter that again:")
        bot.register_next_step_handler(msg, func)
        return False

    return True


def validate_periodic_time(message, func):
    time = message.text
    if not time.isdigit():
        msg = bot.reply_to(message, f"Periodic time should a be number. Enter that again:")
        bot.register_next_step_handler(msg, func)
        return False

    time = int(time)
    if time < consts.PERIODIC_TIME_MIN or time > consts.PERIODIC_TIME_MAX:
        msg = bot.reply_to(message, f"Periodic time should a be a number between "
                                    f"{consts.PERIODIC_TIME_MIN} and {consts.PERIODIC_TIME_MAX}. Enter that again:")
        bot.register_next_step_handler(msg, func)
        return False

    return True


def set_mesghal_uprate(message):
    if validate_rate(message, set_mesghal_uprate):
        mesghal['uprate'] = int(message.text)
        msg = f"Mesghal up rate successfully changed to <b>{convert_digit_en_fa(mesghal['uprate'])}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')


def set_mesghal_downrate(message):
    if validate_rate(message, set_mesghal_downrate):
        mesghal['downrate'] = int(message.text)
        msg = f"Mesghal down rate successfully changed to <b>{convert_digit_en_fa(mesghal['downrate'])}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')


def set_periodic_time(message):
    if validate_periodic_time(message, set_periodic_time):
        global periodic_time
        periodic_time = int(message.text)
        msg = f"Periodic time successfully change to <b>{convert_digit_en_fa(periodic_time)}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')


####################################### Telegram Bot Message Handlers #######################################
@bot.message_handler(commands=['fetch'])
def fetch_command(message):
    response_string = fetch_string()
    print(response_string)
    bot.send_message(chat_id=consts.CHANNEL_ID, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['testfetch'])
def test_fetch_command(message):
    response_string = fetch_string()
    bot.reply_to(message, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['getprefs'])
def get_prefs(message):
    prefs = f"<b>Mesghal</b>\n" \
            f"{'uprate(rial):' : <30}{convert_digit_en_fa(mesghal['uprate']) : ^20}\n" \
            f"{'downrate(rial):' : <30}{convert_digit_en_fa(mesghal['downrate']) : ^20}\n" \
            f"\n<b>Time</b>\n" \
            f"{'periodic time(minute):' : <30}{convert_digit_en_fa(periodic_time) : ^20}"

    print(prefs)
    bot.reply_to(message, prefs, parse_mode='HTML')


@bot.message_handler(commands=['setmeshgaluprate'])
def set_mesghal_uprate_request(message):
    msg = bot.reply_to(message, f"Please enter the integer value of the up rate for mesghal")
    bot.register_next_step_handler(msg, set_mesghal_uprate)


@bot.message_handler(commands=['setmeshgaldownrate'])
def set_mesghal_downrate_request(message):
    msg = bot.reply_to(message, f"Please enter the integer value of the down rate for mesghal")
    bot.register_next_step_handler(msg, set_mesghal_downrate)


@bot.message_handler(commands=['setperiodictime'])
def set_periodic_time_request(message):
    msg = bot.reply_to(message, f"Please enter the new value for periodic time."
                                f"\nIt must be a number between {consts.PERIODIC_TIME_MIN} to "
                                f"{consts.PERIODIC_TIME_MAX}.\n"
                                f"0 means it will turn off")
    bot.register_next_step_handler(msg, set_periodic_time)
    # start_polling_thread()


# @periodic_request.job(interval=timedelta(minutes=periodic_time))
# def periodic_request_interval():
#     print('periodic_request_interval')
#     fetch_command({})


# def start_periodic_request():
#     print('periodic call')
#     periodic_request.start()


# def start_polling_thread():
#     print(f"start new thread with: {periodic_time}")
#     periodic_thread = threading.Thread(target=start_periodic_request)
#     periodic_thread.start()


if __name__ == "__main__":
    # try:
    #     start_polling_thread()
    # except KeyboardInterrupt:
    #     periodic_request.stop()

    print('bot polling')
    bot.polling(none_stop=True)
