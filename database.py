import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def get_conn(retries=3, delay=1):
    """
    Подключение к PostgreSQL на Amvera.
    sslmode=require обязателен, иначе может быть SSL SYSCALL error / EOF detected.
    Делаем несколько попыток, потому что база иногда просыпается не сразу после деплоя.
    """
    if not DATABASE_URL:
        raise ValueError("Не задан DATABASE_URL")

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            return psycopg2.connect(
                DATABASE_URL,
                sslmode="require",
                connect_timeout=10,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
        except psycopg2.OperationalError as e:
            last_error = e
            print(f"Database connection attempt {attempt}/{retries} failed: {e}", flush=True)
            if attempt < retries:
                time.sleep(delay)

    raise last_error


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS saved_charts (
                    id SERIAL PRIMARY KEY,

                    telegram_user_id BIGINT,

                    name TEXT NOT NULL,

                    birth_date TEXT NOT NULL,
                    birth_time TEXT NOT NULL,

                    place_name TEXT NOT NULL,

                    lat DOUBLE PRECISION,
                    lon DOUBLE PRECISION,

                    timezone TEXT,

                    comment TEXT DEFAULT '',

                    chart_type TEXT DEFAULT 'D1',

                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            # Безопасная миграция для старых таблиц
            cur.execute("""
                ALTER TABLE saved_charts
                ADD COLUMN IF NOT EXISTS chart_type TEXT DEFAULT 'D1'
            """)

            cur.execute("""
                ALTER TABLE saved_charts
                ADD COLUMN IF NOT EXISTS comment TEXT DEFAULT ''
            """)

            conn.commit()


def sanitize_comment(comment):
    if comment is None:
        return ""

    comment = str(comment)

    # AI-разборы не сохраняем в БД
    forbidden = [
        "ai-разбор",
        "ии-разбор",
        "anaya",
        "аная",
        "openrouter"
    ]

    lower = comment.lower()

    for word in forbidden:
        if word in lower:
            return ""

    return comment.strip()


def save_chart(
    telegram_user_id,
    name,
    birth_date,
    birth_time,
    place_name,
    lat,
    lon,
    timezone,
    comment="",
    chart_type="D1"
):
    clean_comment = sanitize_comment(comment)

    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("""
                INSERT INTO saved_charts (
                    telegram_user_id,
                    name,
                    birth_date,
                    birth_time,
                    place_name,
                    lat,
                    lon,
                    timezone,
                    comment,
                    chart_type
                )

                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )

                RETURNING *
            """, (
                telegram_user_id,
                name,
                birth_date,
                birth_time,
                place_name,
                lat,
                lon,
                timezone,
                clean_comment,
                chart_type
            ))

            row = cur.fetchone()

            conn.commit()

            return dict(row)


def get_saved_charts(telegram_user_id=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            if telegram_user_id:

                cur.execute("""
                    SELECT
                        id,
                        telegram_user_id,
                        name,
                        birth_date,
                        birth_time,
                        place_name,
                        lat,
                        lon,
                        timezone,
                        comment,
                        chart_type,
                        created_at

                    FROM saved_charts

                    WHERE telegram_user_id = %s

                    ORDER BY created_at DESC
                """, (telegram_user_id,))

            else:

                cur.execute("""
                    SELECT
                        id,
                        telegram_user_id,
                        name,
                        birth_date,
                        birth_time,
                        place_name,
                        lat,
                        lon,
                        timezone,
                        comment,
                        chart_type,
                        created_at

                    FROM saved_charts

                    ORDER BY created_at DESC
                """)

            rows = cur.fetchall()

            result = []

            for row in rows:
                item = dict(row)

                item["display_name"] = (
                    f"{item.get('name', '')} — "
                    f"{item.get('birth_date', '')}"
                )

                result.append(item)

            return result


def get_saved_chart(chart_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("""
                SELECT *
                FROM saved_charts
                WHERE id = %s
            """, (chart_id,))

            row = cur.fetchone()

            if not row:
                return None

            item = dict(row)

            # AI-разбор не отдаём
            item["comment"] = sanitize_comment(
                item.get("comment", "")
            )

            return item


def delete_saved_chart(chart_id):
    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                DELETE FROM saved_charts
                WHERE id = %s
            """, (chart_id,))

            deleted = cur.rowcount > 0

            conn.commit()

            return deleted
