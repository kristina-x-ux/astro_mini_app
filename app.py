from flask import Flask, render_template, request, jsonify
import telebot
import os
from threading import Thread
import time

from astro_engine import calculate_chart, search_places

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = telebot.TeleBot(TOKEN) if TOKEN else None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search_place", methods=["GET"])
def search_place():
    query = request.args.get("q", "").strip()

    try:
        places = search_places(query)
        return jsonify({"places": places})
    except Exception as e:
        return jsonify({"places": [], "error": str(e)})


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}

    date = data.get("date", "")
    time_birth = data.get("time", "")
    city = data.get("city", "")
    mode = data.get("mode", "client")

    lat = data.get("lat")
    lon = data.get("lon")
    display_name = data.get("display_name")

    try:
        chart = calculate_chart(
            date_str=date,
            time_str=time_birth,
            city=city,
            lat=lat,
            lon=lon,
            display_name=display_name
        )

        return jsonify({
            "success": True,
            "mode": mode,
            "chart": chart
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


if bot:
    @bot.message_handler(commands=["start"])
    def start(message):
        markup = telebot.types.InlineKeyboardMarkup()

        button = telebot.types.InlineKeyboardButton(
            text="🌐 Перейти в веб-приложение",
            web_app=telebot.types.WebAppInfo(url=WEBAPP_URL)
        )

        markup.add(button)

        text = """
✨ Добро пожаловать в AstroEngine

AstroEngine — система джйотиш-анализа,
которая объединяет понятный разбор для пользователя и профессиональный инструмент для астрологов.

Сервис рассчитывает натальную карту и показывает:
— структуру личности
— сильные и слабые планеты
— ключевые сценарии реализации

Для астрологов доступен расширенный режим с детальными расчётами и параметрами карты.

Введите данные рождения, чтобы получить персональный анализ.

👇 Перейти в веб-приложение
"""

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=markup
        )


def run_bot():
    if not bot:
        return

    time.sleep(10)
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)


if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=80)
