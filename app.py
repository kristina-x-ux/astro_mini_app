from flask import Flask, render_template, request, jsonify
import telebot
import os
from threading import Thread
import time

from astro_engine import calculate_chart, search_places
from database import (
    init_db,
    save_chart,
    get_saved_charts,
    get_saved_chart,
    delete_saved_chart
)

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
        return jsonify({"success": True, "places": places})
    except Exception as e:
        return jsonify({"success": False, "places": [], "error": str(e)})


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


@app.route("/save_chart", methods=["POST"])
def save_chart_route():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    birth_date = data.get("birth_date", "").strip()
    birth_time = data.get("birth_time", "").strip()
    place_name = data.get("place_name", "").strip()
    lat = data.get("lat")
    lon = data.get("lon")
    timezone = data.get("timezone", "")
    comment = data.get("comment", "")

    telegram_user_id = data.get("telegram_user_id")

    if not name:
        return jsonify({"success": False, "error": "Введите имя карты"})

    if not birth_date or not birth_time or not place_name:
        return jsonify({"success": False, "error": "Не хватает данных для сохранения"})

    try:
        saved = save_chart(
            telegram_user_id=telegram_user_id,
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            place_name=place_name,
            lat=lat,
            lon=lon,
            timezone=timezone,
            comment=comment
        )

        return jsonify({"success": True, "chart": saved})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/saved_charts", methods=["GET"])
def saved_charts_route():
    telegram_user_id = request.args.get("telegram_user_id")

    try:
        charts = get_saved_charts(telegram_user_id)
        return jsonify({"success": True, "charts": charts})

    except Exception as e:
        return jsonify({"success": False, "charts": [], "error": str(e)})


@app.route("/open_chart/<int:chart_id>", methods=["GET"])
def open_chart_route(chart_id):
    try:
        saved = get_saved_chart(chart_id)

        if not saved:
            return jsonify({"success": False, "error": "Карта не найдена"})

        chart = calculate_chart(
            date_str=saved["birth_date"],
            time_str=saved["birth_time"],
            city=saved["place_name"],
            lat=saved["lat"],
            lon=saved["lon"],
            display_name=saved["place_name"]
        )

        return jsonify({
            "success": True,
            "saved": saved,
            "chart": chart
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/delete_chart/<int:chart_id>", methods=["DELETE"])
def delete_chart_route(chart_id):
    try:
        deleted = delete_saved_chart(chart_id)

        if not deleted:
            return jsonify({"success": False, "error": "Карта не найдена"})

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


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

        bot.send_message(message.chat.id, text, reply_markup=markup)


def run_bot():
    if not bot:
        return

    time.sleep(10)
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)


if __name__ == "__main__":
    try:
        init_db()
        print("Database initialized")
    except Exception as e:
        print(f"Database init error: {e}")

    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=80)
