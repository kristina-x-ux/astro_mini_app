from datetime import datetime
import swisseph as swe
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

swe.set_ephe_path(".")
swe.set_sid_mode(swe.SIDM_LAHIRI)

SIGNS = [
    "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
    "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
]

SIGN_LORDS = {
    "Овен": "Марс",
    "Телец": "Венера",
    "Близнецы": "Меркурий",
    "Рак": "Луна",
    "Лев": "Солнце",
    "Дева": "Меркурий",
    "Весы": "Венера",
    "Скорпион": "Марс",
    "Стрелец": "Юпитер",
    "Козерог": "Сатурн",
    "Водолей": "Сатурн",
    "Рыбы": "Юпитер",
}

NAKSHATRAS = [
    "Ашвини", "Бхарани", "Криттика", "Рохини", "Мригашира",
    "Ардра", "Пунарвасу", "Пушья", "Ашлеша", "Магха",
    "Пурва Пхалгуни", "Уттара Пхалгуни", "Хаста", "Читра",
    "Свати", "Вишакха", "Анурадха", "Джйештха", "Мула",
    "Пурва Ашадха", "Уттара Ашадха", "Шравана", "Дхаништха",
    "Шатабхиша", "Пурва Бхадрапада", "Уттара Бхадрапада", "Ревати"
]

PLANETS = {
    "Солнце": swe.SUN,
    "Луна": swe.MOON,
    "Марс": swe.MARS,
    "Меркурий": swe.MERCURY,
    "Юпитер": swe.JUPITER,
    "Венера": swe.VENUS,
    "Сатурн": swe.SATURN,
    "Раху": swe.MEAN_NODE
}

def normalize_degree(degree):
    return degree % 360

def format_degree(degree):
    deg = int(degree)
    minutes = int((degree - deg) * 60)
    return f"{deg}°{minutes:02d}′"

def get_sign_data(longitude):
    longitude = normalize_degree(longitude)
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30
    sign = SIGNS[sign_index]

    return {
        "sign_index": sign_index,
        "sign": sign,
        "degree_text": format_degree(degree_in_sign),
        "full_text": f"{sign} {format_degree(degree_in_sign)}"
    }

def get_nakshatra_data(longitude):
    longitude = normalize_degree(longitude)

    nak_size = 360 / 27
    pada_size = nak_size / 4

    nak_index = int(longitude // nak_size)
    degree_in_nak = longitude % nak_size
    pada = int(degree_in_nak // pada_size) + 1

    return {
        "nakshatra": NAKSHATRAS[nak_index],
        "pada": pada
    }

def get_coordinates(city):
    geolocator = Nominatim(user_agent="astro_bot")
    location = geolocator.geocode(city)

    if not location:
        raise ValueError("Город не найден")

    return location.latitude, location.longitude

def get_timezone(lat, lon):
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=lat, lng=lon)

    if not tz:
        raise ValueError("Не удалось определить часовой пояс")

    return tz

def calculate_chart(date_str, time_str, city):
    lat, lon = get_coordinates(city)
    timezone_name = get_timezone(lat, lon)

    tz = pytz.timezone(timezone_name)
    dt_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt_local = tz.localize(dt_local)
    dt_utc = dt_local.astimezone(pytz.utc)

    jd = swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60
    )

    ayanamsha = swe.get_ayanamsa_ut(jd)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    houses, ascmc = swe.houses_ex(jd, lat, lon, b"W")
    lagna = normalize_degree(ascmc[0])

    lagna_sign_data = get_sign_data(lagna)
    lagna_nak = get_nakshatra_data(lagna)

    lagna_sign_index = lagna_sign_data["sign_index"]

    planets = {}

    for name, code in PLANETS.items():
        lon_p = normalize_degree(swe.calc_ut(jd, code, flags)[0][0])

        sign_data = get_sign_data(lon_p)
        nak_data = get_nakshatra_data(lon_p)

        house = ((sign_data["sign_index"] - lagna_sign_index) % 12) + 1

        planets[name] = {
            "full_text": sign_data["full_text"],
            "nakshatra": nak_data["nakshatra"],
            "pada": nak_data["pada"],
            "house": house
        }

    # Кету
    rahu_deg = swe.calc_ut(jd, swe.MEAN_NODE)[0][0]
    ketu_deg = normalize_degree(rahu_deg + 180)

    sign_data = get_sign_data(ketu_deg)
    nak_data = get_nakshatra_data(ketu_deg)

    house = ((sign_data["sign_index"] - lagna_sign_index) % 12) + 1

    planets["Кету"] = {
        "full_text": sign_data["full_text"],
        "nakshatra": nak_data["nakshatra"],
        "pada": nak_data["pada"],
        "house": house
    }

    return {
        "city": city,
        "lat": lat,
        "lon": lon,
        "timezone": timezone_name,
        "utc": str(dt_utc),
        "jd": jd,
        "ayanamsha": ayanamsha,
        "lagna_full_text": lagna_sign_data["full_text"],
        "lagna_nakshatra": lagna_nak["nakshatra"],
        "lagna_pada": lagna_nak["pada"],
        "planets": planets
                                             }
