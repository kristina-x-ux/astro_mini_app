from flask import Flask, render_template, request, jsonify
import telebot
import os
from threading import Thread

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = telebot.TeleBot(TOKEN)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()

    date = data.get("date")
    time = data.get("time")
    city = data.get("city")

    result = f"Дата: {date}\nВремя: {time}\nГород: {city}\n\n✨ Анализ скоро будет"

    return jsonify({"result": result})


@bot.message_handler(commands=["start"])
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


def run_bot():
    bot.infinity_polling()


if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=80)
