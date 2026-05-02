from flask import Flask, render_template, request, jsonify
import telebot
import os

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- WEB ЧАСТЬ ---

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()

    date = data.get("date")
    time = data.get("time")
    city = data.get("city")

    # пока тестовый ответ
    result = f"Дата: {date}\nВремя: {time}\nГород: {city}\n\n✨ Анализ скоро будет"

    return jsonify({"result": result})


# --- БОТ ---

@bot.message_handler(commands=['start'])
def start(message):
    webapp_url = os.getenv("WEBAPP_URL")

    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        text="🔮 Открыть разбор",
        web_app=telebot.types.WebAppInfo(webapp_url)
    )
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Открой приложение и получи анализ",
        reply_markup=markup
    )


# --- ЗАПУСК ---

if __name__ == "__main__":
    from threading import Thread

    def run_bot():
        bot.infinity_polling()

    Thread(target=run_bot).start()

    app.run(host="0.0.0.0", port=80)
