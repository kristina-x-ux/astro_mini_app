from flask import Flask, render_template, request, jsonify
import telebot
import os
from threading import Thread
from astro_engine import calculate_chart

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = telebot.TeleBot(TOKEN)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}

    date = data.get("date", "")
    time = data.get("time", "")
    city = data.get("city", "")

    try:
        chart = calculate_chart(date, time, city)

        # =========================
        # 🧠 СОБИРАЕМ КАРТОЧКИ
        # =========================

        result = f"""
        <div class="card">
            <h2>✨ Джйотиш-расчёт</h2>
            <p>📍 {chart['city']}</p>
            <p>🌍 {round(chart['lat'],4)} / {round(chart['lon'],4)}</p>
            <p>🕒 {chart['timezone']}</p>
        </div>

        <div class="card">
            <h3>🌅 Лагна</h3>
            <p>{chart['lagna_full_text']}</p>
            <p>{chart['lagna_nakshatra']}, пада {chart['lagna_pada']}</p>
        </div>

        <div class="card">
            <h3>🏠 Дома</h3>
        """

        for house, info in chart["houses"].items():
            result += f"<p>{house} — {info}</p>"

        result += "</div>"

        # 🌙 ЛУНА
        result += f"""
        <div class="card">
            <h3>🌙 Луна</h3>
            <p>{chart['moon_full_text']}</p>
            <p>{chart['moon_nakshatra']}, пада {chart['moon_pada']}</p>
        </div>
        """

        # 🪐 ПЛАНЕТЫ
        result += """
        <div class="card">
            <h3>🪐 Планеты</h3>
        """

        for planet, info in chart["planets"].items():
            result += f"""
            <div class="planet">
                <b>{planet}</b><br>
                {info['full_text']}<br>
                Дом: {info['house']}<br>
                Накшатра: {info['nakshatra']}, пада {info['pada']}
            </div>
            """

        result += "</div>"

        # 💰 ПРО-БЛОК
        result += """
        <div class="card pro">
            🔒 Полный разбор:
            <ul>
                <li>Аспекты Парашары</li>
                <li>Кармические задачи</li>
                <li>Даша и периоды</li>
                <li>Отношения и деньги</li>
            </ul>
            <button class="pro-btn">Открыть полный разбор</button>
        </div>
        """

    except Exception as e:
        result = f"<div class='error'>Ошибка расчёта: {str(e)}</div>"

    return jsonify({"result": result})


# =========================
# 🤖 TELEGRAM БОТ
# =========================

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
        "✨ Добро пожаловать в «Звёздный Код»\n\nНажми кнопку ниже 👇",
        reply_markup=markup
    )


def run_bot():
    import time
    time.sleep(10)
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)


if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=80)
