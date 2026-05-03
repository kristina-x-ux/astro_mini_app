import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz


SIGNS = [
    "Овен", "Телец", "Близнецы", "Рак",
    "Лев", "Дева", "Весы", "Скорпион",
    "Стрелец", "Козерог", "Водолей", "Рыбы"
]

NAKSHATRAS = [
    "Ашвини", "Бхарани", "Криттика", "Рохини",
    "Мригашира", "Ардра", "Пунарвасу", "Пушья",
    "Ашлеша", "Магха", "Пурва Пхалгуни", "Уттара Пхалгуни",
    "Хаста", "Читра", "Свати", "Вишакха",
    "Анурадха", "Джйештха", "Мула", "Пурва Ашадха",
    "Уттара Ашадха", "Шравана", "Дхаништха", "Шатабхиша",
    "Пурва Бхадрапада", "Уттара Бхадрапада", "Ревати"
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


def normalize_degree(deg):
    return deg % 360


def get_sign_and_degree(lon):
    lon = normalize_degree(lon)
    sign_index = int(lon // 30)
    degree_in_sign = lon % 30
    return SIGNS[sign_index], degree_in_sign, sign_index


def get_nakshatra(lon):
    lon = normalize_degree(lon)
    nak_size = 360 / 27
    pada_size = nak_size / 4

    nak_index = int(lon // nak_size)
    degree_in_nak = lon % nak_size
    pada = int(degree_in_nak // pada_size) + 1

    return NAKSHATRAS[nak_index], pada


def format_degree(deg):
    degree = int(deg)
    minute = int((deg - degree) * 60)
    return f"{degree}°{minute:02d}'"


def get_house(planet_sign_index, lagna_sign_index):
    return ((planet_sign_index - lagna_sign_index) % 12) + 1


def get_coordinates(place):
    place = place.strip()

    if not place:
        raise ValueError("Введите место рождения")

    geolocator = Nominatim(user_agent="astroengine_global_search")

    location = geolocator.geocode(
        place,
        timeout=10,
        language="ru",
        addressdetails=True
    )

    if not location:
        raise ValueError(
            "Место не найдено. Введите подробнее, например: Киев, Украина"
        )

    display_name = location.address

    return location.latitude, location.longitude, display_name


def get_timezone(lat, lon):
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=lat, lng=lon)

    if not timezone_name:
        raise ValueError("Не удалось определить часовой пояс")

    return timezone_name


def calculate_chart(date_str, time_str, city):
    if not date_str or not time_str or not city:
        raise ValueError("Заполните дату, время и место рождения")

    lat, lon, display_city = get_coordinates(city)
    timezone_name = get_timezone(lat, lon)

    local_tz = pytz.timezone(timezone_name)

    local_dt = datetime.strptime(
        f"{date_str} {time_str}",
        "%Y-%m-%d %H:%M"
    )

    local_dt = local_tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.utc)

    hour_decimal = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600

    jd = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        hour_decimal
    )

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsha = swe.get_ayanamsa_ut(jd)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    houses, ascmc = swe.houses_ex(
        jd,
        lat,
        lon,
        b'P',
        flags
    )

    lagna_lon = normalize_degree(ascmc[0])
    lagna_sign, lagna_deg, lagna_sign_index = get_sign_and_degree(lagna_lon)
    lagna_nak, lagna_pada = get_nakshatra(lagna_lon)

    result = {
        "city": display_city,
        "lat": lat,
        "lon": lon,
        "timezone": timezone_name,
        "utc": utc_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "jd": jd,
        "ayanamsha": round(ayanamsha, 3),
        "lagna": {
            "sign": lagna_sign,
            "degree": format_degree(lagna_deg),
            "nakshatra": lagna_nak,
            "pada": lagna_pada
        },
        "moon": {},
        "planets": {}
    }

    rahu_pos = None

    for planet_name, planet_id in PLANETS.items():
        pos = swe.calc_ut(jd, planet_id, flags)[0][0]
        pos = normalize_degree(pos)

        if planet_name == "Раху":
            rahu_pos = pos

        sign, deg_in_sign, sign_index = get_sign_and_degree(pos)
        nak, pada = get_nakshatra(pos)
        house = get_house(sign_index, lagna_sign_index)

        planet_data = {
            "sign": sign,
            "degree": format_degree(deg_in_sign),
            "nakshatra": nak,
            "pada": pada,
            "house": house,
            "longitude": round(pos, 4)
        }

        if planet_name == "Луна":
            result["moon"] = planet_data

        result["planets"][planet_name] = planet_data

    ketu_pos = normalize_degree(rahu_pos + 180)
    ketu_sign, ketu_deg, ketu_sign_index = get_sign_and_degree(ketu_pos)
    ketu_nak, ketu_pada = get_nakshatra(ketu_pos)

    result["planets"]["Кету"] = {
        "sign": ketu_sign,
        "degree": format_degree(ketu_deg),
        "nakshatra": ketu_nak,
        "pada": ketu_pada,
        "house": get_house(ketu_sign_index, lagna_sign_index),
        "longitude": round(ketu_pos, 4)
    }

    return result
