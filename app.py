from flask import Flask, render_template, request, jsonify
import telebot
import os

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


@app.route("/telegram_webhook", methods=["POST"])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBAPP_URL.rstrip("/") + "/telegram_webhook")
    app.run(host="0.0.0.0", port=80)
