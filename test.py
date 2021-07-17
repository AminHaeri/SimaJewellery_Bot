import os

import requests
import telebot
import yfinance as yf
from telebot import types
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode=None)

markup = types.ReplyKeyboardMarkup(row_width=2)
itembtn1 = types.KeyboardButton('a')
itembtn2 = types.KeyboardButton('v')
itembtn3 = types.KeyboardButton('d')
markup.add(itembtn1, itembtn2, itembtn3)


def gen_markup():
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row_width = 2
    inline_markup.add(types.InlineKeyboardButton("Yes", callback_data="cb_yes"),
                      types.InlineKeyboardButton("No", callback_data="cb_no"))
    return inline_markup


@bot.message_handler(commands=['test'])
def test_markup(message):
    bot.send_message(message.chat.id, "Yes/no?", reply_markup=gen_markup())
    # bot.send_message(message.chat.id, "Choose one letter:", reply_markup=markup)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    response = requests.get('https://call16.tgju.org/ajax.json?2021071622-20210716230060-LkhfJvGIxwKp8Wa6k9Ti')
    json_response = response.json()
    for key, value in json_response.items():
        print(f'{key} : {value}')
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(commands=['wsb'])
def get_stocks(message):
    response = ""
    stocks = ["gme", "amc", "nok"]
    stock_data = []
    for stock in stocks:
        data = yf.download(tickers=stock, period='2d', interval='1d')
        data = data.reset_index()
        response += f"----{stock}----\n"
        stock_data.append([stock])
        columns = ['stock']
        for index, row in data.iterrows():
            stock_position = len(stock_data) - 1
            price = round(row['Close'], 2)
            format_date = row['Date'].strftime('%m/%d')
            response += f"{format_date}: {price}\n"
            stock_data[stock_position].append(price)
            columns.append(format_date)
        print()

        response = f"{columns[0] : <10}{columns[1] : ^10}{columns[2] : >10}\n"
        for row in stock_data:
            response += f"{row[0] : <10}{row[1] : ^10}{row[2] : >10}\n"
        response += "\nStock Data"
        print(response)
        bot.send_message(message.chat.id, response)


bot.polling(none_stop=True)
