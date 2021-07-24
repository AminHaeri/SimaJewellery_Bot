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

commands = ['get', 'fetch', 'getprefs', 'setmesghaluprate', 'setmesghaldownrate',
            'setperiodictime', 'setonlychangesfetch']
last_mesghal_object = None


def decor_help_reply(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        message = None
        if len(args) > 0:
            arg_message = args[0]
            print(arg_message)
            if type(arg_message) is telebot.types.Message:
                message = arg_message
            elif type(arg_message) is telebot.types.CallbackQuery:
                message = arg_message.message
            bot.send_message(message.chat.id, f"OK. to get the list of commands /help")

    return wrapper


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

    raw = f"{constants.EMOJI_MONEY_BAG} #{constants.MESGHAL_RAW_FA}: " \
          f"<b>{convert_digit_en_fa(currency['p'])}</b>\n\n"

    rates = f"{constants.EMOJI_BLACK_SPADE} #{constants.MESGHAL_BUY_FA}: " \
            f"<b>{convert_digit_en_fa(currency['downrate'])}</b>\n\n" \
            f"{constants.EMOJI_BLACK_CLUB} #{constants.MESGHAL_SELL_FA}: " \
            f"<b>{convert_digit_en_fa(currency['uprate'])}</b>\n\n\n\n"

    time = f"{constants.EMOJI_CLOCK_FACE_TWO} <b>{constants.MESGHAL_TIME_FA}:</b> " \
           f"{get_jalili_format(mesghal_object['time'], True, True)}\n\n" \
           f"{constants.EMPTY_TRICK}"

    return title + (raw if is_raw else '') + rates + time


def validate_rate(message):
    rate = message.text
    if not rate.isdigit():
        bot.reply_to(message, text=f"Mesghal rate should a be a <b>positive number</b>.", parse_mode='HTML')
        return False

    rate = int(rate)
    if rate < 0:
        bot.reply_to(message, text=f"Mesghal rate should a be a <b>positive number</b>.", parse_mode='HTML')
        return False

    return True


def validate_periodic_time(message):
    error_string = f"Periodic time should a be a number between " \
                   f"<b>{constants.PERIODIC_TIME_MIN}</b> and <b>{constants.PERIODIC_TIME_MAX}</b>."

    time = message.text
    if not time.isdigit():
        bot.reply_to(message, text=error_string, parse_mode='HTML')
        return False

    time = int(time)
    if time < constants.PERIODIC_TIME_MIN or time > constants.PERIODIC_TIME_MAX:
        bot.reply_to(message, text=error_string, parse_mode='HTML')
        return False

    return True


def update_sharedprefs_file():
    fileutils.write_shared_prefs(fileutils.SHARED_PREFS_OBJECT)


@decor_help_reply
def set_mesghal_uprate(message):
    if validate_rate(message):
        fileutils.SHARED_PREFS_OBJECT['mesghalUprate'] = int(message.text)
        msg = f"Mesghal up rate successfully changed to: <b>{fileutils.SHARED_PREFS_OBJECT['mesghalUprate']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')

    update_sharedprefs_file()


@decor_help_reply
def set_mesghal_downrate(message):
    if validate_rate(message):
        fileutils.SHARED_PREFS_OBJECT['mesghalDownrate'] = int(message.text)
        msg = f"Mesghal down rate successfully changed to: <b>{fileutils.SHARED_PREFS_OBJECT['mesghalDownrate']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')

        update_sharedprefs_file()


@decor_help_reply
def set_periodic_time(message):
    if validate_periodic_time(message):
        new_time = int(message.text)
        fileutils.SHARED_PREFS_OBJECT['periodicTime'] = new_time
        msg = ''
        if new_time > 0:
            modify_periodic_job_fetch()
            msg = f"Periodic time successfully changed to: <b>{fileutils.SHARED_PREFS_OBJECT['periodicTime']}</b>"
        elif new_time == 0:
            remove_periodic_job_fetch()
            msg = f"Periodic time has successfully <b>removed</b>."

        bot.reply_to(message, msg, parse_mode='HTML')
        update_sharedprefs_file()


def add_periodic_job_fetch():
    global job_periodic_fetch

    if job_periodic_fetch is not None:
        return

    job_periodic_fetch = scheduler.add_job(
        func=fetch_command,
        trigger='interval',
        minutes=fileutils.SHARED_PREFS_OBJECT['periodicTime'],
        args={},
        kwargs={'message': {}})


def modify_periodic_job_fetch():
    if job_periodic_fetch is None:
        add_periodic_job_fetch()
    else:
        scheduler.reschedule_job(
            job_id=job_periodic_fetch.id,
            trigger='interval',
            minutes=fileutils.SHARED_PREFS_OBJECT['periodicTime'])


def remove_periodic_job_fetch():
    global job_periodic_fetch

    if job_periodic_fetch is None:
        return

    scheduler.remove_job(job_id=job_periodic_fetch.id)
    job_periodic_fetch = None


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
@decor_help_reply
def show_command(message):
    mesghal_object = extract_mesghal(fetch_finance_data())
    response_string = string_mesghal(mesghal_object, True)
    print(response_string)

    bot.reply_to(message, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['fetch'])
@decor_help_reply
def fetch_command(message):
    print(message)
    mesghal_object = extract_mesghal(fetch_finance_data())
    if check_fetch_updated(mesghal_object):
        response_string = string_mesghal(mesghal_object, False)
        print(response_string)
        bot.send_message(chat_id=constants.CHANNEL_ID, text=response_string, parse_mode='HTML')

        if type(message) is telebot.types.Message:
            bot.reply_to(message, text=response_string, parse_mode='HTML')
    else:
        response_string = f"There is no changes to last data." \
                          f"\nIf you want to see the data anyway please turn off the <b>only change fetch</b>."
        print(response_string)

        if type(message) is telebot.types.Message:
            bot.reply_to(message, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['getprefs'])
@decor_help_reply
def get_prefs(message):
    prefs = f"<b>Mesghal</b>\n" \
            f"{'uprate (rial):'}  " \
            f"{convert_digit_en_fa(convert_int_currency(fileutils.SHARED_PREFS_OBJECT['mesghalUprate']))}\n" \
            f"{'downrate (rial):'}  " \
            f"{convert_digit_en_fa(convert_int_currency(fileutils.SHARED_PREFS_OBJECT['mesghalDownrate']))}\n" \
            f"\n<b>Time</b>\n" \
            f"{'periodic time(minute):'}  {fileutils.SHARED_PREFS_OBJECT['periodicTime']}\n" \
            f"\n<b>Update</b>\n" \
            f"{'only change:'}  {'on' if fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] else 'off'}\n"

    print(prefs)
    bot.reply_to(message, prefs, parse_mode='HTML')


@bot.message_handler(commands=['setmesghaluprate'])
def set_mesghal_uprate_request(message):
    response_string = f"Current up rate: <b>{fileutils.SHARED_PREFS_OBJECT['mesghalUprate']}</b>\n" \
                      f"Please enter <b>positive number</b>"
    msg = bot.reply_to(message, text=response_string, parse_mode='HTML')
    bot.register_next_step_handler(msg, set_mesghal_uprate)


@bot.message_handler(commands=['setmesghaldownrate'])
def set_mesghal_downrate_request(message):
    response_string = f"Current down rate: <b>{fileutils.SHARED_PREFS_OBJECT['mesghalDownrate']}</b>\n" \
                      f"Please enter <b>positive number</b>"
    msg = bot.reply_to(message, text=response_string, parse_mode='HTML')
    bot.register_next_step_handler(msg, set_mesghal_downrate)


@bot.message_handler(commands=['setperiodictime'])
def set_periodic_time_request(message):
    msg = bot.reply_to(message,
                       text=f"Current periodic time: <b>{fileutils.SHARED_PREFS_OBJECT['periodicTime']}</b>."
                            f"\nPlease enter number between "
                            f"<b>{constants.PERIODIC_TIME_MIN}</b> to "
                            f"<b>{constants.PERIODIC_TIME_MAX}</b>.\n\n"
                            f"<b>{constants.PERIODIC_TIME_MIN}</b> will turn it off.",
                       parse_mode='HTML')
    bot.register_next_step_handler(msg, set_periodic_time)


@bot.message_handler(commands=['setonlychangesfetch'])
def set_only_changes_fetch_request(message):
    bot.send_message(message.chat.id, "Do you want to have fetch only on changes?",
                     reply_markup=gen_markup_only_changes_fetch())


@bot.callback_query_handler(func=lambda is_only_change: True)
@decor_help_reply
def callback_query_is_only_change(is_only_change):
    if is_only_change.data == 'cb_on':
        fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] = True
        bot.answer_callback_query(is_only_change.id, "You chose On.")
    elif is_only_change.data == 'cb_off':
        fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] = False
        bot.answer_callback_query(is_only_change.id, "You chose Off.")

    bot.delete_message(chat_id=is_only_change.message.chat.id, message_id=is_only_change.message.id)
    update_sharedprefs_file()


if __name__ == "__main__":
    fileutils.load_prefs_from_disk()

    if fileutils.SHARED_PREFS_OBJECT['periodicTime'] > 0:
        add_periodic_job_fetch()

    scheduler.start()

    print('bot polling')
    bot.polling(none_stop=True)
