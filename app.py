import os
import time
import requests
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from flask import Flask, render_template, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from astro_engine import calculate_chart, search_places, calculate_chara_dasha_rao, calculate_rectification_range
from database import (
    init_db,
    save_chart,
    get_saved_charts,
    get_saved_chart,
    delete_saved_chart
)


app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

bot = telebot.TeleBot(TOKEN, parse_mode="HTML") if TOKEN else None
executor = ThreadPoolExecutor(max_workers=4)

DB_READY = False


def initialize_database():
    global DB_READY

    try:
        init_db()
        DB_READY = True
        print("Database initialized", flush=True)
        return True
    except Exception as e:
        DB_READY = False
        print(f"Database init error: {e}", flush=True)
        print("App will continue without saved charts until database is fixed.", flush=True)
        return False


def ensure_database_ready():
    """Проверяет БД перед каждым действием с сохранёнными картами.
    Это важно для Amvera: если база не успела подключиться при старте,
    приложение попробует подключиться ещё раз при нажатии кнопки сохранения.
    """
    if DB_READY:
        return True

    return initialize_database()


def safe_calculate_chart(**kwargs):
    print("calculate_chart started", flush=True)
    result = calculate_chart(**kwargs)
    print("calculate_chart finished", flush=True)
    return result


def calculate_with_timeout(timeout_seconds=60, **kwargs):
    future = executor.submit(safe_calculate_chart, **kwargs)

    try:
        return future.result(timeout=timeout_seconds)
    except TimeoutError:
        raise TimeoutError(
            "Расчёт занял слишком много времени. "
            "Проверьте город, координаты или расчётные функции."
        )


def get_request_user_id(data=None):
    if data is None:
        data = {}

    user_id = (
        data.get("telegram_user_id")
        or request.args.get("telegram_user_id")
        or request.headers.get("X-Telegram-User-Id")
    )

    if user_id is None:
        return None

    return str(user_id).strip()


def chart_belongs_to_user(saved_chart, telegram_user_id):
    saved_user_id = saved_chart.get("telegram_user_id")

    # Пока проект в разработке и старые карты могли быть сохранены без telegram_user_id,
    # не блокируем их открытие. После database.py можно будет ужесточить проверку.
    if saved_user_id in [None, "", "None"]:
        return True

    if not telegram_user_id:
        return False

    return str(saved_user_id).strip() == str(telegram_user_id).strip()


def extract_current_dasha_text(dasha_data):
    if not dasha_data:
        return "не передано"

    current_path_text = dasha_data.get("current_path_text")

    if current_path_text:
        return current_path_text

    current_path = dasha_data.get("current_path")

    if isinstance(current_path, list) and current_path:
        return " / ".join([str(x) for x in current_path])

    current_periods = dasha_data.get("current_periods", {})

    if isinstance(current_periods, dict):
        path_text = current_periods.get("path_text")
        if path_text:
            return path_text

    return "не найдено в данных"


def compact_period_tree(nodes, max_top=3):
    if not isinstance(nodes, list):
        return []

    compact = []

    for node in nodes[:max_top]:
        compact.append({
            "name": node.get("lord") or node.get("sign") or node.get("name"),
            "start": node.get("start"),
            "end": node.get("end"),
            "is_current": node.get("is_current", False),
            "children": compact_period_tree(node.get("children", []), max_top=3)
        })

    return compact


def compact_current_periods(dasha_data):
    if not isinstance(dasha_data, dict):
        return {}

    current = dasha_data.get("current_periods", {}) or {}

    result = {
        "path_text": extract_current_dasha_text(dasha_data),
        "mahadasha": None,
        "antardasha": None,
        "pratyantardasha": None
    }

    for key in ["mahadasha", "antardasha", "pratyantardasha"]:
        item = current.get(key)

        if isinstance(item, dict):
            result[key] = {
                "name": item.get("lord") or item.get("sign") or item.get("name"),
                "start": item.get("start"),
                "end": item.get("end"),
                "level": item.get("level"),
                "path_text": item.get("path_text") or " / ".join(item.get("path", []))
            }

    return result


def compact_chart_for_ai(chart):
    planets = chart.get("planets", {}) or {}
    houses = chart.get("houses", []) or []
    lagna = chart.get("lagna", {}) or {}
    moon = chart.get("moon", {}) or {}
    dashas = chart.get("dashas", {}) or {}
    chara_dasha = chart.get("chara_dasha", {}) or {}
    selected_varga = chart.get("selected_varga", "D1")

    compact_planets = {}

    for name, p in planets.items():
        compact_planets[name] = {
            "sign": p.get("sign"),
            "house": p.get("house"),
            "degree": p.get("degree"),
            "nakshatra": p.get("nakshatra"),
            "pada": p.get("pada"),
            "karaka": p.get("karaka"),
            "retro": p.get("retro", False)
        }

    return {
        "full_name": chart.get("full_name") or chart.get("name") or "",
        "birth_data": {
            "date": chart.get("input_date"),
            "time": chart.get("input_time"),
            "city": chart.get("city"),
            "timezone": chart.get("timezone"),
            "utc_offset": chart.get("utc_offset"),
            "lat": chart.get("lat"),
            "lon": chart.get("lon")
        },
        "lagna": lagna,
        "moon": moon,
        "houses": houses,
        "planets": compact_planets,
        "selected_varga": selected_varga,
        "vimshottari": {
            "birth_lord": dashas.get("birth_lord"),
            "current_path": dashas.get("current_path"),
            "current_path_text": extract_current_dasha_text(dashas),
            "current_periods": compact_current_periods(dashas),
            "levels": dashas.get("levels"),
            "cycle_years": dashas.get("cycle_years"),
            "sample_period_tree": compact_period_tree(dashas.get("tree") or dashas.get("mahadashas") or [], max_top=3)
        },
        "chara_dasha": {
            "system": chara_dasha.get("system"),
            "current_path": chara_dasha.get("current_path"),
            "current_path_text": extract_current_dasha_text(chara_dasha),
            "current_periods": compact_current_periods(chara_dasha),
            "levels": chara_dasha.get("levels"),
            "needs_next_cycle": chara_dasha.get("needs_next_cycle"),
            "sample_period_tree": compact_period_tree(chara_dasha.get("tree") or chara_dasha.get("periods") or [], max_top=3)
        },
        "calculation_debug": chart.get("calculation_debug", {})
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "status": "ok",
        "bot_enabled": bool(bot),
        "webapp_url_set": bool(WEBAPP_URL),
        "database_ready": DB_READY,
        "openrouter_key_set": bool(OPENROUTER_API_KEY)
    })


@app.route("/search_place", methods=["GET"])
def search_place_route():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "success": True,
            "places": []
        })

    try:
        places = search_places(query)

        return jsonify({
            "success": True,
            "places": places
        })

    except Exception as e:
        print(f"search_place error: {e}", flush=True)

        return jsonify({
            "success": False,
            "places": [],
            "error": str(e)
        })


@app.route("/calculate", methods=["POST"])
def calculate():
    print("POST /calculate started", flush=True)

    data = request.get_json(force=True) or {}
    print(f"POST /calculate data: {data}", flush=True)

    date = data.get("date", "").strip()
    time_birth = data.get("time", "").strip()
    city = data.get("city", "").strip()
    mode = data.get("mode", "client")
    full_name = (
        data.get("full_name")
        or data.get("name")
        or data.get("client_name")
        or ""
    ).strip()
    telegram_user_id = get_request_user_id(data)

    lat = data.get("lat")
    lon = data.get("lon")
    display_name = data.get("display_name")

    try:
        chart = calculate_with_timeout(
            timeout_seconds=60,
            date_str=date,
            time_str=time_birth,
            city=city,
            lat=lat,
            lon=lon,
            display_name=display_name
        )

        chart["mode"] = mode
        chart["full_name"] = full_name
        chart["telegram_user_id"] = telegram_user_id
        chart["active_vimshottari"] = extract_current_dasha_text(chart.get("dashas", {}))
        chart["active_chara_dasha"] = extract_current_dasha_text(chart.get("chara_dasha", {}))

        print("POST /calculate success", flush=True)

        return jsonify({
            "success": True,
            "mode": mode,
            "chart": chart
        })

    except Exception as e:
        print(f"POST /calculate error: {e}", flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/calculate_transit", methods=["POST"])
def calculate_transit():
    print("POST /calculate_transit started", flush=True)

    data = request.get_json(force=True) or {}

    date = data.get("date", "").strip()
    time_transit = data.get("time", "").strip()
    city = data.get("city", "").strip()

    lat = data.get("lat")
    lon = data.get("lon")
    display_name = data.get("display_name")

    try:
        transit_chart = calculate_with_timeout(
            timeout_seconds=60,
            date_str=date,
            time_str=time_transit,
            city=city,
            lat=lat,
            lon=lon,
            display_name=display_name
        )

        transit_chart["active_vimshottari"] = extract_current_dasha_text(transit_chart.get("dashas", {}))
        transit_chart["active_chara_dasha"] = extract_current_dasha_text(transit_chart.get("chara_dasha", {}))

        return jsonify({
            "success": True,
            "transit": transit_chart
        })

    except Exception as e:
        print(f"POST /calculate_transit error: {e}", flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/rectification", methods=["POST"])
def rectification():
    print("POST /rectification started", flush=True)

    data = request.get_json(force=True) or {}

    date = data.get("date", "").strip()
    city = data.get("city", "").strip()
    full_name = (
        data.get("full_name")
        or data.get("name")
        or data.get("client_name")
        or ""
    ).strip()

    lat = data.get("lat")
    lon = data.get("lon")
    display_name = data.get("display_name")

    # Новый режим ректификации: диапазон времени + шаг + события.
    start_time = (data.get("start_time") or data.get("startTime") or "").strip()
    end_time = (data.get("end_time") or data.get("endTime") or "").strip()
    life_events = data.get("events") or data.get("life_events") or []
    step_minutes = int(data.get("step_minutes") or data.get("stepMinutes") or 15)

    try:
        if start_time and end_time:
            result = calculate_rectification_range(
                date_str=date,
                start_time=start_time,
                end_time=end_time,
                city=city,
                life_events=life_events,
                step_minutes=step_minutes,
                lat=lat,
                lon=lon,
                display_name=display_name
            )

            return jsonify({
                "success": True,
                "rectification": result
            })

        # Старый безопасный режим: просто пересчитать карту на новое время.
        time_birth = data.get("time", "").strip()
        rectified_chart = calculate_with_timeout(
            timeout_seconds=60,
            date_str=date,
            time_str=time_birth,
            city=city,
            lat=lat,
            lon=lon,
            display_name=display_name
        )

        rectified_chart["full_name"] = full_name
        rectified_chart["active_vimshottari"] = extract_current_dasha_text(rectified_chart.get("dashas", {}))
        rectified_chart["active_chara_dasha"] = extract_current_dasha_text(rectified_chart.get("chara_dasha", {}))

        return jsonify({
            "success": True,
            "chart": rectified_chart
        })

    except Exception as e:
        print(f"POST /rectification error: {e}", flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/api/ai_astrologer", methods=["POST"])
def ai_astrologer():
    print("POST /api/ai_astrologer started", flush=True)

    data = request.get_json(force=True) or {}

    question = data.get("question", "").strip()
    chart = data.get("chart", {})
    mode = data.get("mode", "client")
    compact_chart = compact_chart_for_ai(chart)

    if not OPENROUTER_API_KEY:
        return jsonify({
            "success": False,
            "error": "OPENROUTER_API_KEY не задан в переменных Amvera."
        })

    if not question:
        return jsonify({
            "success": False,
            "error": "Введите вопрос для AI-астролога."
        })

    if mode == "pro":
        style_instruction = """
Отвечай как профессиональный джйотиш-аналитик для астролога.
Можно использовать технические термины: лагна, бхава, граха, дришти, йоги, авастхи, варги, даши.
Не упрощай чрезмерно.
"""
    else:
        style_instruction = """
Отвечай понятным языком для обычного пользователя.
Санскритские термины можно использовать, но обязательно кратко поясняй.
Не пугай, не фатализируй, не обещай гарантированных событий.
"""

    prompt = f"""
Ты Аная — профессиональный AI-астролог AstroEngine, работающий в системе ведической астрологии Джйотиш.

Главные правила:
1. Представляйся именем Аная, если это уместно в начале диалога.
2. Отвечай глубоко, внимательно и честно.
3. Не придумывай расчёты, которых нет в данных.
4. Если данных недостаточно, прямо скажи об этом.
5. Не давай медицинских, юридических или финансовых гарантий.
6. Не обещай точных событий как неизбежность.
7. Делай выводы только на основе предоставленной карты.
8. Пиши на русском языке.
9. Если пользователь спрашивает про период Марс/Юпитер, Марс-Юпитер или похожую связку, трактуй это как Вимшоттари: махадаша / антардаша / пратьянтардаша, если такой период есть в данных.
10. Обязательно учитывай активные периоды и даты внутри current_periods:
   - Вимшоттари: {compact_chart.get("vimshottari", {}).get("current_path_text")}
   - Чара Даша: {compact_chart.get("chara_dasha", {}).get("current_path_text")}
11. Если в данных есть dates/start/end по периодам, обязательно используй их в ответе.
12. Не сохраняй и не проси сохранять AI-разбор в карту.

Стиль ответа:
{style_instruction}

Сжатые данные карты:
{compact_chart}

Вопрос пользователя:
{question}

Дай структурированный ответ.
"""

    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        payload = {
            "model": "openrouter/auto",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        result = response.json()

        if response.status_code != 200:
            print(f"OpenRouter API error: {result}", flush=True)
            return jsonify({
                "success": False,
                "error": result
            })

        answer = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        if not answer:
            return jsonify({
                "success": False,
                "error": "OpenRouter не вернул текст ответа."
            })

        print("POST /api/ai_astrologer success", flush=True)

        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as e:
        print(f"AI astrologer error: {e}", flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/calculate_chara_cycle", methods=["POST"])
def calculate_chara_cycle():
    print("POST /calculate_chara_cycle started", flush=True)

    data = request.get_json(force=True) or {}
    chart = data.get("chart", {}) or {}
    cycles = int(data.get("cycles", 2) or 2)

    if cycles < 1:
        cycles = 1

    if cycles > 5:
        cycles = 5

    try:
        input_date = chart.get("input_date", "").strip()
        input_time = chart.get("input_time", "").strip()
        lagna = chart.get("lagna", {}) or {}
        planets = chart.get("planets", {}) or {}

        if not input_date or not input_time or "sign_index" not in lagna or not planets:
            return jsonify({
                "success": False,
                "error": "Не хватает данных карты для расчёта следующего цикла Чара Даши."
            })

        from datetime import datetime

        local_dt = datetime.strptime(
            f"{input_date} {input_time}",
            "%d.%m.%Y %H:%M:%S"
        )

        chara_dasha = calculate_chara_dasha_rao(
            local_dt=local_dt,
            lagna_sign_index=int(lagna["sign_index"]),
            planets=planets,
            cycles=cycles
        )

        return jsonify({
            "success": True,
            "cycles": cycles,
            "chara_dasha": chara_dasha
        })

    except Exception as e:
        print(f"calculate_chara_cycle error: {e}", flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/save_chart", methods=["POST"])
def save_chart_route():
    if not ensure_database_ready():
        return jsonify({
            "success": False,
            "error": "База данных временно недоступна. Проверьте DATABASE_URL."
        })

    data = request.get_json(force=True) or {}

    name = (
        data.get("name")
        or data.get("full_name")
        or data.get("client_name")
        or ""
    ).strip()
    birth_date = data.get("birth_date", "").strip()
    birth_time = data.get("birth_time", "").strip()
    place_name = data.get("place_name", "").strip()

    lat = data.get("lat")
    lon = data.get("lon")
    timezone = data.get("timezone", "")
    comment = data.get("comment", "")
    telegram_user_id = data.get("telegram_user_id")

    # AI-разбор не сохраняем в карточку. Сохраняется только карта.
    if "ai" in str(comment).lower() or "разбор" in str(comment).lower():
        comment = ""

    if not name:
        return jsonify({
            "success": False,
            "error": "Введите имя карты"
        })

    if not birth_date or not birth_time or not place_name:
        return jsonify({
            "success": False,
            "error": "Не хватает данных для сохранения"
        })

    try:
        saved = save_chart(
            telegram_user_id=telegram_user_id,
            name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            place_name=place_name,
            lat=lat,
            lon=lon,
            timezone=timezone,
            comment=comment
        )

        return jsonify({
            "success": True,
            "chart": saved
        })

    except Exception as e:
        print(f"save_chart error: {e}", flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/saved_charts", methods=["GET"])
def saved_charts_route():
    if not ensure_database_ready():
        return jsonify({
            "success": False,
            "charts": [],
            "error": "База данных временно недоступна. Проверьте DATABASE_URL."
        })

    telegram_user_id = request.args.get("telegram_user_id")

    try:
        charts = get_saved_charts(telegram_user_id)

        return jsonify({
            "success": True,
            "charts": charts
        })

    except Exception as e:
        print(f"saved_charts error: {e}", flush=True)

        return jsonify({
            "success": False,
            "charts": [],
            "error": str(e)
        })


@app.route("/open_chart/<int:chart_id>", methods=["GET"])
def open_chart_route(chart_id):
    if not ensure_database_ready():
        return jsonify({
            "success": False,
            "error": "База данных временно недоступна. Проверьте DATABASE_URL."
        })

    try:
        telegram_user_id = get_request_user_id()
        saved = get_saved_chart(chart_id)

        if not saved:
            return jsonify({
                "success": False,
                "error": "Карта не найдена"
            })

        if not chart_belongs_to_user(saved, telegram_user_id):
            return jsonify({
                "success": False,
                "error": "Нет доступа к этой карте"
            })

        chart = calculate_with_timeout(
            timeout_seconds=60,
            date_str=saved["birth_date"],
            time_str=saved["birth_time"],
            city=saved["place_name"],
            lat=saved["lat"],
            lon=saved["lon"],
            display_name=saved["place_name"]
        )

        chart["full_name"] = saved.get("name", "")
        chart["telegram_user_id"] = telegram_user_id
        chart["active_vimshottari"] = extract_current_dasha_text(chart.get("dashas", {}))
        chart["active_chara_dasha"] = extract_current_dasha_text(chart.get("chara_dasha", {}))

        return jsonify({
            "success": True,
            "saved": saved,
            "chart": chart
        })

    except Exception as e:
        print(f"open_chart error: {e}", flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/delete_chart/<int:chart_id>", methods=["DELETE"])
def delete_chart_route(chart_id):
    if not ensure_database_ready():
        return jsonify({
            "success": False,
            "error": "База данных временно недоступна. Проверьте DATABASE_URL."
        })

    try:
        telegram_user_id = get_request_user_id()
        saved = get_saved_chart(chart_id)

        if not saved:
            return jsonify({
                "success": False,
                "error": "Карта не найдена"
            })

        if not chart_belongs_to_user(saved, telegram_user_id):
            return jsonify({
                "success": False,
                "error": "Нет доступа к этой карте"
            })

        deleted = delete_saved_chart(chart_id)

        if not deleted:
            return jsonify({
                "success": False,
                "error": "Карта не найдена"
            })

        return jsonify({
            "success": True
        })

    except Exception as e:
        print(f"delete_chart error: {e}", flush=True)

        return jsonify({
            "success": False,
            "error": str(e)
        })


def make_start_keyboard():
    markup = InlineKeyboardMarkup()

    if WEBAPP_URL:
        button = InlineKeyboardButton(
            text="🌐 Перейти в веб-приложение",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    else:
        button = InlineKeyboardButton(
            text="⚠️ WEBAPP_URL не задан",
            callback_data="no_webapp_url"
        )

    markup.add(button)
    return markup


if bot:
    @bot.message_handler(commands=["start"])
    def start(message):
        text = """
✨ Добро пожаловать в <b>AstroEngine</b>

AstroEngine — система джйотиш-анализа, которая объединяет понятный разбор для пользователя и профессиональный инструмент для астрологов.

Сервис рассчитывает натальную карту и показывает:
— структуру личности
— сильные и слабые планеты
— ключевые сценарии реализации
— периоды
— дробные карты
— технические параметры карты

Для астрологов доступен расширенный режим с детальными расчётами.

👇 Перейти в веб-приложение
"""

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=make_start_keyboard()
        )


    @bot.callback_query_handler(func=lambda call: call.data == "no_webapp_url")
    def no_webapp_url(call):
        bot.answer_callback_query(
            call.id,
            "В Amvera нужно добавить переменную WEBAPP_URL со ссылкой на веб-приложение.",
            show_alert=True
        )


def run_bot():
    if not bot:
        print("Telegram bot disabled: BOT_TOKEN is missing", flush=True)
        return

    time.sleep(5)

    try:
        bot.remove_webhook()
        print("Webhook removed", flush=True)
    except Exception as e:
        print(f"Webhook remove error: {e}", flush=True)

    print("Telegram bot polling started", flush=True)

    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )
        except Exception as e:
            print(f"Bot polling error: {e}", flush=True)
            time.sleep(5)


initialize_database()

if __name__ == "__main__":
    if bot:
        Thread(target=run_bot, daemon=True).start()

    app.run(
        host="0.0.0.0",
        port=80,
        debug=False,
        use_reloader=False,
        threaded=True
    )
