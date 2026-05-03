from flask import Flask, render_template, request, jsonify
import telebot
import os
from threading import Thread
from datetime import datetime
import pytz
import swisseph as swe
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = telebot.TeleBot(TOKEN)

swe.set_sid_mode(swe.SIDM_LAHIRI)

PLANETS = {
    "Солнце": swe.SUN,
    "Луна": swe.MOON,
    "Марс": swe.MARS,
    "Меркурий": swe.MERCURY,
    "Юпитер": swe.JUPITER,
    "Венера": swe.VENUS,
    "Сатурн": swe.SATURN,
    "Раху": swe.MEAN_NODE,
}

SIGNS = [
    "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
    "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
]

NAKSHATRAS = [
    "Ашвини", "Бхарани", "Криттика", "Рохини", "Мригашира", "Ардра",
    "Пунарвасу", "Пушья", "Ашлеша", "Магха", "Пурва Пхалгуни", "Уттара Пхалгуни",
    "Хаста", "Читра", "Свати", "Вишакха", "Анурадха", "Джйештха",
    "Мула", "Пурва Ашадха", "Уттара Ашадха", "Шравана", "Дхаништха", "Шатабхиша",
    "Пурва Бхадрапада", "Уттара Бхадрапада", "Ревати"
]

DASHA_LORDS = [
    "Кету", "Венера", "Солнце", "Луна", "Марс",
    "Раху", "Юпитер", "Сатурн", "Меркурий"
]

DASHA_YEARS = {
    "Кету": 7,
    "Венера": 20,
    "Солнце": 6,
    "Луна": 10,
    "Марс": 7,
    "Раху": 18,
    "Юпитер": 16,
    "Сатурн": 19,
    "Меркурий": 17,
}

CITY_FALLBACK = {
    "киев": (50.4501, 30.5234),
    "київ": (50.4501, 30.5234),
    "москва": (55.7558, 37.6173),
    "ялта": (44.4952, 34.1663),
    "симферополь": (44.9521, 34.1024),
    "санкт-петербург": (59.9311, 30.3609),
}


def normalize_degree(deg):
    return deg % 360


def sign_info(lon):
    sign_index = int(lon // 30)
    degree_in_sign = lon % 30
    return SIGNS[sign_index], degree_in_sign


def nakshatra_info(lon):
    nak_size = 360 / 27
    pada_size = nak_size / 4

    nak_index = int(lon // nak_size)
    degree_in_nak = lon % nak_size
    pada = int(degree_in_nak // pada_size) + 1

    lord = DASHA_LORDS[nak_index % 9]

    return NAKSHATRAS[nak_index], pada, lord, degree_in_nak


def format_degree(value):
    deg = int(value)
    minutes = int((value - deg) * 60)
    return f"{deg}°{minutes:02d}′"


def get_coordinates(city):
    key = city.strip().lower()

    if key in CITY_FALLBACK:
        return CITY_FALLBACK[key]

    geolocator = Nominatim(user_agent="zvezdny_kod_bot")
    location = geolocator.geocode(city, timeout=10)

    if not location:
        raise ValueError("Город не найден")

    return location.latitude, location.longitude


def get_timezone(lat, lon):
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=lat, lng=lon)

    if not timezone_name:
        raise ValueError("Не удалось определить часовой пояс")

    return timezone_name


def calculate_jyotish(date_str, time_str, city):
    lat, lon = get_coordinates(city)
    timezone_name = get_timezone(lat, lon)

    local_tz = pytz.timezone(timezone_name)
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    localized_dt = local_tz.localize(local_dt)

    utc_dt = localized_dt.astimezone(pytz.utc)

    jd_ut = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    )

    ayanamsha = swe.get_ayanamsa_ut(jd_ut)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    planets_result = []

    for name, planet_id in PLANETS.items():
        position = swe.calc_ut(jd_ut, planet_id, flags)[0][0]
        position = normalize_degree(position)

        if name == "Раху":
            ketu_position = normalize_degree(position + 180)

        sign, deg_in_sign = sign_info(position)
        nak, pada, nak_lord, deg_in_nak = nakshatra_info(position)

        planets_result.append({
            "name": name,
            "longitude": position,
            "sign": sign,
            "degree": format_degree(deg_in_sign),
            "nakshatra": nak,
            "pada": pada,
            "nak_lord": nak_lord
        })

    ketu_sign, ketu_deg = sign_info(ketu_position)
    ketu_nak, ketu_pada, ketu_lord, _ = nakshatra_info(ketu_position)

    planets_result.append({
        "name": "Кету",
        "longitude": ketu_position,
        "sign": ketu_sign,
        "degree": format_degree(ketu_deg),
        "nakshatra": ketu_nak,
        "pada": ketu_pada,
        "nak_lord": ketu_lord
    })

    houses = swe.houses_ex(jd_ut, lat, lon, b"W", flags)
    asc = normalize_degree(houses[1][0])
    asc_sign, asc_degree = sign_info(asc)
    asc_nak, asc_pada, asc_lord, _ = nakshatra_info(asc)

    moon = next(p for p in planets_result if p["name"] == "Луна")
    moon_lon = moon["longitude"]
    moon_nak, moon_pada, moon_lord, moon_deg_in_nak = nakshatra_info(moon_lon)

    nak_size = 360 / 27
    remaining_fraction = (nak_size - moon_deg_in_nak) / nak_size
    balance_years = DASHA_YEARS[moon_lord] * remaining_fraction

    result = f"""
✨ ТВОЙ ДЖЙОТИШ-РАСЧЁТ

📅 Дата рождения: {date_str}
⏰ Время рождения: {time_str}
📍 Город: {city}

🌍 Координаты:
Широта: {round(lat, 4)}
Долгота: {round(lon, 4)}
Часовой пояс: {timezone_name}

🕰 UTC:
{utc_dt.strftime("%Y-%m-%d %H:%M")}

📌 Julian Day:
{round(jd_ut, 5)}

📌 Айанамша Лахири:
{format_degree(ayanamsha)}

━━━━━━━━━━━━━━

🌅 ЛАГНА:
{asc_sign} {format_degree(asc_degree)}
Накшатра: {asc_nak}, пада {asc_pada}

🌙 ЛУНА:
{moon["sign"]} {moon["degree"]}
Накшатра: {moon_nak}, пада {moon_pada}
Управитель накшатры: {moon_lord}

🪐 ПЛАНЕТЫ:
"""

    for p in planets_result:
        result += f"""
{p["name"]}: {p["sign"]} {p["degree"]}
Накшатра: {p["nakshatra"]}, пада {p["pada"]}
"""

    result += f"""

━━━━━━━━━━━━━━

⏳ ВИМШОТТАРИ ДАША:

Первая махадаша от Луны:
{moon_lord}

Остаток махадаши при рождении:
примерно {round(balance_years, 2)} лет

━━━━━━━━━━━━━━

🔮 БАЗОВЫЙ ВЫВОД:

Это уже не нумерология и не игрушечный расчёт.
Бот рассчитал карту по сидерическому зодиаку с айанамшей Лахири, определил лагну, накшатры, пады и стартовую Вимшоттари Дашу.

Следующий этап — добавить интерпретацию домов, управителей, аспектов Парашары и полноценный текст разбора.
"""

    return result


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
        result = calculate_jyotish(date, time, city)
    except Exception as e:
        result = f"Ошибка расчёта: {str(e)}"

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
