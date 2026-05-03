from flask import Flask, request, jsonify
import telebot
import os
from threading import Thread

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = telebot.TeleBot(TOKEN)


# 🔥 ТЕСТОВАЯ ГЛАВНАЯ СТРАНИЦА (без шаблонов)
@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Звёздный Код</title>
      </head>
      <body style="font-family: Arial; padding: 30px;">
        <h1>✨ Звёздный Код работает</h1>
        <p>Если ты видишь этот текст — сервер и домен работают правильно.</p>
      </body>
    </html>
    """


# 🔮 API для расчёта
@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}

    date = data.get("date", "")
    time = data.get("time", "")
    city = data.get("city", "")

    result = f"Дата: {date}\nВремя: {time}\nГород: {city}\n\n✨ Анализ скоро будет"

    return jsonify({"result": result})


# 🤖 Команда /start
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


# 🔁 Запуск бота
def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)


# 🚀 Запуск всего
if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=80)
