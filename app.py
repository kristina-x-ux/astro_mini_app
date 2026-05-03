from flask import Flask, render_template, request, jsonify
import telebot
import os
from threading import Thread
from datetime import datetime

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
        birth_date = datetime.strptime(date, "%Y-%m-%d")
        day = birth_date.day
        month = birth_date.month
        year = birth_date.year

        life_code = sum(int(x) for x in f"{day}{month}{year}")
        while life_code > 9:
            life_code = sum(int(x) for x in str(life_code))

        if life_code == 1:
            archetype = "Лидер, инициатор, человек сильной воли"
            advice = "Важно не бояться проявляться и брать ответственность."
        elif life_code == 2:
            archetype = "Дипломат, чувствительный проводник, человек партнёрства"
            advice = "Важно учиться слышать себя, а не только других."
        elif life_code == 3:
            archetype = "Творец, человек слова, красоты и вдохновения"
            advice = "Важно раскрывать голос, творчество и личный стиль."
        elif life_code == 4:
            archetype = "Строитель, системный человек, опора для других"
            advice = "Важно не застревать в контроле и разрешать себе гибкость."
        elif life_code == 5:
            archetype = "Исследователь, человек перемен, свободы и движения"
            advice = "Важно направлять энергию в развитие, а не в хаос."
        elif life_code == 6:
            archetype = "Гармонизатор, человек любви, семьи и красоты"
            advice = "Важно не тащить всё на себе и сохранять личные границы."
        elif life_code == 7:
            archetype = "Мудрец, аналитик, человек глубины и внутреннего знания"
            advice = "Важно доверять интуиции, но не уходить в изоляцию."
        elif life_code == 8:
            archetype = "Стратег, человек силы, денег и управления"
            advice = "Важно выстраивать зрелое отношение к власти и ресурсам."
        else:
            archetype = "Проводник, человек завершения, смысла и большой души"
            advice = "Важно отпускать старое и не бояться нового этапа."

        result = f"""
✨ ТВОЙ ЗВЁЗДНЫЙ КОД

📅 Дата рождения: {date}
⏰ Время рождения: {time}
📍 Город рождения: {city}

🔢 Код судьбы: {life_code}

🌟 Твой архетип:
{archetype}

🧭 Главная задача:
{advice}

💫 Краткий вывод:
У тебя сильная внутренняя программа, связанная с раскрытием личного пути, талантов и предназначения. Важные события в жизни часто приходят не случайно, а через внутренние переломные моменты, когда нужно сделать выбор в пользу себя.

🔮 Это базовый мини-разбор. Для точного астрологического анализа нужны полные расчёты карты рождения.
"""

    except Exception:
        result = "Ошибка расчёта. Проверь дату, время и город."

    return jsonify({"result": result})


@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()

    button = telebot.types.InlineKeyboardButton(
        text="🔮 Открыть разбор",
        web_app=telebot.types.WebAppInfo(url=WEBAPP_URL)
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
