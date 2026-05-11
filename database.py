import os
import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def get_conn():

    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=30,
        cursor_factory=RealDictCursor
    )


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

            cur.execute("""
                ALTER TABLE saved_charts
                ADD COLUMN IF NOT EXISTS chart_type TEXT DEFAULT 'D1'
            """)

            cur.execute("""
                ALTER TABLE saved_charts
                ADD COLUMN IF NOT EXISTS comment TEXT DEFAULT ''
            """)

            conn.commit()

            print("PostgreSQL connected successfully")


def sanitize_comment(comment):
    if comment is None:
        return ""

    comment = str(comment)

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

    # PostgreSQL BIGINT не принимает пустую строку.
    # Если Telegram ID нет, сохраняем NULL.
    if telegram_user_id in ["", "None", "null"]:
        telegram_user_id = None

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

                    ORDER BY LOWER(name) ASC, created_at DESC
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

                    ORDER BY LOWER(name) ASC, created_at DESC
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
