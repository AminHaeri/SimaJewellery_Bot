import os

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import constants
import fileutils
import networkutils
import security
from mathutils import *

load_dotenv()
API_KEY = os.getenv('API_KEY')

# telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(API_KEY, parse_mode=None)

scheduler = BackgroundScheduler()
job_periodic_fetch = None
commands = ['show', 'fetch', 'getprefs', 'setmesghalsellrate', 'setmesghalBuyRate',
            'setperiodictime', 'setonlychangesfetch']


def decor_reply_help(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

        arg_message = args[0] if len(args) > 0 else kwargs['message']
        message = None
        if type(arg_message) is telebot.types.Message:
            message = arg_message
        elif type(arg_message) is telebot.types.CallbackQuery:
            message = arg_message.message

        if message.chat is not None:
            bot.send_message(message.chat.id, f"OK. to get the list of commands /help")

    return wrapper


def decor_authorization(func):
    def wrapper(*args, **kwargs):
        arg_message: telebot.types.Message = args[0] if len(args) > 0 else kwargs['message']
        if security.is_user_authorized(arg_message):
            func(*args, **kwargs)
        else:
            error_msg = f"Hello @{arg_message.from_user.username}\n" \
                        f"You are not <b>authorized</b> to use this bot.\n\nSorry!!!"
            bot.reply_to(arg_message, error_msg, parse_mode='HTML')

    return wrapper


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
                   f"<b>{constants.PERIODIC_TIME_MIN}</b> and <b>{constants.PERIODIC_TIME_MAX}</b> or <b>0</b>."

    time = message.text
    if not time.isdigit():
        bot.reply_to(message, text=error_string, parse_mode='HTML')
        return False

    time = int(time)
    if time != 0 and (time < constants.PERIODIC_TIME_MIN or time > constants.PERIODIC_TIME_MAX):
        bot.reply_to(message, text=error_string, parse_mode='HTML')
        return False

    return True


def update_sharedprefs_file():
    fileutils.write_shared_prefs(fileutils.SHARED_PREFS_OBJECT)


@decor_reply_help
def set_mesghal_sell_rate(message):
    if validate_rate(message):
        fileutils.SHARED_PREFS_OBJECT['mesghalSellRate'] = int(message.text)
        msg = f"Mesghal sell rate successfully changed to: <b>{fileutils.SHARED_PREFS_OBJECT['mesghalSellRate']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')

    update_sharedprefs_file()


@decor_reply_help
def set_mesghal_buy_rate(message):
    if validate_rate(message):
        fileutils.SHARED_PREFS_OBJECT['mesghalBuyRate'] = int(message.text)
        msg = f"Mesghal buy rate successfully changed to: <b>{fileutils.SHARED_PREFS_OBJECT['mesghalBuyRate']}</b>"
        bot.reply_to(message, msg, parse_mode='HTML')

        update_sharedprefs_file()


@decor_reply_help
def set_periodic_time(message):
    if validate_periodic_time(message):
        new_time = int(message.text)
        fileutils.SHARED_PREFS_OBJECT['periodicTime'] = new_time
        msg = ''
        if new_time >= constants.PERIODIC_TIME_MIN:
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

    user = telebot.types.User(0, True, constants.BOT_USERNAME, username=constants.BOT_USERNAME)
    msg = telebot.types.Message(0, user, None, None, None, [], None)
    job_periodic_fetch = scheduler.add_job(
        func=fetch_command,
        trigger='interval',
        seconds=fileutils.SHARED_PREFS_OBJECT['periodicTime'],
        args={},
        kwargs={'message': msg})


def modify_periodic_job_fetch():
    if job_periodic_fetch is None:
        add_periodic_job_fetch()
    else:
        scheduler.reschedule_job(
            job_id=job_periodic_fetch.id,
            trigger='interval',
            seconds=fileutils.SHARED_PREFS_OBJECT['periodicTime'])


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


# @bot.middleware_handler(update_types=['message'])
# def authorization(bot_instance, message: telebot.types.Message):
#     error_msg = f"Hello @{message.from_user.username}\nYou are not authorized to use this bot.\n\nSorry !"
#     bot.delete_message(message.chat.id, message.id)
#     bot.send_message(message.chat.id, error_msg)


@bot.message_handler(commands=['help'])
@decor_authorization
def help_command(message):
    help_string = f"List of command available:\n\n" + fileutils.read_help()
    bot.reply_to(message, text=help_string, parse_mode='HTML')


@bot.message_handler(commands=['show'])
@decor_authorization
@decor_reply_help
def show_command(message):
    mesghal_object = networkutils.extract_mesghal(networkutils.fetch_finance_data())
    response_string = mesghal_object.get_html()
    print(response_string)

    bot.reply_to(message, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['fetch'])
@decor_authorization
@decor_reply_help
def fetch_command(message):
    print(message)
    mesghal_object = networkutils.extract_mesghal(networkutils.fetch_finance_data())
    if networkutils.check_fetch_updated(mesghal_object):
        response_string = mesghal_object.get_mesghal_html(False)
        print(response_string)
        bot.send_message(chat_id=constants.CHANNEL_ID, text=response_string, parse_mode='HTML')

        if type(message) is telebot.types.Message and message.chat is not None:
            bot.reply_to(message, text=response_string, parse_mode='HTML')
    else:
        response_string = f"There is no changes to last data." \
                          f"\nIf you want to see the data anyway please turn off the <b>only change fetch</b>."
        print(response_string)

        if type(message) is telebot.types.Message:
            bot.reply_to(message, text=response_string, parse_mode='HTML')


@bot.message_handler(commands=['getprefs'])
@decor_authorization
@decor_reply_help
def get_prefs(message):
    prefs = f"<b>Mesghal</b>\n" \
            f"{'Sell Rate (Rial):'}  " \
            f"{convert_digit_en_fa(convert_int_currency(fileutils.SHARED_PREFS_OBJECT['mesghalSellRate']))}\n" \
            f"{'Buy Rate (Rial):'}  " \
            f"{convert_digit_en_fa(convert_int_currency(fileutils.SHARED_PREFS_OBJECT['mesghalBuyRate']))}\n" \
            f"\n<b>Time</b>\n" \
            f"{'Periodic Time(Seconds):'}  {fileutils.SHARED_PREFS_OBJECT['periodicTime']}\n" \
            f"\n<b>Update</b>\n" \
            f"{'Only Change:'}  {'on' if fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] else 'off'}\n"\

    print(prefs)
    bot.reply_to(message, prefs, parse_mode='HTML')


@bot.message_handler(commands=['setmesghalsellrate'])
@decor_authorization
def set_mesghal_sell_rate_request(message):
    response_string = f"Current sell rate: <b>{fileutils.SHARED_PREFS_OBJECT['mesghalSellRate']}</b>\n" \
                      f"Please enter <b>positive number</b>"
    msg = bot.reply_to(message, text=response_string, parse_mode='HTML')
    bot.register_next_step_handler(msg, set_mesghal_sell_rate)


@bot.message_handler(commands=['setmesghalbuyrate'])
@decor_authorization
def set_mesghal_buy_rate_request(message):
    response_string = f"Current buy rate: <b>{fileutils.SHARED_PREFS_OBJECT['mesghalBuyRate']}</b>\n" \
                      f"Please enter <b>positive number</b>"
    msg = bot.reply_to(message, text=response_string, parse_mode='HTML')
    bot.register_next_step_handler(msg, set_mesghal_buy_rate)


@bot.message_handler(commands=['setperiodictime'])
@decor_authorization
def set_periodic_time_request(message):
    msg = bot.reply_to(message,
                       text=f"Current periodic time: <b>{fileutils.SHARED_PREFS_OBJECT['periodicTime']}</b>."
                            f"\nPlease enter number between "
                            f"<b>{constants.PERIODIC_TIME_MIN}</b> to "
                            f"<b>{constants.PERIODIC_TIME_MAX}</b>.\n\n"
                            f"<b>0</b> will turn it off.",
                       parse_mode='HTML')
    bot.register_next_step_handler(msg, set_periodic_time)


@bot.message_handler(commands=['setonlychangesfetch'])
@decor_authorization
def set_only_changes_fetch_request(message):
    bot.send_message(message.chat.id, "Do you want to have fetch only on changes?",
                     reply_markup=gen_markup_only_changes_fetch())


@bot.callback_query_handler(func=lambda is_only_change: True)
@decor_reply_help
def callback_query_is_only_change(is_only_change):
    if is_only_change.data == 'cb_on':
        fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] = True
        bot.answer_callback_query(is_only_change.id, "You chose On.")
    elif is_only_change.data == 'cb_off':
        fileutils.SHARED_PREFS_OBJECT['updateOnlyChanges'] = False
        bot.answer_callback_query(is_only_change.id, "You chose Off.")

    bot.delete_message(chat_id=is_only_change.message.chat.id, message_id=is_only_change.message.id)
    update_sharedprefs_file()


fileutils.load_prefs_from_disk()

if fileutils.SHARED_PREFS_OBJECT['periodicTime'] > 0:
    add_periodic_job_fetch()

scheduler.start()

print('bot polling')
bot.polling(none_stop=True)
