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

CITY_FALLBACK = {
    "киев": (50.4501, 30.5234, "Киев, Украина"),
    "киев, украина": (50.4501, 30.5234, "Киев, Украина"),
    "ялта": (44.4952, 34.1663, "Ялта, Россия"),
    "ялта, россия": (44.4952, 34.1663, "Ялта, Россия"),
    "москва": (55.7558, 37.6173, "Москва, Россия"),
    "москва, россия": (55.7558, 37.6173, "Москва, Россия"),
    "рига": (56.9496, 24.1052, "Рига, Латвия"),
    "рига, латвия": (56.9496, 24.1052, "Рига, Латвия"),
    "алматы": (43.2389, 76.8897, "Алматы, Казахстан"),
    "алматы, казахстан": (43.2389, 76.8897, "Алматы, Казахстан")
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


def short_place_name(location):
    address = location.raw.get("address", {})

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or ""
    )

    state = address.get("state") or address.get("region") or ""
    country = address.get("country") or ""

    parts = []

    if city:
        parts.append(city)

    if state and state != city:
        parts.append(state)

    if country:
        parts.append(country)

    if parts:
        return ", ".join(parts)

    return location.address


def search_places(query):
    query = query.strip()

    if len(query) < 2:
        return []

    key = query.lower()

    fallback_results = []
    for name, data in CITY_FALLBACK.items():
        if key in name:
            lat, lon, display = data
            fallback_results.append({
                "name": display,
                "lat": lat,
                "lon": lon
            })

    geolocator = Nominatim(user_agent="astroengine_place_search")

    locations = geolocator.geocode(
        query,
        exactly_one=False,
        limit=5,
        timeout=10,
        language="ru",
        addressdetails=True
    )

    results = fallback_results

    if locations:
        for loc in locations:
            results.append({
                "name": short_place_name(loc),
                "lat": loc.latitude,
                "lon": loc.longitude
            })

    unique = []
    seen = set()

    for item in results:
        key_item = (item["name"], round(item["lat"], 4), round(item["lon"], 4))

        if key_item not in seen:
            seen.add(key_item)
            unique.append(item)

    return unique[:6]


def get_coordinates(city, lat=None, lon=None, display_name=None):
    if lat is not None and lon is not None:
        return float(lat), float(lon), display_name or city

    city_clean = city.strip()
    key = city_clean.lower()

    if key in CITY_FALLBACK:
        lat, lon, display = CITY_FALLBACK[key]
        return lat, lon, display

    geolocator = Nominatim(user_agent="astroengine_geocoder")

    location = geolocator.geocode(
        city_clean,
        timeout=10,
        language="ru",
        addressdetails=True
    )

    if not location:
        raise ValueError(
            "Место не найдено. Введите подробнее, например: Киев, Украина"
        )

    return location.latitude, location.longitude, short_place_name(location)


def get_timezone(lat, lon):
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=lat, lng=lon)

    if not timezone_name:
        raise ValueError("Не удалось определить часовой пояс")

    return timezone_name


def calculate_chart(date_str, time_str, city, lat=None, lon=None, display_name=None):
    if not date_str or not time_str or not city:
        raise ValueError("Заполните дату, время и место рождения")

    lat, lon, display_city = get_coordinates(
        city=city,
        lat=lat,
        lon=lon,
        display_name=display_name
    )

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
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "timezone": timezone_name,
        "utc": utc_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "jd": round(jd, 5),
        "ayanamsha": round(ayanamsha, 3),
        "lagna": {
            "sign": lagna_sign,
            "degree": format_degree(lagna_deg),
            "nakshatra": lagna_nak,
            "pada": lagna_pada,
            "longitude": round(lagna_lon, 4)
        },
        "moon": {},
        "houses": [],
        "planets": {}
    }

    for i in range(12):
        sign_index = (lagna_sign_index + i) % 12
        result["houses"].append({
            "house": i + 1,
            "sign": SIGNS[sign_index]
        })

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
