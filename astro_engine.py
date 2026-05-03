from datetime import datetime
import swisseph as swe
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim


# =========================
# БАЗОВЫЕ НАСТРОЙКИ
# =========================

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
    "Раху": swe.MEAN_NODE,
}


CITY_FALLBACK = {
    "киев": (50.4501, 30.5234),
    "київ": (50.4501, 30.5234),
    "москва": (55.7558, 37.6173),
    "ялта": (44.4952, 34.1663),
    "симферополь": (44.9521, 34.1024),
    "санкт-петербург": (59.9311, 30.3609),
}


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

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


def get_sign_index(longitude):
    longitude = normalize_degree(longitude)
    return int(longitude // 30)


def get_sign_data(longitude):
    longitude = normalize_degree(longitude)
    sign_index = get_sign_index(longitude)
    degree_in_sign = longitude % 30
    sign = SIGNS[sign_index]

    return {
        "sign_index": sign_index,
        "sign": sign,
        "degree_in_sign": degree_in_sign,
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


def get_house_from_lagna(planet_sign_index, lagna_sign_index):
    return ((planet_sign_index - lagna_sign_index) % 12) + 1


def build_houses_from_lagna(lagna_sign_index):
    houses = {}

    for house_number in range(1, 13):
        sign_index = (lagna_sign_index + house_number - 1) % 12
        sign = SIGNS[sign_index]

        houses[house_number] = {
            "house": house_number,
            "sign": sign,
            "sign_index": sign_index,
            "lord": SIGN_LORDS[sign]
        }

    return houses


def get_coordinates(city):
    city_clean = city.strip()
    key = city_clean.lower()

    if key in CITY_FALLBACK:
        return CITY_FALLBACK[key]

    geolocator = Nominatim(user_agent="zvezdny_kod_bot")
    location = geolocator.geocode(city_clean, timeout=10)

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


def build_planet_data(name, longitude, lagna_sign_index):
    longitude = normalize_degree(longitude)

    sign_data = get_sign_data(longitude)
    nak_data = get_nakshatra_data(longitude)

    house_number = get_house_from_lagna(
        sign_data["sign_index"],
        lagna_sign_index
    )

    return {
        "name": name,
        "longitude": round(longitude, 4),
        "degree": round(longitude, 2),
        "sign": sign_data["sign"],
        "sign_index": sign_data["sign_index"],
        "degree_text": sign_data["degree_text"],
        "full_text": sign_data["full_text"],
        "nakshatra": nak_data["nakshatra"],
        "pada": nak_data["pada"],
        "house": house_number
    }


# =========================
# ГЛАВНАЯ ФУНКЦИЯ РАСЧЁТА
# =========================

def calculate_chart(date_str, time_str, city):
    lat, lon = get_coordinates(city)
    timezone_name = get_timezone(lat, lon)

    local_tz = pytz.timezone(timezone_name)

    local_dt = datetime.strptime(
        f"{date_str} {time_str}",
        "%Y-%m-%d %H:%M"
    )

    localized_dt = local_tz.localize(local_dt)
    utc_dt = localized_dt.astimezone(pytz.utc)

    jd = calculate_jd(utc_dt)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsha = swe.get_ayanamsa_ut(jd)

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # =========================
    # ЛАГНА
    # =========================

    houses, ascmc = swe.houses_ex(jd, lat, lon, b"W")
    lagna_longitude = normalize_degree(ascmc[0])

    lagna_sign_data = get_sign_data(lagna_longitude)
    lagna_nak_data = get_nakshatra_data(lagna_longitude)
    lagna_sign_index = lagna_sign_data["sign_index"]

    houses_from_lagna = build_houses_from_lagna(lagna_sign_index)

    # =========================
    # ПЛАНЕТЫ
    # =========================

    planets_result = {}

    for name, planet_code in PLANETS.items():
        longitude = swe.calc_ut(jd, planet_code, flags)[0][0]

        planets_result[name] = build_planet_data(
            name=name,
            longitude=longitude,
            lagna_sign_index=lagna_sign_index
        )

    # =========================
    # КЕТУ
    # =========================

    rahu_longitude = planets_result["Раху"]["longitude"]
    ketu_longitude = normalize_degree(rahu_longitude + 180)

    planets_result["Кету"] = build_planet_data(
        name="Кету",
        longitude=ketu_longitude,
        lagna_sign_index=lagna_sign_index
    )

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
        "lagna_sign_index": lagna_sign_index,
        "lagna_degree_text": lagna_sign_data["degree_text"],
        "lagna_full_text": lagna_sign_data["full_text"],
        "lagna_nakshatra": lagna_nak_data["nakshatra"],
        "lagna_pada": lagna_nak_data["pada"],
        "lagna_lord": SIGN_LORDS[lagna_sign_data["sign"]],

        "moon": moon["longitude"],
        "moon_sign": moon["sign"],
        "moon_full_text": moon["full_text"],
        "moon_nakshatra": moon["nakshatra"],
        "moon_pada": moon["pada"],
        "moon_house": moon["house"],

        "houses": houses_from_lagna,
        "planets": planets_result
        }
