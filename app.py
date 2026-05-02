import os
from flask import Flask, render_template
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

WEBAPP_URL = os.getenv("WEBAPP_URL")

@app.route("/")
def index():
    return render_template("index.html")

@bot.message_handler(commands=["start"])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    webAppButton = KeyboardButton(
        text="🔮 Открыть Звёздный Код",
        web_app=WebAppInfo(WEBAPP_URL)
    )

    markup.add(webAppButton)

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в Звёздный Код ✨",
        reply_markup=markup
    )

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
