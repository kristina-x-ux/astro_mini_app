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

CITY_FALLBACK = {
    "киев": (50.4501, 30.5234),
    "київ": (50.4501, 30.5234),
    "москва": (55.7558, 37.6173),
    "ялта": (44.4952, 34.1663),
    "симферополь": (44.9521, 34.1024),
    "санкт-петербург": (59.9311, 30.3609),
}


def normalize_degree(degree):
    return degree % 360


def format_degree(degree):
    deg = int(degree)
    minute_float = (degree - deg) * 60
    minute = int(round(minute_float))

    if minute == 60:
        deg += 1
        minute = 0

    return f"{deg}°{minute:02d}′"


def get_sign_data(longitude):
    longitude = normalize_degree(longitude)
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30

    return {
        "sign": SIGNS[sign_index],
        "degree_in_sign": degree_in_sign,
        "degree_text": format_degree(degree_in_sign),
        "full_text": f"{SIGNS[sign_index]} {format_degree(degree_in_sign)}"
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


def calculate_jd(dt_utc):
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600
    )


def calculate_chart(date_str, time_str, city):
    lat, lon = get_coordinates(city)
    timezone_name = get_timezone(lat, lon)

    local_tz = pytz.timezone(timezone_name)
    local_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    localized_dt = local_tz.localize(local_dt)

    utc_dt = localized_dt.astimezone(pytz.utc)
    jd = calculate_jd(utc_dt)

    ayanamsha = swe.get_ayanamsa_ut(jd)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    planets_result = {}

    for name, planet_code in PLANETS.items():
        longitude = swe.calc_ut(jd, planet_code, flags)[0][0]
        longitude = normalize_degree(longitude)

        sign_data = get_sign_data(longitude)
        nak_data = get_nakshatra_data(longitude)

        planets_result[name] = {
            "longitude": round(longitude, 4),
            "degree": round(longitude, 2),
            "sign": sign_data["sign"],
            "degree_text": sign_data["degree_text"],
            "full_text": sign_data["full_text"],
            "nakshatra": nak_data["nakshatra"],
            "pada": nak_data["pada"]
        }

    rahu_longitude = planets_result["Раху"]["longitude"]
    ketu_longitude = normalize_degree(rahu_longitude + 180)

    ketu_sign_data = get_sign_data(ketu_longitude)
    ketu_nak_data = get_nakshatra_data(ketu_longitude)

    planets_result["Кету"] = {
        "longitude": round(ketu_longitude, 4),
        "degree": round(ketu_longitude, 2),
        "sign": ketu_sign_data["sign"],
        "degree_text": ketu_sign_data["degree_text"],
        "full_text": ketu_sign_data["full_text"],
        "nakshatra": ketu_nak_data["nakshatra"],
        "pada": ketu_nak_data["pada"]
    }

    houses, ascmc = swe.houses_ex(jd, lat, lon, b"W")
    lagna_longitude = normalize_degree(ascmc[0])

    lagna_sign_data = get_sign_data(lagna_longitude)
    lagna_nak_data = get_nakshatra_data(lagna_longitude)

    moon = planets_result["Луна"]

    return {
        "city": city,
        "lat": lat,
        "lon": lon,
        "timezone": timezone_name,
        "utc": utc_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "jd": jd,
        "ayanamsha": ayanamsha,

        "lagna": round(lagna_longitude, 4),
        "lagna_sign": lagna_sign_data["sign"],
        "lagna_degree_text": lagna_sign_data["degree_text"],
        "lagna_full_text": lagna_sign_data["full_text"],
        "lagna_nakshatra": lagna_nak_data["nakshatra"],
        "lagna_pada": lagna_nak_data["pada"],

        "moon": moon["longitude"],
        "moon_full_text": moon["full_text"],
        "moon_nakshatra": moon["nakshatra"],
        "moon_pada": moon["pada"],

        "planets": planets_result
    }
