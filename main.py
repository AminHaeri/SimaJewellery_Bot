import os

import requests
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import parser
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import constants
import fileutils
from mathutils import *

API_URL = 'https://call16.tgju.org/ajax.json?2021071622-20210716230060-LkhfJvGIxwKp8Wa6k9Ti'
load_dotenv()

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode=None)
scheduler = BackgroundScheduler()

job_periodic_fetch = None

commands = ['get', 'fetch', 'testfetch', 'getprefs', 'setmesghaluprate', 'setmesghaldownrate',
            'setperiodictime', 'setonlychangesfetch']
last_mesghal_object = None


def fetch_finance_data():
    response = requests.get(API_URL)
    json_response = response.json()
    return json_response


def check_fetch_updated(mesghal_object):
    global last_mesghal_object
    if fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges']:
        if last_mesghal_object is not None and last_mesghal_object['p'] == mesghal_object['p']:
            return False

        last_mesghal_object = mesghal_object

    return True


def extract_mesghal(finance_object):
    mesghal_object = finance_object['current'][constants.MESGHAL_TEXT]
    return {
        'p': convert_currency_int(mesghal_object['p']),
        'uprate': convert_currency_int(mesghal_object['p']) + fileutils.SHARED_PREFS_OBJECT['mesghalUprate'],
        'downrate': convert_currency_int(mesghal_object['p']) - fileutils.SHARED_PREFS_OBJECT['mesghalDownrate'],
        'time': convert_date_jalili(parser.parse(mesghal_object['ts']))
    }


def string_mesghal(mesghal_object, is_raw):
    currency = {
        'p': convert_int_currency(mesghal_object['p']),
        'uprate': convert_int_currency(mesghal_object['uprate']),
        'downrate': convert_int_currency(mesghal_object['downrate'])
    }
    title = f"{constants.EMOJI_BANK} <b>{constants.MESGHAL_MSG_FA}</b>                                   " \
            f"{constants.EMPTY_TRICK}\n\n"

    raw = f"{constants.EMOJI_BANK} #{constants.MESGHAL_RAW_FA}: " \
          f"<b>{convert_digit_en_fa(currency['p'])}</b>\n\n"

    rates = f"{constants.EMOJI_BLACK_SPADE} #{constants.MESGHAL_BUY_FA}: " \
            f"<b>{convert_digit_en_fa(currency['downrate'])}</b>\n\n" \
            f"{constants.EMOJI_BLACK_CLUB} #{constants.MESGHAL_SELL_FA}: " \
            f"<b>{convert_digit_en_fa(currency['uprate'])}</b>\n\n\n\n"

    time = f"{constants.EMOJI_CLOCK_FACE_TWO} <b>{constants.MESGHAL_TIME_FA}:</b> " \
           f"{get_jalili_format(mesghal_object['time'], True, True)}\n\n" \
           f"{constants.EMPTY_TRICK}"

    return title + (raw if is_raw else '') + rates + time


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
    if time < constants.PERIODIC_TIME_MIN or time > constants.PERIODIC_TIME_MAX:
        msg = bot.reply_to(message, f"Periodic time should a be a number between "
                                    f"{constants.PERIODIC_TIME_MIN} and {constants.PERIODIC_TIME_MAX}. Enter that again:")
        bot.register_next_step_handler(msg, func)
        return False

    return True


def updateSharedPrefsFile():
    fileutils.write_shared_prefs(fileutils.SHARED_PREFS_OBJECT)


def set_mesghal_uprate(message):
    if validate_rate(message, set_mesghal_uprate):
        fileutils.SHARED_PREFS_OBJECT['mesghalUprate'] = int(message.text)
        msg = f"Mesghal up rate successfully changed to <b>{fileutils.SHARED_PREFS_OBJECT['mesghalUprate']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')

    updateSharedPrefsFile()


def set_mesghal_downrate(message):
    if validate_rate(message, set_mesghal_downrate):
        fileutils.SHARED_PREFS_OBJECT['mesghalDownrate'] = int(message.text)
        msg = f"Mesghal down rate successfully changed to <b>{fileutils.SHARED_PREFS_OBJECT['mesghalDownrate']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')

        updateSharedPrefsFile()


def set_periodic_time(message):
    if validate_periodic_time(message, set_periodic_time):
        modify_periodic_job_fetch(int(message.text))
        msg = f"Periodic time successfully changed to <b>{fileutils.SHARED_PREFS_OBJECT['periodicTime']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')

        updateSharedPrefsFile()


def modify_periodic_job_fetch(new_time):
    fileutils.SHARED_PREFS_OBJECT['periodicTime'] = new_time
    scheduler.reschedule_job(
        job_id=job_periodic_fetch.id,
        trigger='interval',
        minutes=fileutils.SHARED_PREFS_OBJECT['periodicTime'])


def gen_markup_only_changes_fetch():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('On', callback_data='cb_on'), InlineKeyboardButton('Off', callback_data='cb_off'))
    return markup


@bot.message_handler(commands=['help'])
def help_command(message):
    help_string = f"List of command available:\n\n" + fileutils.read_help()
    bot.reply_to(message, text=help_string, parse_mode='HTML')


@bot.message_handler(commands=['show'])
def get_command(message):
    mesghal_object = extract_mesghal(fetch_finance_data())
    response_string = string_mesghal(mesghal_object, True)
    print(response_string)

    bot.reply_to(message, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['fetch'])
def fetch_command(message):
    print(message)
    mesghal_object = extract_mesghal(fetch_finance_data())
    if check_fetch_updated(mesghal_object):
        response_string = string_mesghal(mesghal_object, False)
        print(response_string)
        bot.send_message(chat_id=constants.CHANNEL_ID, text=response_string, parse_mode='HTML')
    else:
        print(f"There is no changes to last prices")


@bot.message_handler(commands=['testfetch'])
def test_fetch_command(message):
    mesghal_object = extract_mesghal(fetch_finance_data())
    if check_fetch_updated(mesghal_object):
        response_string = string_mesghal(mesghal_object, False)
        bot.reply_to(message, text=response_string, parse_mode='HTML')
    else:
        bot.reply_to(message, f"There is no changes to last prices")


@bot.message_handler(commands=['getprefs'])
def get_prefs(message):
    prefs = f"<b>Mesghal</b>\n" \
            f"{'uprate (rial):'}  {convert_digit_en_fa(fileutils.SHARED_PREFS_OBJECT['mesghalUprate'])}\n" \
            f"{'downrate (rial):'}  {convert_digit_en_fa(fileutils.SHARED_PREFS_OBJECT['mesghalDownrate'])}\n" \
            f"\n<b>Time</b>\n" \
            f"{'periodic time(minute):'}  {fileutils.SHARED_PREFS_OBJECT['periodicTime']}\n" \
            f"\n<b>Update</b>\n" \
            f"{'only change:'}  {'on' if fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] else 'off'}\n"

    print(prefs)
    bot.reply_to(message, prefs, parse_mode='HTML')


@bot.message_handler(commands=['setmesghaluprate'])
def set_mesghal_uprate_request(message):
    msg = bot.reply_to(message, f"Please enter the integer value of the up rate for mesghal")
    bot.register_next_step_handler(msg, set_mesghal_uprate)


@bot.message_handler(commands=['setmesghaldownrate'])
def set_mesghal_downrate_request(message):
    msg = bot.reply_to(message, f"Please enter the integer value of the down rate for mesghal")
    bot.register_next_step_handler(msg, set_mesghal_downrate)


@bot.message_handler(commands=['setperiodictime'])
def set_periodic_time_request(message):
    msg = bot.reply_to(message, f"Please enter the new value for periodic time."
                                f"\nIt must be a number between {constants.PERIODIC_TIME_MIN} to "
                                f"{constants.PERIODIC_TIME_MAX}.\n"
                                f"0 means it will turn off")
    bot.register_next_step_handler(msg, set_periodic_time)


@bot.message_handler(commands=['setonlychangesfetch'])
def set_only_changes_fetch_request(message):
    bot.send_message(message.chat.id, "Do you want to have fetch only on changes?",
                     reply_markup=gen_markup_only_changes_fetch())


@bot.callback_query_handler(func=lambda is_only_change: True)
def callback_query_is_only_change(is_only_change):
    if is_only_change.data == 'cb_on':
        fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] = True
        bot.answer_callback_query(is_only_change.id, "You chose On.")
    elif is_only_change.data == 'cb_off':
        fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] = False
        bot.answer_callback_query(is_only_change.id, "You chose Off.")

    bot.delete_message(chat_id=is_only_change.message.chat.id, message_id=is_only_change.message.id)
    updateSharedPrefsFile()


if __name__ == "__main__":
    fileutils.load_prefs_from_disk()

    job_periodic_fetch = scheduler.add_job(
        func=fetch_command,
        trigger='interval',
        minutes=fileutils.SHARED_PREFS_OBJECT['periodicTime'],
        kwargs={'message': {}})
    scheduler.start()

    print('bot polling')
    bot.polling(none_stop=True)
