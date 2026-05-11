# ============================================================
# VARGA ENGINE
# Правильный расчёт дробных карт для AstroEngine
# D1, D7, D9, D10, D24
# ============================================================

SIGNS = [
    "Овен", "Телец", "Близнецы", "Рак",
    "Лев", "Дева", "Весы", "Скорпион",
    "Стрелец", "Козерог", "Водолей", "Рыбы"
]


def normalize_degree(degree):
    return degree % 360


def get_sign_index(longitude):
    return int(normalize_degree(longitude) // 30)


def get_sign_name(sign_index):
    return SIGNS[sign_index % 12]


def get_degree_in_sign(longitude):
    return normalize_degree(longitude) % 30


def get_d1_sign(longitude):
    sign_index = get_sign_index(longitude)
    return {
        "sign_index": sign_index,
        "sign": get_sign_name(sign_index),
        "degree_in_sign": round(get_degree_in_sign(longitude), 6),
    }


# ============================================================
# D9 NAVAMSHA
# Каждый знак делится на 9 частей по 3°20'
# Подвижные знаки: от себя
# Фиксированные: от 9-го от себя
# Двойственные: от 5-го от себя
# ============================================================

def get_d9_sign(longitude):
    sign_index = get_sign_index(longitude)
    degree = get_degree_in_sign(longitude)

    part = int(degree / (30 / 9))

    if sign_index in [0, 3, 6, 9]:
        start = sign_index
    elif sign_index in [1, 4, 7, 10]:
        start = (sign_index + 8) % 12
    else:
        start = (sign_index + 4) % 12

    d9_index = (start + part) % 12

    return {
        "sign_index": d9_index,
        "sign": get_sign_name(d9_index),
        "part": part + 1,
    }


# ============================================================
# D7 SAPTAMSHA
# Каждый знак делится на 7 частей
# Нечётные знаки: от самого знака
# Чётные знаки: от 7-го от знака
# ============================================================

def get_d7_sign(longitude):
    sign_index = get_sign_index(longitude)
    degree = get_degree_in_sign(longitude)

    part = int(degree / (30 / 7))

    if sign_index % 2 == 0:
        start = sign_index
    else:
        start = (sign_index + 6) % 12

    d7_index = (start + part) % 12

    return {
        "sign_index": d7_index,
        "sign": get_sign_name(d7_index),
        "part": part + 1,
    }


# ============================================================
# D10 DASHAMSHA
# Каждый знак делится на 10 частей по 3°
# Нечётные знаки: от самого знака
# Чётные знаки: от 9-го от знака
# ============================================================

def get_d10_sign(longitude):
    sign_index = get_sign_index(longitude)
    degree = get_degree_in_sign(longitude)

    part = int(degree / 3)

    if sign_index % 2 == 0:
        start = sign_index
    else:
        start = (sign_index + 8) % 12

    d10_index = (start + part) % 12

    return {
        "sign_index": d10_index,
        "sign": get_sign_name(d10_index),
        "part": part + 1,
    }


# ============================================================
# D24 SIDDHAMSHA / CHATURVIMSHAMSHA
# Каждый знак делится на 24 части по 1°15'
# Нечётные знаки: от Льва
# Чётные знаки: от Рака
# ============================================================

def get_d24_sign(longitude):
    sign_index = get_sign_index(longitude)
    degree = get_degree_in_sign(longitude)

    part = int(degree / (30 / 24))

    if sign_index % 2 == 0:
        start = 4  # Лев
    else:
        start = 3  # Рак

    d24_index = (start + part) % 12

    return {
        "sign_index": d24_index,
        "sign": get_sign_name(d24_index),
        "part": part + 1,
    }


# ============================================================
# Общая функция расчёта одной планеты/лагны во всех варгах
# ============================================================

def calculate_vargas_for_longitude(longitude):
    return {
        "D1": get_d1_sign(longitude),
        "D7": get_d7_sign(longitude),
        "D9": get_d9_sign(longitude),
        "D10": get_d10_sign(longitude),
        "D24": get_d24_sign(longitude),
    }


def calculate_all_vargas(points):
    """
    points пример:
    {
        "Лагна": 118.25,
        "Солнце": 41.2,
        "Луна": 250.1
    }
    """

    result = {}

    for name, longitude in points.items():
        result[name] = calculate_vargas_for_longitude(longitude)

    return result
