import os

import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import parser
from dotenv import load_dotenv

import constants as consts
from mathutils import *

API_URL = 'https://call16.tgju.org/ajax.json?2021071622-20210716230060-LkhfJvGIxwKp8Wa6k9Ti'
load_dotenv()

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode=None)
scheduler = BackgroundScheduler()

periodic_time = consts.PERIODIC_TIME
job_periodic_fetch = None

commands = ['fetch', 'testfetch', 'getprefs', 'setmesghaluprate', 'setmesghaldownrate',
            'setperiodictime', 'setonlychangesfetch']
mesghal = {
    'uprate': consts.MESGHAL_UPRATE,
    'downrate': consts.MESGHAL_DOWNRATE
}
update_only_changes = True
last_mesghal_object = None


def fetch_finance_data():
    response = requests.get(API_URL)
    json_response = response.json()
    return json_response


def fetch_string():
    return string_mesghal(extract_mesghal(fetch_finance_data()))


def check_fetch_updated():
    global last_mesghal_object
    mesghal_object = extract_mesghal(fetch_finance_data())
    if update_only_changes:
        if last_mesghal_object is not None and last_mesghal_object['p'] == mesghal_object['p']:
            return False

        last_mesghal_object = mesghal_object

    return True


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
        msg = f"Mesghal up rate successfully changed to <b>{mesghal['uprate']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')


def set_mesghal_downrate(message):
    if validate_rate(message, set_mesghal_downrate):
        mesghal['downrate'] = int(message.text)
        msg = f"Mesghal down rate successfully changed to <b>{mesghal['downrate']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')


def set_periodic_time(message):
    if validate_periodic_time(message, set_periodic_time):
        modify_periodic_job_fetch(int(message.text))
        msg = f"Periodic time successfully changed to <b>{periodic_time}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')


def modify_periodic_job_fetch(new_time):
    global periodic_time
    periodic_time = new_time
    scheduler.reschedule_job(job_id=job_periodic_fetch.id, trigger='interval', minutes=periodic_time)

def gen_markup_only_changes_fetch():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Yes', callback_data='cb_yes'), InlineKeyboardButton('No', callback_data='cb_no'))
    return markup


####################################### Telegram Bot Message Handlers #######################################
@bot.message_handler(commands=['fetch'])
def fetch_command(message):
    if check_fetch_updated():
        response_string = fetch_string()
        print(response_string)
        bot.send_message(chat_id=consts.CHANNEL_ID, text=response_string, parse_mode='HTML')
    else:
        print(f"There is no changes to last prices")


@bot.message_handler(commands=['testfetch'])
def test_fetch_command(message):
    if check_fetch_updated():
        response_string = fetch_string()
        bot.reply_to(message, text=response_string, parse_mode='HTML')
    else:
        bot.reply_to(message, f"There is no changes to last prices")


@bot.message_handler(commands=['getprefs'])
def get_prefs(message):
    prefs = f"<b>Mesghal</b>\n" \
            f"{'uprate(rial):' : <30}{convert_digit_en_fa(mesghal['uprate']) : ^20}\n" \
            f"{'downrate(rial):' : <30}{convert_digit_en_fa(mesghal['downrate']) : ^20}\n" \
            f"\n<b>Time</b>\n" \
            f"{'periodic time(minute):' : <30}{convert_digit_en_fa(periodic_time) : ^20}\n" \
            f"\n<b>Update</b>\n" \
            f"{'only change:' : <30}{str(update_only_changes) : ^20}\n"

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
                                f"\nIt must be a number between {consts.PERIODIC_TIME_MIN} to "
                                f"{consts.PERIODIC_TIME_MAX}.\n"
                                f"0 means it will turn off")
    bot.register_next_step_handler(msg, set_periodic_time)


@bot.message_handler(commands=['setonlychangesfetch'])
def set_only_changes_fetch_request(message):
    bot.send_message(message.chat.id, "Do you want to have fetch only on changes?",
                     reply_markup=gen_markup_only_changes_fetch())


@bot.callback_query_handler(func=lambda is_only_change: True)
def callback_query_is_only_change(is_only_change):
    global update_only_changes
    if is_only_change.data == 'cb_yes':
        update_only_changes = True
        bot.answer_callback_query(is_only_change.id, "You chose Yes.")
    elif is_only_change.data == 'cb_no':
        update_only_changes = False
        bot.answer_callback_query(is_only_change.id, "The chose No.")

    bot.delete_message(chat_id=is_only_change.message.chat.id, message_id=is_only_change.message.id)


if __name__ == "__main__":
    job_periodic_fetch = \
        scheduler.add_job(func=fetch_command, trigger='interval', minutes=periodic_time, kwargs={'message': {}})
    scheduler.start()

    print('bot polling')
    bot.polling(none_stop=True)
