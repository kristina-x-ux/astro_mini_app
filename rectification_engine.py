from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


# ============================================================
# RECTIFICATION ENGINE
# Модуль ректификации времени рождения для AstroEngine
# ============================================================


SUPPORTED_VARGAS = ["D1", "D9", "D7", "D10", "D24"]


EVENT_RULES = {
    "marriage": {
        "label": "Брак / серьёзные отношения",
        "main_vargas": ["D1", "D9"],
        "houses": [7, 2, 11],
        "karakas": ["Венера", "Даракарака"],
        "weight": 1.4,
    },
    "child": {
        "label": "Рождение ребёнка",
        "main_vargas": ["D1", "D7"],
        "houses": [5, 2, 9, 11],
        "karakas": ["Юпитер", "Путракарака"],
        "weight": 1.5,
    },
    "career": {
        "label": "Карьера / работа / статус",
        "main_vargas": ["D1", "D10"],
        "houses": [10, 6, 2, 11],
        "karakas": ["Сатурн", "Солнце", "Аматьякарака"],
        "weight": 1.3,
    },
    "education": {
        "label": "Образование / обучение",
        "main_vargas": ["D1", "D24"],
        "houses": [4, 5, 9],
        "karakas": ["Меркурий", "Юпитер"],
        "weight": 1.2,
    },
    "relocation": {
        "label": "Переезд",
        "main_vargas": ["D1", "D4"],
        "houses": [4, 9, 12],
        "karakas": ["Луна", "Раху"],
        "weight": 1.2,
    },
    "illness": {
        "label": "Болезнь / операция",
        "main_vargas": ["D1", "D30"],
        "houses": [6, 8, 12],
        "karakas": ["Марс", "Сатурн"],
        "weight": 1.3,
    },
}


# ============================================================
# 1. Генератор вариантов времени
# ============================================================

def generate_time_variants(
    birth_date: str,
    start_time: str,
    end_time: str,
    step_minutes: int = 15
) -> List[datetime]:
    """
    Создаёт список возможных времён рождения внутри заданного диапазона.

    birth_date: '1990-05-16'
    start_time: '06:00'
    end_time: '09:00'
    step_minutes: 10 или 15
    """

    start_dt = datetime.strptime(f"{birth_date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{birth_date} {end_time}", "%Y-%m-%d %H:%M")

    variants = []
    current = start_dt

    while current <= end_dt:
        variants.append(current)
        current += timedelta(minutes=step_minutes)

    return variants


# ============================================================
# 2. Заглушка под расчёт карт
# Потом сюда подключим твой astro_engine.py
# ============================================================

def calculate_variant_charts(
    birth_dt: datetime,
    place_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Здесь позже будет реальный расчёт через AstroEngine.

    Должно возвращать:
    - D1
    - D9
    - D7
    - D10
    - D24
    - даши
    - чаракараки
    - хозяева домов
    """

    return {
        "birth_time": birth_dt.strftime("%H:%M"),
        "datetime": birth_dt.isoformat(),
        "place": place_data,

        "vargas": {
            "D1": {},
            "D9": {},
            "D7": {},
            "D10": {},
            "D24": {},
        },

        "dashas": {
            "vimshottari": [],
            "chara_dasha": [],
        },

        "meta": {
            "lagna": None,
            "lagna_degree": None,
            "moon_nakshatra": None,
        }
    }


# ============================================================
# 3. Определение коридоров дробных карт
# ============================================================

def detect_varga_corridors(
    calculated_variants: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Группирует соседние варианты времени, где дробные карты совпадают.

    Например:
    06:00–06:20 одна D9,
    06:20–06:40 другая D9.
    """

    corridors = []

    for variant in calculated_variants:
        corridors.append({
            "time": variant["birth_time"],
            "d1_lagna": get_varga_lagna(variant, "D1"),
            "d9_lagna": get_varga_lagna(variant, "D9"),
            "d7_lagna": get_varga_lagna(variant, "D7"),
            "d10_lagna": get_varga_lagna(variant, "D10"),
            "d24_lagna": get_varga_lagna(variant, "D24"),
        })

    return corridors


def get_varga_lagna(
    variant: Dict[str, Any],
    varga_name: str
) -> Optional[str]:
    """
    Достаёт лагну конкретной дробной карты.
    Пока заглушка.
    """

    return (
        variant
        .get("vargas", {})
        .get(varga_name, {})
        .get("lagna")
    )


# ============================================================
# 4. Оценка события
# ============================================================

def score_life_event(
    event: Dict[str, Any],
    variant: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Оценивает, насколько конкретный вариант времени объясняет событие.

    event пример:
    {
        "type": "marriage",
        "date": "2012-06-15",
        "description": "Брак"
    }
    """

    event_type = event.get("type")

    if event_type not in EVENT_RULES:
        return {
            "event": event,
            "score": 0,
            "details": ["Неизвестный тип события"],
        }

    rule = EVENT_RULES[event_type]

    score = 0
    details = []

    # Пока базовая логика-заглушка.
    # Позже здесь будут реальные проверки:
    # - активен ли нужный дом в даше
    # - есть ли связь хозяина дома
    # - подтверждает ли дробная карта
    # - есть ли транзитное подтверждение

    varga_support = check_varga_support(rule, variant)
    dasha_support = check_dasha_support(event, rule, variant)

    if varga_support:
        score += 40
        details.append("Дробная карта поддерживает событие")

    if dasha_support:
        score += 40
        details.append("Период поддерживает событие")

    score = score * rule.get("weight", 1)

    return {
        "event": event,
        "event_label": rule["label"],
        "score": round(score, 2),
        "details": details,
    }


def check_varga_support(
    rule: Dict[str, Any],
    variant: Dict[str, Any]
) -> bool:
    """
    Проверка дробной карты.
    Пока заглушка.
    """

    return False


def check_dasha_support(
    event: Dict[str, Any],
    rule: Dict[str, Any],
    variant: Dict[str, Any]
) -> bool:
    """
    Проверка Вимшоттари / Чара Даши на дату события.
    Пока заглушка.
    """

    return False


# ============================================================
# 5. Оценка всех вариантов времени
# ============================================================

def score_all_variants(
    calculated_variants: List[Dict[str, Any]],
    life_events: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    results = []

    for variant in calculated_variants:
        event_scores = []
        total_score = 0

        for event in life_events:
            event_result = score_life_event(event, variant)
            event_scores.append(event_result)
            total_score += event_result["score"]

        results.append({
            "birth_time": variant["birth_time"],
            "datetime": variant["datetime"],
            "lagna": variant.get("meta", {}).get("lagna"),
            "lagna_degree": variant.get("meta", {}).get("lagna_degree"),
            "total_score": round(total_score, 2),
            "event_scores": event_scores,
            "variant_data": variant,
        })

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results


# ============================================================
# 6. Поиск лучшего коридора времени
# ============================================================

def find_best_rectification_window(
    scored_variants: List[Dict[str, Any]],
    top_limit: int = 5
) -> Dict[str, Any]:

    top_variants = scored_variants[:top_limit]

    if not top_variants:
        return {
            "best_window": None,
            "confidence": 0,
            "top_variants": [],
        }

    best = top_variants[0]

    return {
        "best_time": best["birth_time"],
        "best_score": best["total_score"],
        "confidence": calculate_confidence(scored_variants),
        "top_variants": top_variants,
    }


def calculate_confidence(
    scored_variants: List[Dict[str, Any]]
) -> int:
    """
    Примерная уверенность.
    Потом улучшим формулу.
    """

    if not scored_variants:
        return 0

    best = scored_variants[0]["total_score"]

    if best <= 0:
        return 0

    second = scored_variants[1]["total_score"] if len(scored_variants) > 1 else 0

    gap = best - second

    if gap >= 30:
        return 90
    elif gap >= 15:
        return 75
    elif gap >= 5:
        return 60
    else:
        return 45


# ============================================================
# 7. Подготовка данных для AI
# ============================================================

def prepare_ai_payload(
    rectification_result: Dict[str, Any]
) -> Dict[str, Any]:

    return {
        "task": "rectification_analysis",
        "best_time": rectification_result.get("best_time"),
        "best_score": rectification_result.get("best_score"),
        "confidence": rectification_result.get("confidence"),
        "top_variants": [
            {
                "birth_time": item["birth_time"],
                "lagna": item.get("lagna"),
                "lagna_degree": item.get("lagna_degree"),
                "total_score": item["total_score"],
                "event_scores": item["event_scores"],
            }
            for item in rectification_result.get("top_variants", [])
        ],
        "instruction_for_ai": (
            "Проанализируй результаты ректификации. "
            "Объясни, какое время рождения наиболее вероятно, "
            "какие события его подтверждают, какие события слабее, "
            "и насколько уверенным можно считать вывод. "
            "Не пересчитывай астрологию самостоятельно, используй только переданные данные."
        )
    }


# ============================================================
# 8. Главная функция запуска ректификации
# ============================================================

def run_rectification(
    birth_date: str,
    start_time: str,
    end_time: str,
    place_data: Dict[str, Any],
    life_events: List[Dict[str, Any]],
    step_minutes: int = 15
) -> Dict[str, Any]:

    time_variants = generate_time_variants(
        birth_date=birth_date,
        start_time=start_time,
        end_time=end_time,
        step_minutes=step_minutes,
    )

    calculated_variants = []

    for birth_dt in time_variants:
        variant = calculate_variant_charts(
            birth_dt=birth_dt,
            place_data=place_data,
        )
        calculated_variants.append(variant)

    corridors = detect_varga_corridors(calculated_variants)

    scored_variants = score_all_variants(
        calculated_variants=calculated_variants,
        life_events=life_events,
    )

    best_result = find_best_rectification_window(scored_variants)

    ai_payload = prepare_ai_payload(best_result)

    return {
        "status": "success",
        "variants_count": len(time_variants),
        "corridors": corridors,
        "scored_variants": scored_variants,
        "best_result": best_result,
        "ai_payload": ai_payload,
}
