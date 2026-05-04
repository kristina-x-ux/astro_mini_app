import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta, date
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

NAKSHATRA_LORDS = [
    "Кету", "Венера", "Солнце", "Луна", "Марс", "Раху", "Юпитер", "Сатурн", "Меркурий",
    "Кету", "Венера", "Солнце", "Луна", "Марс", "Раху", "Юпитер", "Сатурн", "Меркурий",
    "Кету", "Венера", "Солнце", "Луна", "Марс", "Раху", "Юпитер", "Сатурн", "Меркурий"
]

DASHA_ORDER = ["Кету", "Венера", "Солнце", "Луна", "Марс", "Раху", "Юпитер", "Сатурн", "Меркурий"]

DASHA_YEARS = {
    "Кету": 7,
    "Венера": 20,
    "Солнце": 6,
    "Луна": 10,
    "Марс": 7,
    "Раху": 18,
    "Юпитер": 16,
    "Сатурн": 19,
    "Меркурий": 17
}

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


def parse_date(date_str):
    date_str = date_str.strip()

    if "." in date_str:
        return datetime.strptime(date_str, "%d.%m.%Y").date()

    return datetime.strptime(date_str, "%Y-%m-%d").date()


def parse_time(time_str):
    time_str = time_str.strip()

    if len(time_str.split(":")) == 2:
        return datetime.strptime(time_str, "%H:%M").time()

    return datetime.strptime(time_str, "%H:%M:%S").time()


def format_date_ru(dt):
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime("%d.%m.%Y")


def format_datetime_ru(dt):
    return dt.strftime("%d.%m.%Y")


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

    return NAKSHATRAS[nak_index], pada, nak_index


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
        raise ValueError("Место не найдено. Введите подробнее, например: Киев, Украина")

    return location.latitude, location.longitude, short_place_name(location)


def get_timezone(lat, lon):
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=lat, lng=lon)

    if not timezone_name:
        raise ValueError("Не удалось определить часовой пояс")

    return timezone_name


def get_utc_offset_string(local_dt):
    offset = local_dt.utcoffset()

    if offset is None:
        return "UTC 0"

    total_seconds = int(offset.total_seconds())
    hours = total_seconds // 3600

    if hours >= 0:
        return f"UTC +{hours}"

    return f"UTC {hours}"


def years_to_days(years):
    return years * 365.2425


def add_days(dt, days):
    return dt + timedelta(days=days)


def next_lord(lord):
    index = DASHA_ORDER.index(lord)
    return DASHA_ORDER[(index + 1) % len(DASHA_ORDER)]


def ordered_lords_from(start_lord):
    start_index = DASHA_ORDER.index(start_lord)
    return DASHA_ORDER[start_index:] + DASHA_ORDER[:start_index]


def is_current_period(start_dt, end_dt):
    today = datetime.utcnow()
    return start_dt <= today < end_dt


def build_sub_periods(parent_start, parent_end, parent_lord, level):
    total_days = (parent_end - parent_start).total_seconds() / 86400
    periods = []
    current_start = parent_start

    for lord in ordered_lords_from(parent_lord):
        portion = DASHA_YEARS[lord] / 120
        duration_days = total_days * portion
        current_end = add_days(current_start, duration_days)

        periods.append({
            "lord": lord,
            "start": format_datetime_ru(current_start),
            "end": format_datetime_ru(current_end),
            "is_current": is_current_period(current_start, current_end),
            "level": level
        })

        current_start = current_end

    return periods


def calculate_vimshottari_dashas(birth_dt, moon_longitude):
    nak_size = 360 / 27
    nak_index = int(normalize_degree(moon_longitude) // nak_size)
    degree_in_nak = normalize_degree(moon_longitude) % nak_size

    birth_lord = NAKSHATRA_LORDS[nak_index]
    completed_fraction = degree_in_nak / nak_size
    remaining_fraction = 1 - completed_fraction

    first_md_years_remaining = DASHA_YEARS[birth_lord] * remaining_fraction

    mahadashas = []

    current_start = birth_dt
    current_end = add_days(current_start, years_to_days(first_md_years_remaining))

    mahadashas.append({
        "lord": birth_lord,
        "start": format_datetime_ru(current_start),
        "end": format_datetime_ru(current_end),
        "is_current": is_current_period(current_start, current_end),
        "level": "maha"
    })

    current_lord = next_lord(birth_lord)
    current_start = current_end

    for _ in range(20):
        years = DASHA_YEARS[current_lord]
        current_end = add_days(current_start, years_to_days(years))

        mahadashas.append({
            "lord": current_lord,
            "start": format_datetime_ru(current_start),
            "end": format_datetime_ru(current_end),
            "is_current": is_current_period(current_start, current_end),
            "level": "maha"
        })

        current_lord = next_lord(current_lord)
        current_start = current_end

    current_maha = next((p for p in mahadashas if p["is_current"]), mahadashas[0])

    md_start = datetime.strptime(current_maha["start"], "%d.%m.%Y")
    md_end = datetime.strptime(current_maha["end"], "%d.%m.%Y")

    antardashas = build_sub_periods(
        md_start,
        md_end,
        current_maha["lord"],
        "antar"
    )

    current_antar = next((p for p in antardashas if p["is_current"]), antardashas[0])

    ad_start = datetime.strptime(current_antar["start"], "%d.%m.%Y")
    ad_end = datetime.strptime(current_antar["end"], "%d.%m.%Y")

    pratyantardashas = build_sub_periods(
        ad_start,
        ad_end,
        current_antar["lord"],
        "pratyantar"
    )

    return {
        "birth_lord": birth_lord,
        "current_maha": current_maha,
        "current_antar": current_antar,
        "current_pratyantar": next(
            (p for p in pratyantardashas if p["is_current"]),
            pratyantardashas[0]
        ),
        "mahadashas": mahadashas,
        "antardashas": antardashas,
        "pratyantardashas": pratyantardashas
    }


def calculate_chart(date_str, time_str, city, lat=None, lon=None, display_name=None):
    if not date_str or not time_str or not city:
        raise ValueError("Заполните дату, время и место рождения")

    birth_date = parse_date(date_str)
    birth_time = parse_time(time_str)

    lat, lon, display_city = get_coordinates(
        city=city,
        lat=lat,
        lon=lon,
        display_name=display_name
    )

    timezone_name = get_timezone(lat, lon)
    local_tz = pytz.timezone(timezone_name)

    local_dt = datetime.combine(birth_date, birth_time)
    local_dt = local_tz.localize(local_dt)

    utc_dt = local_dt.astimezone(pytz.utc)

    hour_decimal = (
        utc_dt.hour
        + utc_dt.minute / 60
        + utc_dt.second / 3600
    )

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
    lagna_nak, lagna_pada, lagna_nak_index = get_nakshatra(lagna_lon)

    result = {
        "input_date": birth_date.strftime("%d.%m.%Y"),
        "input_time": birth_time.strftime("%H:%M:%S"),
        "city": display_city,
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "timezone": timezone_name,
        "utc_offset": get_utc_offset_string(local_dt),
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
        "planets": {},
        "dashas": {}
    }

    for i in range(12):
        sign_index = (lagna_sign_index + i) % 12
        result["houses"].append({
            "house": i + 1,
            "sign": SIGNS[sign_index]
        })

    rahu_pos = None
    moon_longitude = None

    for planet_name, planet_id in PLANETS.items():
        pos = swe.calc_ut(jd, planet_id, flags)[0][0]
        pos = normalize_degree(pos)

        if planet_name == "Раху":
            rahu_pos = pos

        sign, deg_in_sign, sign_index = get_sign_and_degree(pos)
        nak, pada, nak_index = get_nakshatra(pos)
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
            moon_longitude = pos
            result["moon"] = planet_data

        result["planets"][planet_name] = planet_data

    ketu_pos = normalize_degree(rahu_pos + 180)
    ketu_sign, ketu_deg, ketu_sign_index = get_sign_and_degree(ketu_pos)
    ketu_nak, ketu_pada, ketu_nak_index = get_nakshatra(ketu_pos)

    result["planets"]["Кету"] = {
        "sign": ketu_sign,
        "degree": format_degree(ketu_deg),
        "nakshatra": ketu_nak,
        "pada": ketu_pada,
        "house": get_house(ketu_sign_index, lagna_sign_index),
        "longitude": round(ketu_pos, 4)
    }

    result["dashas"] = calculate_vimshottari_dashas(
        birth_dt=local_dt.replace(tzinfo=None),
        moon_longitude=moon_longitude
    )

    return result
