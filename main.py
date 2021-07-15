import os
from dotenv import load_dotenv
import telebot

load_dotenv()

API_KEY = os.getenv('API_KEY')
print(API_KEY)

bot = telebot.TeleBot(API_KEY, parse_mode=None)
@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

bot.polling()