import os
from dotenv import load_dotenv
import telebot
import yfinance as yf

load_dotenv()

API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY, parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
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
            # print('sp: '+ str(stock_position))
            # print('\nrow:')
            # print(row)
            # print('\nclose:')
            # print(row['Close'])
            # print()
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


bot.polling()
