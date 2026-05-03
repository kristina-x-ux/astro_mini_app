from datetime import datetime
import swisseph as swe
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

swe.set_ephe_path(".")
swe.set_sid_mode(swe.SIDM_LAHIRI)

ЗНАКИ = [
    "Овен","Телец","Близнецы","Рак","Лев","Дева",
    "Весы","Скорпион","Стрелец","Козерог","Водолей","Рыбы"
]

SIGN_LORDS = {
    "Овен":"Марс","Телец":"Венера","Близнецы":"Меркурий","Рак":"Луна",
    "Лев":"Солнце","Дева":"Меркурий","Весы":"Венера","Скорпион":"Марс",
    "Стрелец":"Юпитер","Козерог":"Сатурн","Водолей":"Сатурн","Рыбы":"Юпитер"
}

НАКШАТРЫ = [
    "Ашвини","Бхарани","Криттика","Рохини","Мригашира","Ардра",
    "Пунарвасу","Пушья","Ашлеша","Магха","Пурва Пхалгуни","Уттара Пхалгуни",
    "Хаста","Читра","Свати","Вишакха","Анурадха","Джйештха",
    "Мула","Пурва Ашадха","Уттара Ашадха","Шравана","Дхаништха",
    "Шатабхиша","Пурва Бхадрапада","Уттара Бхадрапада","Ревати"
]

ПЛАНЕТЫ = {
    "Солнце": swe.SUN,
    "Луна": swe.MOON,
    "Марс": swe.MARS,
    "Меркурий": swe.MERCURY,
    "Юпитер": swe.JUPITER,
    "Венера": swe.VENUS,
    "Сатурн": swe.SATURN,
    "Раху": swe.MEAN_NODE
}

def нормализовать_степень(x):
    return x % 360

def формат_градус(x):
    град = int(x)
    мин = int((x - град) * 60)
    return f"{град}°{мин:02d}'"

def get_sign_data(lon):
    lon = нормализовать_степень(lon)
    sign_index = int(lon // 30)
    degree = lon % 30
    return {
        "sign_index": sign_index,
        "sign": ЗНАКИ[sign_index],
        "degree": degree,
        "full_text": f"{ЗНАКИ[sign_index]} {формат_градус(degree)}"
    }

def get_nakshatra_data(lon):
    lon = нормализовать_степень(lon)
    nak_size = 360 / 27
    pada_size = nak_size / 4

    nak_index = int(lon // nak_size)
    degree_in_nak = lon % nak_size
    pada = int(degree_in_nak // pada_size) + 1

    return {
        "nakshatra": НАКШАТРЫ[nak_index],
        "pada": pada
    }

def получить_координаты(город):
    geolocator = Nominatim(user_agent="astro_bot")
    location = geolocator.geocode(город)

    if not location:
        raise ValueError("Город не найден")

    return location.latitude, location.longitude

def get_timezone(lat, lon):
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=lat, lng=lon)

    if not tz:
        raise ValueError("Часовой пояс не найден")

    return tz

def calculate_chart(date_str, time_str, city):

    lat, lon = получить_координаты(city)
    timezone_name = get_timezone(lat, lon)

    local_tz = pytz.timezone(timezone_name)

    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt_local = local_tz.localize(dt)
    dt_utc = dt_local.astimezone(pytz.utc)

    jd = swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60
    )

    ayanamsha = swe.get_ayanamsa_ut(jd)

    houses_data = swe.houses_ex(jd, lat, lon, b'P')
    asc = нормализовать_степень(houses_data[0][0])

    lagna_sign = get_sign_data(asc)
    lagna_nak = get_nakshatra_data(asc)

    # 🏠 ДОМА
    houses = {}

    for i in range(12):
        sign_index = (lagna_sign["sign_index"] + i) % 12
        sign = ЗНАКИ[sign_index]

        houses[i+1] = {
            "sign": sign,
            "lord": SIGN_LORDS[sign]
        }

    # 🪐 ПЛАНЕТЫ
    planets = {}

    for name, code in ПЛАНЕТЫ.items():
        lon_p = нормализовать_степень(swe.calc_ut(jd, code)[0][0])

        sign_data = get_sign_data(lon_p)
        nak_data = get_nakshatra_data(lon_p)

        house = ((sign_data["sign_index"] - lagna_sign["sign_index"]) % 12) + 1

        planets[name] = {
            "degree": формат_градус(sign_data["degree"]),
            "nakshatra": nak_data["nakshatra"],
            "pada": nak_data["pada"],
            "house": house
        }

    # КЕТУ
    rahu_deg = planets["Раху"]
    ketu_lon = нормализовать_степень(swe.calc_ut(jd, swe.MEAN_NODE)[0][0] + 180)

    sign_data = get_sign_data(ketu_lon)
    nak_data = get_nakshatra_data(ketu_lon)

    house = ((sign_data["sign_index"] - lagna_sign["sign_index"]) % 12) + 1

    planets["Кету"] = {
        "degree": формат_градус(sign_data["degree"]),
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
        "ayanamsha": round(ayanamsha, 3),

        "lagna_full_text": lagna_sign["full_text"],
        "lagna_nakshatra": lagna_nak["nakshatra"],
        "lagna_pada": lagna_nak["pada"],

        "houses": houses,
        "planets": planets
    }
