import os
import threading

from flask import Flask, render_template, request, jsonify
from astro_engine import calculate_chart, search_places

try:
    import telebot
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
except Exception:
    telebot = None


app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

bot = None

if BOT_TOKEN and telebot:
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "success": True,
        "status": "ok",
        "bot_enabled": bool(bot),
        "webapp_url": WEBAPP_URL
    })


@app.route("/search_place")
def search_place():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"success": True, "places": []})

    try:
        places = search_places(query)
        return jsonify({"success": True, "places": places})
    except Exception as e:
        return jsonify({
            "success": False,
            "places": [],
            "error": str(e)
        })


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json(force=True)

        chart = calculate_chart(
            date_str=data.get("date", "").strip(),
            time_str=data.get("time", "").strip(),
            city=data.get("city", "").strip(),
            lat=data.get("lat"),
            lon=data.get("lon"),
            display_name=data.get("display_name")
        )

        chart["mode"] = data.get("mode", "client")

        return jsonify({
            "success": True,
            "chart": chart
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/calculate_transit", methods=["POST"])
def calculate_transit():
    try:
        data = request.get_json(force=True)

        transit_chart = calculate_chart(
            date_str=data.get("date", "").strip(),
            time_str=data.get("time", "").strip(),
            city=data.get("city", "").strip(),
            lat=data.get("lat"),
            lon=data.get("lon"),
            display_name=data.get("display_name")
        )

        return jsonify({
            "success": True,
            "transit": transit_chart
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/rectification", methods=["POST"])
def rectification():
    try:
        data = request.get_json(force=True)

        rectified_chart = calculate_chart(
            date_str=data.get("date", "").strip(),
            time_str=data.get("time", "").strip(),
            city=data.get("city", "").strip(),
            lat=data.get("lat"),
            lon=data.get("lon"),
            display_name=data.get("display_name")
        )

        return jsonify({
            "success": True,
            "chart": rectified_chart
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


def make_start_keyboard():
    keyboard = InlineKeyboardMarkup()

    if WEBAPP_URL:
        keyboard.add(
            InlineKeyboardButton(
                text="✨ Открыть AstroEngine",
                web_app=WebAppInfo(WEBAPP_URL)
            )
        )
    else:
        keyboard.add(
            InlineKeyboardButton(
                text="⚠️ WEBAPP_URL не задан",
                callback_data="no_webapp_url"
            )
        )

    return keyboard


if bot:
    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(
            message.chat.id,
            "✨ Добро пожаловать в <b>AstroEngine</b>\n\n"
            "Откройте мини-приложение для джйотиш-расчёта.",
            reply_markup=make_start_keyboard()
        )


    @bot.callback_query_handler(func=lambda call: call.data == "no_webapp_url")
    def no_webapp_url(call):
        bot.answer_callback_query(
            call.id,
            "В Amvera нужно добавить переменную WEBAPP_URL со ссылкой на сайт.",
            show_alert=True
        )


def run_bot():
    if not bot:
        print("Telegram bot is disabled: BOT_TOKEN missing or telebot not installed")
        return

    print("Telegram bot polling started")
    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )


if __name__ == "__main__":
    if bot:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=False,
        use_reloader=False
          )
