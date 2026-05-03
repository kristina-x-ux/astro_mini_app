from flask import Flask, render_template, request, jsonify
import telebot
import os
from threading import Thread
import time

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
    time_birth = data.get("time", "")
    city = data.get("city", "")
    mode = data.get("mode", "client")

    try:
        chart = calculate_chart(date, time_birth, city)

        result = f"""
✨ ДЖЙОТИШ-РАСЧЁТ

📍 Место рождения: {chart.get("city", city)}
🌍 Широта: {round(chart.get("lat", 0), 4)}
🌍 Долгота: {round(chart.get("lon", 0), 4)}
🕘 Часовой пояс: {chart.get("timezone", "-")}

UTC:
{chart.get("utc", "-")}

Julian Day:
{round(chart.get("jd", 0), 5)}

Айанамша Лахири:
{chart.get("ayanamsha", "-")}°

──────────────

🌅 ЛАГНА:
{chart.get("lagna", {}).get("sign", "-")} {chart.get("lagna", {}).get("degree", "-")}
Накшатра: {chart.get("lagna", {}).get("nakshatra", "-")}, пада {chart.get("lagna", {}).get("pada", "-")}

──────────────

🌙 ЛУНА:
{chart.get("moon", {}).get("sign", "-")} {chart.get("moon", {}).get("degree", "-")}
Накшатра: {chart.get("moon", {}).get("nakshatra", "-")}, пада {chart.get("moon", {}).get("pada", "-")}
Дом: {chart.get("moon", {}).get("house", "-")}

──────────────

🪐 ПЛАНЕТЫ:
"""

        planets = chart.get("planets", {})

        for planet, info in planets.items():
            result += f"""

{planet}: {info.get("sign", "-")} {info.get("degree", "-")}
Дом: {info.get("house", "-")}
Накшатра: {info.get("nakshatra", "-")}, пада {info.get("pada", "-")}
"""

        if mode == "client":
            result += """

──────────────

🌙 РЕЖИМ КЛИЕНТА:

Это базовый персональный разбор. 
Следующий этап — добавить интерпретацию сильных и слабых планет, жизненных сценариев и рекомендаций.
"""
        else:
            result += """

──────────────

🧿 РЕЖИМ АСТРОЛОГА:

Это технический режим для работы с картой.
Следующий этап — добавить управителей домов, аспекты Парашары, йоги, силу планет и варги.
"""

    except Exception as e:
        result = f"Ошибка расчёта: {str(e)}"

    return jsonify({"result": result})


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
    time.sleep(10)
    bot.remove_webhook()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)


if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=80)
