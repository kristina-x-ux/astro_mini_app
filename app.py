import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()

    button = telebot.types.InlineKeyboardButton(
        text="🔮 Открыть разбор",
        url=WEBAPP_URL
    )

    markup.add(button)

    bot.send_message(
        message.chat.id,
        "✨ Добро пожаловать в «Звёздный код»\n\nНажми кнопку ниже и получи свой разбор:",
        reply_markup=markup
    )


bot.infinity_polling()
