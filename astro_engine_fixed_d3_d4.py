import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
import pytz
import math


SIGNS = [
    "Овен", "Телец", "Близнецы", "Рак",
    "Лев", "Дева", "Весы", "Скорпион",
    "Стрелец", "Козерог", "Водолей", "Рыбы"
]

SIGN_NUMBERS = {
    "Овен": 1,
    "Телец": 2,
    "Близнецы": 3,
    "Рак": 4,
    "Лев": 5,
    "Дева": 6,
    "Весы": 7,
    "Скорпион": 8,
    "Стрелец": 9,
    "Козерог": 10,
    "Водолей": 11,
    "Рыбы": 12
}

SIGN_LORDS = {
    0: "Марс",
    1: "Венера",
    2: "Меркурий",
    3: "Луна",
    4: "Солнце",
    5: "Меркурий",
    6: "Венера",
    7: "Марс",
    8: "Юпитер",
    9: "Сатурн",
    10: "Сатурн",
    11: "Юпитер"
}

PLANET_WEEK_ORDER = [
    "Солнце", "Луна", "Марс", "Меркурий",
    "Юпитер", "Венера", "Сатурн"
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

DASHA_ORDER = [
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
    "Уран": swe.URANUS,
    "Нептун": swe.NEPTUNE,
    "Плутон": swe.PLUTO,
    "Раху": swe.MEAN_NODE
}

CORE_KARAKA_PLANETS = [
    "Солнце", "Луна", "Марс", "Меркурий",
    "Юпитер", "Венера", "Сатурн"
]

PLANET_SHORT = {
    "Солнце": "Со",
    "Луна": "Лу",
    "Марс": "Ма",
    "Меркурий": "Ме",
    "Юпитер": "Юп",
    "Венера": "Ве",
    "Сатурн": "Са",
    "Уран": "Ур",
    "Нептун": "Не",
    "Плутон": "Пл",
    "Раху": "Ра",
    "Кету": "Ке",
    "Манди": "Мн",
    "Гулика": "Гу"
}

SPECIAL_POINT_SHORT = {
    "Арудха Лагна": "AL",
    "Упапада": "UL",
    "Хора Лагна": "HL",
    "Гхати Лагна": "GL",
    "Варнада Лагна": "VL"
}

KARAKA_NAMES = ["АК", "АмК", "БК", "МК", "ПК", "ГК", "ДК"]

VARGAS = {
    "D1": 1,
    "Moon": 1,
    "D2": 2,
    "D3": 3,
    "D4": 4,
    "D5": 5,
    "D6": 6,
    "D7": 7,
    "D8": 8,
    "D9": 9,
    "D10": 10,
    "D11": 11,
    "D12": 12,
    "D16": 16,
    "D24": 24,
    "D30": 30,
    "D60": 60,
    "D81": 81
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
    date_str = str(date_str).strip()
    if "." in date_str:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def parse_time(time_str):
    time_str = str(time_str).strip()
    parts = time_str.split(":")
    if len(parts) == 2:
        return datetime.strptime(time_str, "%H:%M").time()
    return datetime.strptime(time_str, "%H:%M:%S").time()


def format_date(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%d.%m.%Y")
    return dt.strftime("%d.%m.%Y")


def parse_period_date(date_str):
    return datetime.strptime(date_str, "%d.%m.%Y")


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
    minute_float = (deg - degree) * 60
    minute = int(minute_float)
    second = int((minute_float - minute) * 60)
    return f"{degree}°{minute:02d}'{second:02d}\""


def get_house(planet_sign_index, lagna_sign_index):
    return ((planet_sign_index - lagna_sign_index) % 12) + 1


def get_sign_distance(from_sign_index, to_sign_index):
    return (to_sign_index - from_sign_index) % 12


def sign_from_house(lagna_sign_index, house):
    return (lagna_sign_index + house - 1) % 12


def house_from_sign(lagna_sign_index, sign_index):
    return ((sign_index - lagna_sign_index) % 12) + 1


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

    return ", ".join(parts) if parts else location.address


def search_places(query):
    query = str(query).strip()

    if len(query) < 2:
        return []

    key = query.lower()
    fallback_results = []

    for name, data in CITY_FALLBACK.items():
        if key in name:
            lat, lon, display = data
            fallback_results.append({"name": display, "lat": lat, "lon": lon})

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

    city_clean = str(city).strip()
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


def ordered_lords_from(start_lord):
    start_index = DASHA_ORDER.index(start_lord)
    return DASHA_ORDER[start_index:] + DASHA_ORDER[:start_index]


def period_is_current(start_dt, end_dt):
    now = datetime.utcnow()
    return start_dt <= now < end_dt


def make_period_node(lord, start_dt, end_dt, level, path):
    return {
        "lord": lord,
        "start": format_date(start_dt),
        "end": format_date(end_dt),
        "is_current": period_is_current(start_dt, end_dt),
        "level": level,
        "path": path,
        "children": []
    }


def build_children(parent_start, parent_end, parent_lord, level, path, max_depth):
    total_days = (parent_end - parent_start).total_seconds() / 86400
    children = []
    current_start = parent_start

    for lord in ordered_lords_from(parent_lord):
        duration_days = total_days * (DASHA_YEARS[lord] / 120)
        current_end = add_days(current_start, duration_days)
        child_path = path + [lord]

        node = make_period_node(
            lord,
            current_start,
            current_end,
            level,
            child_path
        )

        if level < max_depth:
            node["children"] = build_children(
                current_start,
                current_end,
                lord,
                level + 1,
                child_path,
                max_depth
            )

        children.append(node)
        current_start = current_end

    return children


def next_lord(lord):
    index = DASHA_ORDER.index(lord)
    return DASHA_ORDER[(index + 1) % len(DASHA_ORDER)]


def find_current_path(nodes):
    for node in nodes:
        if node.get("is_current"):
            return node["path"]

        child_path = find_current_path(node.get("children", []))
        if child_path:
            return child_path

    return []


def find_current_periods(nodes):
    active = {
        "mahadasha": None,
        "antardasha": None,
        "pratyantardasha": None,
        "path": [],
        "path_text": ""
    }

    def walk(items):
        for item in items:
            if item.get("is_current"):
                level = item.get("level")

                if level == 1:
                    active["mahadasha"] = item
                elif level == 2:
                    active["antardasha"] = item
                elif level == 3:
                    active["pratyantardasha"] = item

                walk(item.get("children", []))
                break

    walk(nodes)

    path = []

    for key in ["mahadasha", "antardasha", "pratyantardasha"]:
        if active[key]:
            path.append(active[key].get("lord"))

    active["path"] = path
    active["path_text"] = " / ".join(path)

    return active


def calculate_vimshottari_dashas(birth_dt, moon_longitude):
    nak_size = 360 / 27
    moon_longitude = normalize_degree(moon_longitude)

    nak_index = int(moon_longitude // nak_size)
    degree_in_nak = moon_longitude % nak_size

    birth_lord = NAKSHATRA_LORDS[nak_index]
    completed_fraction = degree_in_nak / nak_size
    remaining_fraction = 1 - completed_fraction

    first_md_years_remaining = DASHA_YEARS[birth_lord] * remaining_fraction

    mahadashas = []
    current_start = birth_dt

    ordered = ordered_lords_from(birth_lord)

    for index, lord in enumerate(ordered):
        years = first_md_years_remaining if index == 0 else DASHA_YEARS[lord]
        current_end = add_days(current_start, years_to_days(years))

        node = make_period_node(
            lord,
            current_start,
            current_end,
            1,
            [lord]
        )

        node["children"] = build_children(
            current_start,
            current_end,
            lord,
            2,
            [lord],
            3
        )

        node["antardashas"] = node["children"]

        for antar in node["children"]:
            antar["pratyantardashas"] = antar.get("children", [])

        mahadashas.append(node)
        current_start = current_end

    current_periods = find_current_periods(mahadashas)

    return {
        "birth_lord": birth_lord,
        "system": "Вимшоттари",
        "levels": 3,
        "cycle_years": 120,
        "tree": mahadashas,
        "mahadashas": mahadashas,
        "current_path": current_periods["path"],
        "current_path_text": current_periods["path_text"],
        "current_periods": current_periods
    }


def calculate_chara_karakas(planets):
    sortable = []

    for name in CORE_KARAKA_PLANETS:
        longitude = planets[name]["longitude"]
        degree_in_sign = longitude % 30
        sortable.append((name, degree_in_sign))

    sortable.sort(key=lambda x: x[1], reverse=True)

    karakas = {}

    for index, item in enumerate(sortable):
        planet_name = item[0]
        karakas[planet_name] = KARAKA_NAMES[index]

    return karakas


def aspect_target(from_house, aspect_number):
    return ((from_house + aspect_number - 2) % 12) + 1


def get_planet_aspect_houses(planet_name, from_house):
    if planet_name == "Марс":
        return [
            aspect_target(from_house, 4),
            aspect_target(from_house, 7),
            aspect_target(from_house, 8)
        ]

    if planet_name == "Юпитер":
        return [
            aspect_target(from_house, 5),
            aspect_target(from_house, 7),
            aspect_target(from_house, 9)
        ]

    if planet_name == "Сатурн":
        return [
            aspect_target(from_house, 3),
            aspect_target(from_house, 7),
            aspect_target(from_house, 10)
        ]

    if planet_name in ["Раху", "Кету"]:
        return [
            aspect_target(from_house, 5),
            aspect_target(from_house, 7),
            aspect_target(from_house, 9)
        ]

    if planet_name in ["Солнце", "Луна", "Меркурий", "Венера", "Уран", "Нептун", "Плутон"]:
        return [aspect_target(from_house, 7)]

    return []


def calculate_parashara_aspects(planets):
    aspects = []

    for name, p in planets.items():
        if name in ["Манди", "Гулика"]:
            continue

        from_house = p["house"]
        aspect_houses = get_planet_aspect_houses(name, from_house)

        aspects.append({
            "planet": name,
            "planet_short": PLANET_SHORT.get(name, name),
            "from_house": from_house,
            "aspects_houses": sorted(list(set(aspect_houses)))
        })

    return aspects


def calc_jd_from_datetime(dt_utc):
    hour_decimal = (
        dt_utc.hour
        + dt_utc.minute / 60
        + dt_utc.second / 3600
    )
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        hour_decimal
    )


def calc_lagna_longitude(jd, lat, lon):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    houses, ascmc = swe.houses_ex(
        jd,
        lat,
        lon,
        b'P',
        flags
    )
    return normalize_degree(ascmc[0])


def safe_rise_set(jd, lat, lon, rsmi):
    geopos = (lon, lat, 0)
    try:
        result = swe.rise_trans(
            jd,
            swe.SUN,
            rsmi,
            geopos,
            0,
            0
        )
        if isinstance(result, tuple):
            if len(result) >= 2:
                code = result[0]
                values = result[1]
                if code == 0 and values:
                    return values[0]
    except Exception:
        pass
    return None


def find_sunrise_sunset(jd, lat, lon):
    sunrise = safe_rise_set(jd, lat, lon, swe.CALC_RISE | swe.BIT_DISC_CENTER)
    sunset = safe_rise_set(jd, lat, lon, swe.CALC_SET | swe.BIT_DISC_CENTER)

    if sunrise is None or sunset is None:
        return None, None

    return sunrise, sunset


def datetime_from_jd(jd, timezone_name):
    y, m, d, hour = swe.revjul(jd)
    h = int(hour)
    minute_float = (hour - h) * 60
    mi = int(minute_float)
    sec = int((minute_float - mi) * 60)

    utc_dt = datetime(y, m, d, h, mi, sec, tzinfo=pytz.utc)
    return utc_dt.astimezone(pytz.timezone(timezone_name))


def jd_from_local_datetime(local_dt):
    utc_dt = local_dt.astimezone(pytz.utc)
    return calc_jd_from_datetime(utc_dt)


def get_saturn_segment_index_for_day(weekday):
    day_lord = PLANET_WEEK_ORDER[weekday]
    order = PLANET_WEEK_ORDER[PLANET_WEEK_ORDER.index(day_lord):] + PLANET_WEEK_ORDER[:PLANET_WEEK_ORDER.index(day_lord)]
    return order.index("Сатурн")


def get_saturn_segment_index_for_night(weekday):
    fifth_lord_index = (weekday + 4) % 7
    night_lord = PLANET_WEEK_ORDER[fifth_lord_index]
    order = PLANET_WEEK_ORDER[PLANET_WEEK_ORDER.index(night_lord):] + PLANET_WEEK_ORDER[:PLANET_WEEK_ORDER.index(night_lord)]
    return order.index("Сатурн")


def calculate_mandi_gulika(local_dt, lat, lon, timezone_name):
    jd_birth = jd_from_local_datetime(local_dt)
    jd_day_start = math.floor(jd_birth - 0.5) + 0.5

    sunrise_today, sunset_today = find_sunrise_sunset(jd_day_start, lat, lon)
    sunrise_next, _ = find_sunrise_sunset(jd_day_start + 1, lat, lon)
    _, sunset_prev = find_sunrise_sunset(jd_day_start - 1, lat, lon)

    if sunrise_today is None or sunset_today is None:
        return {}

    py_to_jyotish_weekday = {
        0: 1,
        1: 2,
        2: 3,
        3: 4,
        4: 5,
        5: 6,
        6: 0
    }

    jyotish_weekday = py_to_jyotish_weekday[local_dt.weekday()]

    if sunrise_today <= jd_birth < sunset_today:
        segment_index = get_saturn_segment_index_for_day(jyotish_weekday)
        part = (sunset_today - sunrise_today) / 8
        saturn_start = sunrise_today + part * segment_index
        saturn_middle = saturn_start + part / 2
    else:
        if jd_birth < sunrise_today:
            night_start = sunset_prev
            night_end = sunrise_today
            night_weekday = py_to_jyotish_weekday[(local_dt - timedelta(days=1)).weekday()]
        else:
            night_start = sunset_today
            night_end = sunrise_next
            night_weekday = jyotish_weekday

        if night_start is None or night_end is None:
            return {}

        segment_index = get_saturn_segment_index_for_night(night_weekday)
        part = (night_end - night_start) / 8
        saturn_start = night_start + part * segment_index
        saturn_middle = saturn_start + part / 2

    gulika_lon = calc_lagna_longitude(saturn_middle, lat, lon)
    mandi_lon = gulika_lon

    return {
        "Гулика": gulika_lon,
        "Манди": mandi_lon
    }


def calculate_arudha_for_house(house_number, lagna_sign_index, planets):
    house_sign = sign_from_house(lagna_sign_index, house_number)
    lord_name = SIGN_LORDS[house_sign]

    if lord_name not in planets:
        return None

    lord_sign = int(planets[lord_name]["sign_index"])
    distance = get_sign_distance(house_sign, lord_sign)
    arudha_sign = (lord_sign + distance) % 12

    if arudha_sign == house_sign or arudha_sign == (house_sign + 6) % 12:
        arudha_sign = (arudha_sign + 9) % 12

    return arudha_sign


def calculate_special_lagnas(lagna_lon, moon_lon, sun_lon, local_dt, sunrise_jd, lat, lon):
    lagna_sign, lagna_deg, lagna_sign_index = get_sign_and_degree(lagna_lon)

    elapsed_days = 0
    birth_jd = jd_from_local_datetime(local_dt)
    if sunrise_jd:
        elapsed_days = max(0, birth_jd - sunrise_jd)

    elapsed_ghatis = elapsed_days * 60

    hora_lon = normalize_degree(sun_lon + elapsed_ghatis * 0.5 * 30)
    ghati_lon = normalize_degree(lagna_lon + elapsed_ghatis * 30)

    hora_sign, _, _ = get_sign_and_degree(hora_lon)
    ghati_sign, _, _ = get_sign_and_degree(ghati_lon)

    sun_sign_index = int(sun_lon // 30)
    moon_sign_index = int(moon_lon // 30)

    if lagna_sign_index % 2 == 0:
        varnada_sign_index = (lagna_sign_index + sun_sign_index) % 12
    else:
        varnada_sign_index = (lagna_sign_index - sun_sign_index) % 12

    return {
        "Хора Лагна": {
            "longitude": round(hora_lon, 4),
            "sign_index": int(hora_lon // 30),
            "sign": hora_sign,
            "sign_number": SIGN_NUMBERS[hora_sign]
        },
        "Гхати Лагна": {
            "longitude": round(ghati_lon, 4),
            "sign_index": int(ghati_lon // 30),
            "sign": ghati_sign,
            "sign_number": SIGN_NUMBERS[ghati_sign]
        },
        "Варнада Лагна": {
            "longitude": round(varnada_sign_index * 30, 4),
            "sign_index": varnada_sign_index,
            "sign": SIGNS[varnada_sign_index],
            "sign_number": SIGN_NUMBERS[SIGNS[varnada_sign_index]]
        }
    }


def add_point_to_planets(name, longitude, lagna_sign_index):
    sign, deg_in_sign, sign_index = get_sign_and_degree(longitude)
    nak, pada, nak_index = get_nakshatra(longitude)

    return {
        "sign": sign,
        "sign_number": SIGN_NUMBERS[sign],
        "sign_index": sign_index,
        "degree": format_degree(deg_in_sign),
        "degree_float": round(deg_in_sign, 4),
        "nakshatra": nak,
        "pada": pada,
        "house": get_house(sign_index, lagna_sign_index),
        "longitude": round(normalize_degree(longitude), 4),
        "karaka": ""
    }


def get_varga_sign_index(longitude, division):
    longitude = normalize_degree(longitude)
    sign_index = int(longitude // 30)
    degree_in_sign = longitude % 30

    if division == 1:
        return sign_index

    if division == 2:
        if sign_index % 2 == 0:
            return 4 if degree_in_sign < 15 else 3
        return 3 if degree_in_sign < 15 else 4

    if division == 3:
        # D3 Дреккана:
        # 0°–10°  -> сам знак
        # 10°–20° -> 5-й знак от него
        # 20°–30° -> 9-й знак от него
        if degree_in_sign < 10:
            return sign_index
        elif degree_in_sign < 20:
            return (sign_index + 4) % 12
        else:
            return (sign_index + 8) % 12

    if division == 4:
        # D4 Чатуртхамша:
        # знак делится на 4 части по 7°30′.
        # 1-я часть -> сам знак
        # 2-я часть -> 4-й знак от него
        # 3-я часть -> 7-й знак от него
        # 4-я часть -> 10-й знак от него
        part = int(degree_in_sign // 7.5)
        if part > 3:
            part = 3
        return (sign_index + part * 3) % 12

    if division == 5:
        part = int(degree_in_sign // 6)
        return (sign_index + part * 2) % 12

    if division == 6:
        part = int(degree_in_sign // 5)
        start = 0 if sign_index % 2 == 0 else 6
        return (start + part) % 12

    if division == 7:
        part = int(degree_in_sign // (30 / 7))
        start = sign_index if sign_index % 2 == 0 else (sign_index + 6) % 12
        return (start + part) % 12

    if division == 8:
        part = int(degree_in_sign // 3.75)
        if sign_index in [0, 4, 8]:
            start = 0
        elif sign_index in [1, 5, 9]:
            start = 8
        elif sign_index in [2, 6, 10]:
            start = 4
        else:
            start = 6
        return (start + part) % 12

    if division == 9:
        part = int(degree_in_sign // (30 / 9))
        if sign_index in [0, 4, 8]:
            start = 0
        elif sign_index in [1, 5, 9]:
            start = 9
        elif sign_index in [2, 6, 10]:
            start = 6
        else:
            start = 3
        return (start + part) % 12

    if division == 10:
        part = int(degree_in_sign // 3)
        start = sign_index if sign_index % 2 == 0 else (sign_index + 8) % 12
        return (start + part) % 12

    if division == 11:
        part = int(degree_in_sign // (30 / 11))
        return (sign_index + part) % 12

    if division == 12:
        part = int(degree_in_sign // 2.5)
        return (sign_index + part) % 12

    if division == 16:
        part = int(degree_in_sign // (30 / 16))
        if sign_index in [0, 4, 8]:
            start = 0
        elif sign_index in [1, 5, 9]:
            start = 4
        elif sign_index in [2, 6, 10]:
            start = 8
        else:
            start = 3
        return (start + part) % 12

    if division == 24:
        part = int(degree_in_sign // 1.25)
        start = 4 if sign_index % 2 == 0 else 3
        return (start + part) % 12

    if division == 30:
        d = degree_in_sign
        if sign_index % 2 == 0:
            if d < 5:
                return 0
            if d < 10:
                return 10
            if d < 18:
                return 8
            if d < 25:
                return 2
            return 6
        else:
            if d < 5:
                return 1
            if d < 12:
                return 5
            if d < 20:
                return 11
            if d < 25:
                return 9
            return 7

    if division == 60:
        part = int(degree_in_sign // 0.5)
        return (sign_index + part) % 12

    if division == 81:
        part = int(degree_in_sign // (30 / 81))
        return (sign_index * 9 + part) % 12

    part_size = 30 / division
    part_index = int(degree_in_sign // part_size)
    return int((sign_index * division + part_index) % 12)


def build_chart_view(lagna_sign_index, planets, special_points=None):
    houses = []

    if special_points is None:
        special_points = {}

    for house in range(1, 13):
        sign_index = (lagna_sign_index + house - 1) % 12
        sign_name = SIGNS[sign_index]
        sign_number = SIGN_NUMBERS[sign_name]
        house_planets = []

        for planet_name, p in planets.items():
            if p["house"] == house:
                short = PLANET_SHORT.get(planet_name, planet_name)
                karaka = p.get("karaka", "")
                label = f"{short} {karaka}".strip()
                house_planets.append(label)

        for point_name, p in special_points.items():
            if p["house"] == house:
                house_planets.append(SPECIAL_POINT_SHORT.get(point_name, point_name))

        houses.append({
            "house": house,
            "sign": sign_number,
            "sign_name": sign_name,
            "sign_index": sign_index,
            "planets": house_planets
        })

    return houses


def build_varga_chart(varga_name, division, base_planets, base_special_points, lagna_longitude, moon_longitude):
    if varga_name == "Moon":
        _, _, lagna_sign_index = get_sign_and_degree(moon_longitude)
    else:
        lagna_sign_index = get_varga_sign_index(lagna_longitude, division)

    varga_planets = {}

    for planet_name, p in base_planets.items():
        sign_index = get_varga_sign_index(p["longitude"], division)
        sign_name = SIGNS[sign_index]
        house = get_house(sign_index, lagna_sign_index)
        deg_in_sign = p["longitude"] % 30
        nak, pada, _ = get_nakshatra(p["longitude"])

        varga_planets[planet_name] = {
            "sign": sign_name,
            "sign_number": SIGN_NUMBERS[sign_name],
            "sign_index": sign_index,
            "house": house,
            "longitude": p["longitude"],
            "degree": format_degree(deg_in_sign),
            "degree_float": round(deg_in_sign, 4),
            "nakshatra": nak,
            "pada": pada,
            "karaka": p.get("karaka", "")
        }

    varga_special_points = {}

    for point_name, p in base_special_points.items():
        sign_index = get_varga_sign_index(p["longitude"], division)
        sign_name = SIGNS[sign_index]
        house = get_house(sign_index, lagna_sign_index)

        varga_special_points[point_name] = {
            "sign": sign_name,
            "sign_number": SIGN_NUMBERS[sign_name],
            "sign_index": sign_index,
            "house": house,
            "longitude": p["longitude"]
        }

    return {
        "name": varga_name,
        "division": division,
        "lagna_sign": SIGNS[lagna_sign_index],
        "lagna_sign_number": SIGN_NUMBERS[SIGNS[lagna_sign_index]],
        "lagna_sign_index": lagna_sign_index,
        "chart_view": build_chart_view(lagna_sign_index, varga_planets, varga_special_points),
        "planets": varga_planets,
        "special_points": varga_special_points,
        "aspects": calculate_parashara_aspects(varga_planets)
    }


CHARA_DIRECT_SIGNS = {0, 1, 2, 6, 7, 8}


def chara_is_direct(sign_index):
    return sign_index in CHARA_DIRECT_SIGNS


def chara_sequence_from(sign_index):
    if chara_is_direct(sign_index):
        return [(sign_index + i) % 12 for i in range(12)]

    return [(sign_index - i) % 12 for i in range(12)]


def chara_years_rao(sign_index, planets):
    lord_name = SIGN_LORDS[sign_index]

    if lord_name not in planets:
        return 1

    lord_sign_index = int(planets[lord_name]["sign_index"])

    if chara_is_direct(sign_index):
        count = ((lord_sign_index - sign_index) % 12) + 1
    else:
        count = ((sign_index - lord_sign_index) % 12) + 1

    years = count - 1

    if years <= 0:
        years = 12

    return years


def make_chara_node(sign_index, start_dt, end_dt, level, path, cycle=1):
    sign_name = SIGNS[sign_index]

    return {
        "sign": sign_name,
        "sign_number": SIGN_NUMBERS[sign_name],
        "sign_index": sign_index,
        "lord": SIGN_LORDS[sign_index],
        "start": format_date(start_dt),
        "end": format_date(end_dt),
        "is_current": period_is_current(start_dt, end_dt),
        "level": level,
        "cycle": cycle,
        "path": path,
        "path_text": " / ".join(path),
        "children": []
    }


def build_chara_children_rao(parent_start, parent_end, parent_sign_index, level, path, max_depth, cycle=1):
    total_days = (parent_end - parent_start).total_seconds() / 86400
    current_start = parent_start
    children = []
    sequence = chara_sequence_from(parent_sign_index)

    for index, sign_index in enumerate(sequence):
        # Подпериоды Чара Даши распределяются внутри периода по 12 знакам.
        # Длительность каждого подпериода пропорциональна одному делению цикла данного уровня.
        current_end = add_days(current_start, total_days / 12)

        if index == 11:
            current_end = parent_end

        sign_name = SIGNS[sign_index]
        child_path = path + [sign_name]

        node = make_chara_node(
            sign_index,
            current_start,
            current_end,
            level,
            child_path,
            cycle=cycle
        )

        if level < max_depth:
            node["children"] = build_chara_children_rao(
                current_start,
                current_end,
                sign_index,
                level + 1,
                child_path,
                max_depth,
                cycle=cycle
            )

        children.append(node)
        current_start = current_end

    return children


def find_current_chara_periods(nodes):
    active = {
        "mahadasha": None,
        "antardasha": None,
        "pratyantardasha": None,
        "path": [],
        "path_text": ""
    }

    def walk(items):
        for item in items:
            if item.get("is_current"):
                level = item.get("level")

                if level == 1:
                    active["mahadasha"] = item
                elif level == 2:
                    active["antardasha"] = item
                elif level == 3:
                    active["pratyantardasha"] = item

                walk(item.get("children", []))
                break

    walk(nodes)

    path = []

    for key in ["mahadasha", "antardasha", "pratyantardasha"]:
        if active[key]:
            path.append(active[key].get("sign"))

    active["path"] = path
    active["path_text"] = " / ".join(path)

    return active


def calculate_chara_dasha_rao(local_dt, lagna_sign_index, planets, cycles=1):
    periods = []
    current_start = local_dt.replace(tzinfo=None)
    main_sequence = chara_sequence_from(lagna_sign_index)

    for cycle_index in range(cycles):
        for sign_index in main_sequence:
            years = chara_years_rao(sign_index, planets)
            current_end = add_days(current_start, years_to_days(years))
            sign_name = SIGNS[sign_index]

            node = make_chara_node(
                sign_index,
                current_start,
                current_end,
                1,
                [sign_name],
                cycle=cycle_index + 1
            )

            node["years"] = years
            node["children"] = build_chara_children_rao(
                current_start,
                current_end,
                sign_index,
                2,
                [sign_name],
                3,
                cycle=cycle_index + 1
            )
            node["antardashas"] = node["children"]

            for antar in node["children"]:
                antar["pratyantardashas"] = antar.get("children", [])

            periods.append(node)
            current_start = current_end

    current_periods = find_current_chara_periods(periods)
    needs_next_cycle = False

    if periods:
        last_end = parse_period_date(periods[-1]["end"])
        needs_next_cycle = datetime.utcnow() >= last_end

    return {
        "system": "Чара Даша К.Н. Рао",
        "levels": 3,
        "cycles": cycles,
        "start_sign": SIGNS[lagna_sign_index],
        "current_path": current_periods["path"],
        "current_path_text": current_periods["path_text"],
        "current_periods": current_periods,
        "needs_next_cycle": needs_next_cycle,
        "tree": periods,
        "periods": periods,
        "mahadashas": periods
    }


def calculate_simple_chara_dasha(local_dt, lagna_sign_index):
    return []


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
    jd = calc_jd_from_datetime(utc_dt)

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
    lagna_nak, lagna_pada, _ = get_nakshatra(lagna_lon)

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
            "sign_number": SIGN_NUMBERS[lagna_sign],
            "sign_index": lagna_sign_index,
            "degree": format_degree(lagna_deg),
            "nakshatra": lagna_nak,
            "pada": lagna_pada,
            "longitude": round(lagna_lon, 4)
        },
        "moon": {},
        "houses": [],
        "planets": {},
        "special_points": {},
        "dashas": {},
        "chara_dasha": [],
        "chart_view": [],
        "aspects": [],
        "vargas": {},
        "transits": {},
        "calculation_debug": {
            "sidereal_mode": "Lahiri",
            "flags": "SWIEPH + SIDEREAL",
            "outer_planets": "Swiss Ephemeris sidereal Lahiri",
            "mandi_gulika": "day/night Saturn segment midpoint"
        }
    }

    for i in range(12):
        sign_index = (lagna_sign_index + i) % 12
        sign_name = SIGNS[sign_index]
        result["houses"].append({
            "house": i + 1,
            "sign": sign_name,
            "sign_number": SIGN_NUMBERS[sign_name],
            "sign_index": sign_index
        })

    rahu_pos = None
    moon_longitude = None
    sun_longitude = None

    for planet_name, planet_id in PLANETS.items():
        pos = swe.calc_ut(jd, planet_id, flags)[0][0]
        pos = normalize_degree(pos)

        if planet_name == "Раху":
            rahu_pos = pos

        if planet_name == "Луна":
            moon_longitude = pos

        if planet_name == "Солнце":
            sun_longitude = pos

        result["planets"][planet_name] = add_point_to_planets(
            planet_name,
            pos,
            lagna_sign_index
        )

        if planet_name == "Луна":
            result["moon"] = result["planets"][planet_name]

    if rahu_pos is None:
        raise ValueError("Не удалось рассчитать Раху")

    ketu_pos = normalize_degree(rahu_pos + 180)
    result["planets"]["Кету"] = add_point_to_planets(
        "Кету",
        ketu_pos,
        lagna_sign_index
    )

    result["calculation_debug"]["uranus"] = result["planets"].get("Уран", {})
    result["calculation_debug"]["neptune"] = result["planets"].get("Нептун", {})
    result["calculation_debug"]["pluto"] = result["planets"].get("Плутон", {})

    upagrahas = calculate_mandi_gulika(local_dt, lat, lon, timezone_name)

    for point_name, point_lon in upagrahas.items():
        result["planets"][point_name] = add_point_to_planets(
            point_name,
            point_lon,
            lagna_sign_index
        )

    result["calculation_debug"]["upagrahas"] = {
        point_name: result["planets"].get(point_name, {})
        for point_name in ["Манди", "Гулика"]
    }

    karakas = calculate_chara_karakas(result["planets"])

    for planet_name, karaka in karakas.items():
        result["planets"][planet_name]["karaka"] = karaka

    al_sign = calculate_arudha_for_house(1, lagna_sign_index, result["planets"])
    ul_sign = calculate_arudha_for_house(12, lagna_sign_index, result["planets"])

    if al_sign is not None:
        result["special_points"]["Арудха Лагна"] = {
            "longitude": round(al_sign * 30, 4),
            "sign_index": al_sign,
            "sign": SIGNS[al_sign],
            "sign_number": SIGN_NUMBERS[SIGNS[al_sign]],
            "house": get_house(al_sign, lagna_sign_index)
        }

    if ul_sign is not None:
        result["special_points"]["Упапада"] = {
            "longitude": round(ul_sign * 30, 4),
            "sign_index": ul_sign,
            "sign": SIGNS[ul_sign],
            "sign_number": SIGN_NUMBERS[SIGNS[ul_sign]],
            "house": get_house(ul_sign, lagna_sign_index)
        }

    sunrise_today, sunset_today = find_sunrise_sunset(math.floor(jd - 0.5) + 0.5, lat, lon)

    extra_lagnas = calculate_special_lagnas(
        lagna_lon=lagna_lon,
        moon_lon=moon_longitude,
        sun_lon=sun_longitude,
        local_dt=local_dt,
        sunrise_jd=sunrise_today,
        lat=lat,
        lon=lon
    )

    for point_name, point_data in extra_lagnas.items():
        sign_index = int(point_data["sign_index"])
        point_data["house"] = get_house(sign_index, lagna_sign_index)
        result["special_points"][point_name] = point_data

    result["aspects"] = calculate_parashara_aspects(result["planets"])

    result["chart_view"] = build_chart_view(
        lagna_sign_index,
        result["planets"],
        result["special_points"]
    )

    result["dashas"] = calculate_vimshottari_dashas(
        birth_dt=local_dt.replace(tzinfo=None),
        moon_longitude=moon_longitude
    )

    result["chara_dasha"] = calculate_chara_dasha_rao(
        local_dt=local_dt,
        lagna_sign_index=lagna_sign_index,
        planets=result["planets"],
        cycles=1
    )

    for varga_name, division in VARGAS.items():
        result["vargas"][varga_name] = build_varga_chart(
            varga_name=varga_name,
            division=division,
            base_planets=result["planets"],
            base_special_points=result["special_points"],
            lagna_longitude=lagna_lon,
            moon_longitude=moon_longitude
        )

    return result



# ============================================================
# RECTIFICATION HELPERS
# Черновой модуль ректификации внутри astro_engine.py.
# Важно: AI не считает карту. Сначала считаются реальные карты/варги/Вимшоттари,
# потом эти структурированные данные можно отдавать AI для интерпретации.
# ============================================================

RECTIFICATION_EVENT_RULES = {
    "marriage": {
        "label": "Брак / отношения",
        "vargas": ["D1", "D9"],
        "houses": [7, 2, 11],
        "karakas": ["Венера", "ДК"],
        "weight": 1.4,
    },
    "child": {
        "label": "Рождение ребёнка",
        "vargas": ["D1", "D7"],
        "houses": [5, 2, 9, 11],
        "karakas": ["Юпитер", "ПК"],
        "weight": 1.5,
    },
    "career": {
        "label": "Карьера / работа",
        "vargas": ["D1", "D10"],
        "houses": [10, 6, 2, 11],
        "karakas": ["Сатурн", "Солнце", "АмК"],
        "weight": 1.3,
    },
    "education": {
        "label": "Образование / обучение",
        "vargas": ["D1", "D24"],
        "houses": [4, 5, 9],
        "karakas": ["Меркурий", "Юпитер"],
        "weight": 1.2,
    },
    "relocation": {
        "label": "Переезд",
        "vargas": ["D1"],
        "houses": [4, 9, 12],
        "karakas": ["Луна", "Раху"],
        "weight": 1.2,
    },
    "illness": {
        "label": "Болезнь / операция",
        "vargas": ["D1", "D30"],
        "houses": [6, 8, 12],
        "karakas": ["Марс", "Сатурн"],
        "weight": 1.3,
    },
    "divorce": {
        "label": "Развод / разрыв отношений",
        "vargas": ["D1", "D9"],
        "houses": [6, 7, 8, 12],
        "karakas": ["Венера", "ДК", "Раху", "Кету"],
        "weight": 1.25,
    },
    "other": {
        "label": "Другое важное событие",
        "vargas": ["D1"],
        "houses": [1, 4, 7, 10],
        "karakas": [],
        "weight": 0.7,
    },
}


def _rectification_parse_time(value):
    value = str(value or "").strip()
    parts = value.split(":")
    if len(parts) == 2:
        value = value + ":00"
    return datetime.strptime(value, "%H:%M:%S").time()


def generate_rectification_times(date_str, start_time, end_time, step_minutes=15):
    birth_date = parse_date(date_str)
    start = datetime.combine(birth_date, _rectification_parse_time(start_time))
    end = datetime.combine(birth_date, _rectification_parse_time(end_time))

    if end < start:
        raise ValueError("Конец диапазона времени не может быть раньше начала")

    step_minutes = int(step_minutes or 15)
    if step_minutes < 1:
        step_minutes = 15
    if step_minutes > 60:
        step_minutes = 60

    result = []
    current = start
    while current <= end:
        result.append(current.strftime("%H:%M:%S"))
        current += timedelta(minutes=step_minutes)
    return result


def _get_period_on_date(nodes, target_dt, level=1):
    for node in nodes or []:
        try:
            start = parse_period_date(node.get("start"))
            end = parse_period_date(node.get("end"))
        except Exception:
            continue
        if start <= target_dt < end:
            item = {
                "lord": node.get("lord") or node.get("sign") or node.get("name"),
                "start": node.get("start"),
                "end": node.get("end"),
                "level": level,
            }
            child = _get_period_on_date(node.get("children", []), target_dt, level + 1)
            if child:
                if isinstance(child, list):
                    return [item] + child
                return [item, child]
            return [item]
    return []


def get_vimshottari_path_on_date(chart, event_date):
    try:
        target_dt = parse_date(event_date)
        target_dt = datetime.combine(target_dt, datetime.min.time())
    except Exception:
        return []
    dashas = chart.get("dashas", {}) or {}
    return _get_period_on_date(dashas.get("tree") or dashas.get("mahadashas") or [], target_dt, 1)


def summarize_rectification_chart(chart):
    vargas = chart.get("vargas", {}) or {}
    planets = chart.get("planets", {}) or {}

    return {
        "time": chart.get("input_time"),
        "lagna": chart.get("lagna", {}),
        "varga_lagnas": {
            name: {
                "lagna_sign": data.get("lagna_sign"),
                "lagna_sign_number": data.get("lagna_sign_number"),
                "lagna_sign_index": data.get("lagna_sign_index"),
            }
            for name, data in vargas.items()
            if name in ["D1", "D4", "D7", "D9", "D10", "D24", "D30"]
        },
        "karakas": {
            planet: info.get("karaka")
            for planet, info in planets.items()
            if info.get("karaka")
        },
        "active_vimshottari_now": chart.get("dashas", {}).get("current_path_text"),
    }


def _score_event_against_chart(chart, event):
    event_type = str(event.get("type") or "").strip()
    rule = RECTIFICATION_EVENT_RULES.get(event_type)
    if not rule:
        return {
            "event": event,
            "score": 0,
            "details": ["Неизвестный тип события"],
        }

    details = []
    score = 0.0

    # 1) Проверяем, что нужные дробные карты есть и имеют лагну.
    vargas = chart.get("vargas", {}) or {}
    present = []
    for varga_name in rule["vargas"]:
        if varga_name == "D1":
            if chart.get("lagna"):
                present.append(varga_name)
        elif vargas.get(varga_name, {}).get("lagna_sign"):
            present.append(varga_name)

    if present:
        score += 10 * len(present)
        details.append("Есть нужные карты: " + ", ".join(present))

    # 2) Проверяем Вимшоттари на дату события: участвует ли карака события в пути периода.
    path = get_vimshottari_path_on_date(chart, event.get("date"))
    lords = [p.get("lord") for p in path if p.get("lord")]
    if lords:
        details.append("Вимшоттари на дату события: " + " / ".join(lords))
        karaka_planets = [k for k in rule.get("karakas", []) if k in PLANETS or k in ["Раху", "Кету"]]
        if any(lord in karaka_planets for lord in lords):
            score += 25
            details.append("Период включает планету-караку события")
        else:
            score += 8
            details.append("Период найден, но прямой караки в периоде нет")

    # 3) Проверяем дома планет периода в D1.
    planets = chart.get("planets", {}) or {}
    relevant_houses = set(rule.get("houses", []))
    activated = []
    for lord in lords:
        p = planets.get(lord)
        if p and p.get("house") in relevant_houses:
            activated.append(f"{lord} в {p.get('house')} доме")
    if activated:
        score += 25
        details.append("Активированы дома события: " + "; ".join(activated))

    return {
        "event": event,
        "event_label": rule.get("label"),
        "score": round(score * rule.get("weight", 1), 2),
        "vimshottari_path": lords,
        "details": details,
    }


def detect_rectification_corridors(variants):
    corridors = []
    last_key = None
    current = None

    for item in variants:
        summary = item.get("summary", {})
        lagnas = summary.get("varga_lagnas", {})
        key = tuple((name, lagnas.get(name, {}).get("lagna_sign")) for name in ["D1", "D4", "D9", "D7", "D10", "D24"])

        if key != last_key:
            if current:
                corridors.append(current)
            current = {
                "start_time": item.get("time"),
                "end_time": item.get("time"),
                "varga_lagnas": {name: lagnas.get(name, {}).get("lagna_sign") for name in ["D1", "D4", "D9", "D7", "D10", "D24"]},
                "times": [item.get("time")],
            }
            last_key = key
        else:
            current["end_time"] = item.get("time")
            current["times"].append(item.get("time"))

    if current:
        corridors.append(current)

    return corridors


def calculate_rectification_range(date_str, start_time, end_time, city, life_events=None, step_minutes=15, lat=None, lon=None, display_name=None):
    """
    Перебирает время рождения в заданном диапазоне, строит настоящие карты через calculate_chart,
    фиксирует лагны D1/D9/D7/D10/D24 и даёт предварительный скоринг по событиям.

    ВАЖНО: это функциональный MVP ректификации. Он уже работает технически,
    но качество вывода зависит от правильности расчёта варг и правил скоринга.
    """
    times = generate_rectification_times(date_str, start_time, end_time, step_minutes)
    life_events = life_events or []

    if len(times) > 60:
        raise ValueError(
            "Слишком большой диапазон для ректификации. "
            "Уменьшите коридор времени или увеличьте шаг проверки. Максимум 60 вариантов за один запуск."
        )

    normalized_events = []
    for event in life_events:
        if not isinstance(event, dict):
            continue
        event_type = str(event.get("type") or "other").strip().lower()
        if event_type not in RECTIFICATION_EVENT_RULES:
            event_type = "other"
        normalized_events.append({
            "type": event_type,
            "date": event.get("date"),
            "description": event.get("description") or event.get("name") or "",
        })

    variants = []
    chronological_variants = []

    for time_str in times:
        chart = calculate_chart(
            date_str=date_str,
            time_str=time_str,
            city=city,
            lat=lat,
            lon=lon,
            display_name=display_name,
        )
        event_scores = [_score_event_against_chart(chart, event) for event in normalized_events]
        total_score = round(sum(item.get("score", 0) for item in event_scores), 2)
        summary = summarize_rectification_chart(chart)

        item = {
            "time": time_str,
            "total_score": total_score,
            "summary": summary,
            "event_scores": event_scores,
        }
        variants.append(item)
        chronological_variants.append(item)

    scored_variants = sorted(variants, key=lambda x: x.get("total_score", 0), reverse=True)
    corridors = detect_rectification_corridors(chronological_variants)

    # Добавляем средний балл по каждому коридору, чтобы было видно не только отдельное время,
    # но и устойчивый временной промежуток с совпадающими дробными лагнами.
    score_by_time = {item.get("time"): item.get("total_score", 0) for item in chronological_variants}
    for corridor in corridors:
        scores = [score_by_time.get(t, 0) for t in corridor.get("times", [])]
        corridor["average_score"] = round(sum(scores) / len(scores), 2) if scores else 0
        corridor["max_score"] = round(max(scores), 2) if scores else 0

    corridors_by_score = sorted(corridors, key=lambda x: x.get("average_score", 0), reverse=True)

    best = scored_variants[0] if scored_variants else None
    second_score = scored_variants[1].get("total_score", 0) if len(scored_variants) > 1 else 0
    confidence = 0
    if best and best.get("total_score", 0) > 0:
        gap = best.get("total_score", 0) - second_score
        confidence = 85 if gap >= 35 else 70 if gap >= 20 else 55 if gap >= 8 else 40

    return {
        "status": "success",
        "date": date_str,
        "city": display_name or city,
        "step_minutes": step_minutes,
        "events": normalized_events,
        "variants_count": len(times),
        "best_time": best.get("time") if best else None,
        "best_score": best.get("total_score") if best else 0,
        "confidence": confidence,
        "top_variants": scored_variants[:10],
        "corridors": corridors,
        "best_corridors": corridors_by_score[:6],
        "ai_payload": {
            "task": "rectification_analysis",
            "instruction": "Не пересчитывай карту. Анализируй только переданные варианты, варги, Вимшоттари и события.",
            "best_time": best.get("time") if best else None,
            "confidence": confidence,
            "top_variants": scored_variants[:5],
            "best_corridors": corridors_by_score[:6],
            "corridors": corridors,
        }
    }
