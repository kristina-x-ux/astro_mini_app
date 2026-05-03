from datetime import datetime
import swisseph as swe
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

swe.set_ephe_path('.')

# ---------------------------
# 🌍 Получение координат
# ---------------------------
def get_coordinates(city):
    geolocator = Nominatim(user_agent="astro_app")
    location = geolocator.geocode(city)

    if not location:
        raise Exception("Город не найден")

    return location.latitude, location.longitude


# ---------------------------
# 🕒 Определение часового пояса
# ---------------------------
def get_timezone(lat, lon):
    tf = TimezoneFinder()
    return tf.timezone_at(lat=lat, lng=lon)


# ---------------------------
# 🧮 Julian Day
# ---------------------------
def calculate_jd(dt_utc):
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60
    )


# ---------------------------
# 🌙 Накшатра
# ---------------------------
nakshatras = [
    "Ашвини", "Бхарани", "Криттика", "Рохини", "Мригашира",
    "Ардра", "Пунарвасу", "Пушья", "Ашлеша", "Магха",
    "Пурва Пхалгуни", "Уттара Пхалгуни", "Хаста", "Читра",
    "Свати", "Вишакха", "Анурадха", "Джйештха", "Мула",
    "Пурва Ашадха", "Уттара Ашадха", "Шравана", "Дхаништха",
    "Шатабхиша", "Пурва Бхадрапада", "Уттара Бхадрапада", "Ревати"
]

def get_nakshatra(deg):
    nak = int(deg / (360 / 27))
    pada = int((deg % (360 / 27)) / (360 / 108)) + 1
    return nakshatras[nak], pada


# ---------------------------
# 🪐 Планеты
# ---------------------------
planets = {
    "Солнце": swe.SUN,
    "Луна": swe.MOON,
    "Марс": swe.MARS,
    "Меркурий": swe.MERCURY,
    "Юпитер": swe.JUPITER,
    "Венера": swe.VENUS,
    "Сатурн": swe.SATURN,
    "Раху": swe.MEAN_NODE
}


# ---------------------------
# 🔮 Главная функция
# ---------------------------
def calculate_chart(date_str, time_str, city):

    # 📅 Парсим дату
    dt_local = datetime.strptime(
        f"{date_str} {time_str}",
        "%Y-%m-%d %H:%M"
    )

    # 🌍 координаты
    lat, lon = get_coordinates(city)

    # 🕒 часовой пояс
    tz_name = get_timezone(lat, lon)
    tz = pytz.timezone(tz_name)

    dt_local = tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.utc)

    # 🧮 JD
    jd = calculate_jd(dt_utc)

    # 🌌 Аянамша
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsha = swe.get_ayanamsa(jd)

    # 🌅 Лагна
    houses, ascmc = swe.houses(jd, lat, lon)
    lagna = ascmc[0]

    # 🌙 Луна
    moon = swe.calc_ut(jd, swe.MOON)[0][0]

    # 🪐 Планеты
    result_planets = {}
    for name, code in planets.items():
        pos = swe.calc_ut(jd, code)[0][0]
        nak, pada = get_nakshatra(pos)
        result_planets[name] = {
            "degree": round(pos, 2),
            "nakshatra": nak,
            "pada": pada
        }

    # ☊ Кету
    ketu_deg = (result_planets["Раху"]["degree"] + 180) % 360
    nak, pada = get_nakshatra(ketu_deg)

    result_planets["Кету"] = {
        "degree": round(ketu_deg, 2),
        "nakshatra": nak,
        "pada": pada
    }

    # 🌙 Накшатра Луны
    moon_nak, moon_pada = get_nakshatra(moon)

    return {
        "city": city,
        "lat": lat,
        "lon": lon,
        "timezone": tz_name,
        "utc": str(dt_utc),
        "jd": jd,
        "ayanamsha": ayanamsha,
        "lagna": lagna,
        "moon": moon,
        "moon_nakshatra": moon_nak,
        "moon_pada": moon_pada,
        "planets": result_planets
    }
