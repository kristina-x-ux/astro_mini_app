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

        result = f"""
✨ ДЖЙОТИШ-РАСЧЁТ

📍 Город: {chart["city"]}
🌍 Широта: {round(chart["lat"], 4)}
🌍 Долгота: {round(chart["lon"], 4)}
🕒 Часовой пояс: {chart["timezone"]}

🕰 UTC:
{chart["utc"]}

📌 Julian Day:
{round(chart["jd"], 5)}

📌 Айанамша Лахири:
{round(chart["ayanamsha"], 4)}°

━━━━━━━━━━━━━━

🌅 ЛАГНА:
{chart["lagna_full_text"]}
Накшатра: {chart["lagna_nakshatra"]}, пада {chart["lagna_pada"]}

━━━━━━━━━━━━━━

🏠 ДОМА:

"""

        for house_num, house_data in chart["houses"].items():
            result += f"{house_num} дом — {house_data['sign']}, управитель: {house_data['lord']}\n"

        result += f"""

━━━━━━━━━━━━━━

🌙 ЛУНА:
{chart["moon_full_text"]}
Накшатра: {chart["moon_nakshatra"]}, пада {chart["moon_pada"]}
Дом: {chart["moon_house"]}

━━━━━━━━━━━━━━

🪐 ПЛАНЕТЫ:

"""

        for planet, info in chart["planets"].items():
            result += f"""
{planet}: {info["full_text"]}
Дом: {info["house"]}
Накшатра: {info["nakshatra"]}, пада {info["pada"]}
"""

        result += """

━━━━━━━━━━━━━━

🔮 БАЗОВЫЙ ВЫВОД:

Это уже профессиональный джйотиш-расчёт:
— сидерический зодиак
— айанамша Лахири
— лагна
— дома по системе знак = дом
— управители домов
— планеты в домах
— накшатры и пады

Следующий уровень:
— аспекты Парашары
— Чаракараки
— Вимшоттари Даша
— бесплатный и платный разбор
"""

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        result = f"Ошибка расчёта:\n{str(e)}"

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
        "✨ Добро пожаловать в «Звёздный Код»\n\nНажми кнопку ниже и получи свой разбор:",
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
