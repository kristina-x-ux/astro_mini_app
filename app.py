import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Введи свои данные и я сделаю разбор 🔮")

@bot.message_handler(func=lambda message: True)
def handle(message):
    bot.send_message(message.chat.id, "Твой астрологический анализ готов ✨")

bot.polling()
