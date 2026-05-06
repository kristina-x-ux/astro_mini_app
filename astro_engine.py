import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
import pytz
import math


SIGNS = [
    "Овен",
    "Телец",
    "Близнецы",
    "Рак",
    "Лев",
    "Дева",
    "Весы",
    "Скорпион",
    "Стрелец",
    "Козерог",
    "Водолей",
    "Рыбы"
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


NAKSHATRAS = [
    "Ашвини",
    "Бхарани",
    "Криттика",
    "Рохини",
    "Мригашира",
    "Ардра",
    "Пунарвасу",
    "Пушья",
    "Ашлеша",
    "Магха",
    "Пурва Пхалгуни",
    "Уттара Пхалгуни",
    "Хаста",
    "Читра",
    "Свати",
    "Вишакха",
    "Анурадха",
    "Джйештха",
    "Мула",
    "Пурва Ашадха",
    "Уттара Ашадха",
    "Шравана",
    "Дхаништха",
    "Шатабхиша",
    "Пурва Бхадрапада",
    "Уттара Бхадрапада",
    "Ревати"
]


NAKSHATRA_LORDS = [
    "Кету", "Венера", "Солнце",
    "Луна", "Марс", "Раху",
    "Юпитер", "Сатурн", "Меркурий",

    "Кету", "Венера", "Солнце",
    "Луна", "Марс", "Раху",
    "Юпитер", "Сатурн", "Меркурий",

    "Кету", "Венера", "Солнце",
    "Луна", "Марс", "Раху",
    "Юпитер", "Сатурн", "Меркурий"
]


DASHA_ORDER = [
    "Кету",
    "Венера",
    "Солнце",
    "Луна",
    "Марс",
    "Раху",
    "Юпитер",
    "Сатурн",
    "Меркурий"
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


PLANET_ORDER = [
    "Асцендент",
    "Солнце",
    "Луна",
    "Марс",
    "Меркурий",
    "Венера",
    "Сатурн",
    "Юпитер",
    "Раху",
    "Кету",
    "Плутон",
    "Нептун",
    "Уран",
    "Манди",
    "Гулика"
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

    "Уран": swe.URANUS,
    "Нептун": swe.NEPTUNE,
    "Плутон": swe.PLUTO
}


PLANET_SHORT = {
    "Солнце": "Su",
    "Луна": "Mo",
    "Марс": "Ma",
    "Меркурий": "Me",
    "Юпитер": "Ju",
    "Венера": "Ve",
    "Сатурн": "Sa",
    "Раху": "Ra",
    "Кету": "Ke",
    "Уран": "Ur",
    "Нептун": "Ne",
    "Плутон": "Pl",
    "Манди": "Gu",
    "Гулика": "Md"
}


KARAKA_NAMES = [
    "АК",
    "АмК",
    "БК",
    "МК",
    "ПК",
    "ГК",
    "ДК"
]


VARGAS = {
    "D1": 1,
    "Moon": 1,
    "D2": 2,
    "D3": 3,
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
    "ялта": (44.4952, 34.1663, "Ялта"),
    "москва": (55.7558, 37.6173, "Москва"),
    "рига": (56.9496, 24.1052, "Рига"),
    "алматы": (43.2389, 76.8897, "Алматы")
}


def normalize_degree(deg):
    return deg % 360


def parse_date(date_str):
    return datetime.strptime(date_str, "%d.%m.%Y").date()


def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M:%S").time()


def format_degree(deg):
    degree = int(deg)
    minute = int((deg - degree) * 60)
    second = int((((deg - degree) * 60) - minute) * 60)

    return f"{degree}°{minute:02d}'{second:02d}\""


def get_sign_and_degree(lon):
    lon = normalize_degree(lon)

    sign_index = int(lon // 30)
    degree_in_sign = lon % 30

    return SIGNS[sign_index], degree_in_sign, sign_index


def get_nakshatra(lon):
    nak_size = 360 / 27
    pada_size = nak_size / 4

    nak_index = int(lon // nak_size)

    degree_in_nak = lon % nak_size
    pada = int(degree_in_nak // pada_size) + 1

    return (
        NAKSHATRAS[nak_index],
        pada,
        nak_index
    )


def get_house(sign_index, lagna_sign_index):
    return ((sign_index - lagna_sign_index) % 12) + 1


def short_place_name(location):
    address = location.raw.get("address", {})

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or ""
    )

    country = address.get("country") or ""

    if city and country:
        return f"{city}, {country}"

    return location.address


def search_places(query):
    query = query.strip()

    if len(query) < 2:
        return []

    results = []

    geolocator = Nominatim(
        user_agent="astroengine"
    )

    locations = geolocator.geocode(
        query,
        exactly_one=False,
        limit=5,
        language="ru",
        addressdetails=True,
        timeout=10
    )

    if locations:
        for loc in locations:
            results.append({
                "name": short_place_name(loc),
                "lat": loc.latitude,
                "lon": loc.longitude
            })

    return results


def get_coordinates(city, lat=None, lon=None, display_name=None):
    if lat is not None and lon is not None:
        return float(lat), float(lon), display_name or city

    city_clean = city.strip().lower()

    if city_clean in CITY_FALLBACK:
        lat, lon, title = CITY_FALLBACK[city_clean]
        return lat, lon, title

    geolocator = Nominatim(
        user_agent="astroengine"
    )

    location = geolocator.geocode(
        city,
        language="ru",
        timeout=10,
        addressdetails=True
    )

    if not location:
        raise ValueError(
            "Место не найдено"
        )

    return (
        location.latitude,
        location.longitude,
        short_place_name(location)
    )


def get_timezone(lat, lon):
    tf = TimezoneFinder()

    timezone_name = tf.timezone_at(
        lat=lat,
        lng=lon
    )

    if not timezone_name:
        raise ValueError(
            "Не удалось определить часовой пояс"
        )

    return timezone_name


def get_utc_offset_string(local_dt):
    offset = local_dt.utcoffset()

    total_seconds = int(offset.total_seconds())
    hours = total_seconds // 3600

    if hours >= 0:
        return f"+{hours}"

    return str(hours)


def calculate_chara_karakas(planets):
    main_planets = [
        "Солнце",
        "Луна",
        "Марс",
        "Меркурий",
        "Юпитер",
        "Венера",
        "Сатурн"
    ]

    sortable = []

    for name in main_planets:
        longitude = planets[name]["longitude"]
        degree_in_sign = longitude % 30

        sortable.append((
            name,
            degree_in_sign
        ))

    sortable.sort(
        key=lambda x: x[1],
        reverse=True
    )

    result = {}

    for i, item in enumerate(sortable):
        result[item[0]] = KARAKA_NAMES[i]

    return result


def calculate_parashara_aspects(planets):
    aspects = []

    for name, p in planets.items():

        if name in [
            "Плутон",
            "Нептун",
            "Уран",
            "Манди",
            "Гулика"
        ]:
            continue

        from_house = p["house"]

        houses = []

        houses.append(
            ((from_house + 6 - 1) % 12) + 1
        )

        if name == "Марс":
            houses.extend([
                ((from_house + 3 - 1) % 12) + 1,
                ((from_house + 7 - 1) % 12) + 1
            ])

        if name == "Юпитер":
            houses.extend([
                ((from_house + 4 - 1) % 12) + 1,
                ((from_house + 8 - 1) % 12) + 1
            ])

        if name == "Сатурн":
            houses.extend([
                ((from_house + 2 - 1) % 12) + 1,
                ((from_house + 9 - 1) % 12) + 1
            ])

        if name in ["Раху", "Кету"]:
            houses.extend([
                ((from_house + 4 - 1) % 12) + 1,
                ((from_house + 8 - 1) % 12) + 1
            ])

        aspects.append({
            "planet": name,
            "from_house": from_house,
            "aspects_houses": sorted(
                list(set(houses))
            )
        })

    return aspects


def calculate_vimshottari_dashas(
    birth_dt,
    moon_longitude
):
    nak_size = 360 / 27

    nak_index = int(
        moon_longitude // nak_size
    )

    degree_in_nak = moon_longitude % nak_size

    start_lord = NAKSHATRA_LORDS[nak_index]

    completed_fraction = (
        degree_in_nak / nak_size
    )

    remaining_fraction = (
        1 - completed_fraction
    )

    current_start = birth_dt

    result = []

    first_years = (
        DASHA_YEARS[start_lord]
        * remaining_fraction
    )

    start_index = DASHA_ORDER.index(
        start_lord
    )

    ordered = (
        DASHA_ORDER[start_index:]
        + DASHA_ORDER[:start_index]
    )

    for i, lord in enumerate(ordered):

        years = (
            first_years
            if i == 0
            else DASHA_YEARS[lord]
        )

        current_end = (
            current_start
            + timedelta(days=years * 365.2425)
        )

        result.append({
            "lord": lord,
            "start": current_start.strftime("%d.%m.%Y"),
            "end": current_end.strftime("%d.%m.%Y")
        })

        current_start = current_end

    return {
        "birth_lord": start_lord,
        "mahadashas": result
    }


def build_chart_view(
    lagna_sign_index,
    planets
):
    houses = []

    for house in range(1, 13):

        sign_index = (
            lagna_sign_index
            + house
            - 1
        ) % 12

        sign_name = SIGNS[sign_index]

        house_planets = []

        for planet_name in PLANET_ORDER:

            if planet_name not in planets:
                continue

            p = planets[planet_name]

            if p["house"] == house:

                label = PLANET_SHORT.get(
                    planet_name,
                    planet_name
                )

                if p.get("retro"):
                    label = f"({label})"

                house_planets.append(label)

        houses.append({
            "house": house,
            "sign": SIGN_NUMBERS[sign_name],
            "sign_name": sign_name,
            "planets": house_planets
        })

    return houses


def calculate_chart(
    date_str,
    time_str,
    city,
    lat=None,
    lon=None,
    display_name=None
):
    birth_date = parse_date(date_str)
    birth_time = parse_time(time_str)

    lat, lon, display_city = get_coordinates(
        city,
        lat,
        lon,
        display_name
    )

    timezone_name = get_timezone(
        lat,
        lon
    )

    local_tz = pytz.timezone(
        timezone_name
    )

    local_dt = local_tz.localize(
        datetime.combine(
            birth_date,
            birth_time
        )
    )

    utc_dt = local_dt.astimezone(
        pytz.utc
    )

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

    swe.set_sid_mode(
        swe.SIDM_LAHIRI
    )

    flags = (
        swe.FLG_SWIEPH
        | swe.FLG_SIDEREAL
    )

    houses, ascmc = swe.houses_ex(
        jd,
        lat,
        lon,
        b'P',
        flags
    )

    lagna_lon = normalize_degree(
        ascmc[0]
    )

    lagna_sign, lagna_deg, lagna_sign_index = (
        get_sign_and_degree(lagna_lon)
    )

    lagna_nak, lagna_pada, _ = (
        get_nakshatra(lagna_lon)
    )

    result = {
        "input_date": birth_date.strftime("%d.%m.%Y"),
        "input_time": birth_time.strftime("%H:%M:%S"),
        "city": display_city,
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "timezone": timezone_name,
        "utc_offset": get_utc_offset_string(local_dt),
        "ayanamsha": round(
            swe.get_ayanamsa_ut(jd),
            4
        ),

        "lagna": {
            "sign": lagna_sign,
            "degree": format_degree(lagna_deg),
            "nakshatra": lagna_nak,
            "pada": lagna_pada,
            "longitude": lagna_lon
        },

        "planets": {},
        "chart_view": [],
        "dashas": {},
        "aspects": []
    }

    moon_longitude = None
    rahu_longitude = None

    for planet_name in PLANET_ORDER:

        if planet_name in [
            "Асцендент",
            "Кету",
            "Манди",
            "Гулика"
        ]:
            continue

        if planet_name not in PLANETS:
            continue

        planet_id = PLANETS[planet_name]

        calc = swe.calc_ut(
            jd,
            planet_id,
            flags
        )

        pos = normalize_degree(
            calc[0][0]
        )

        speed = calc[0][3]

        retro = speed < 0

        if planet_name == "Раху":
            rahu_longitude = pos

        sign, deg_in_sign, sign_index = (
            get_sign_and_degree(pos)
        )

        nak, pada, _ = (
            get_nakshatra(pos)
        )

        house = get_house(
            sign_index,
            lagna_sign_index
        )

        result["planets"][planet_name] = {
            "sign": sign,
            "degree": format_degree(deg_in_sign),
            "degree_float": round(
                deg_in_sign,
                4
            ),
            "nakshatra": nak,
            "pada": pada,
            "house": house,
            "longitude": round(pos, 6),
            "retro": retro,
            "karaka": ""
        }

        if planet_name == "Луна":
            moon_longitude = pos

    ketu_longitude = normalize_degree(
        rahu_longitude + 180
    )

    sign, deg_in_sign, sign_index = (
        get_sign_and_degree(ketu_longitude)
    )

    nak, pada, _ = (
        get_nakshatra(ketu_longitude)
    )

    result["planets"]["Кету"] = {
        "sign": sign,
        "degree": format_degree(deg_in_sign),
        "degree_float": round(
            deg_in_sign,
            4
        ),
        "nakshatra": nak,
        "pada": pada,
        "house": get_house(
            sign_index,
            lagna_sign_index
        ),
        "longitude": round(
            ketu_longitude,
            6
        ),
        "retro": True,
        "karaka": ""
    }

    gulika_longitude = normalize_degree(
        lagna_lon + 90
    )

    mandi_longitude = normalize_degree(
        lagna_lon + 120
    )

    for special_name, special_lon in [
        ("Гулика", gulika_longitude),
        ("Манди", mandi_longitude)
    ]:

        sign, deg_in_sign, sign_index = (
            get_sign_and_degree(
                special_lon
            )
        )

        nak, pada, _ = (
            get_nakshatra(
                special_lon
            )
        )

        result["planets"][special_name] = {
            "sign": sign,
            "degree": format_degree(deg_in_sign),
            "degree_float": round(
                deg_in_sign,
                4
            ),
            "nakshatra": nak,
            "pada": pada,
            "house": get_house(
                sign_index,
                lagna_sign_index
            ),
            "longitude": round(
                special_lon,
                6
            ),
            "retro": False,
            "karaka": ""
        }

    karakas = calculate_chara_karakas(
        result["planets"]
    )

    for planet_name, karaka in karakas.items():
        result["planets"][planet_name]["karaka"] = karaka

    result["chart_view"] = build_chart_view(
        lagna_sign_index,
        result["planets"]
    )

    result["dashas"] = calculate_vimshottari_dashas(
        birth_dt=local_dt.replace(
            tzinfo=None
        ),
        moon_longitude=moon_longitude
    )

    result["aspects"] = calculate_parashara_aspects(
        result["planets"]
    )

    return result
