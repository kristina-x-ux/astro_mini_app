import os
import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    if not DATABASE_URL:
        raise ValueError("Не задан DATABASE_URL")

    return psycopg2.connect(DATABASE_URL, sslmode="require")


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
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)


def save_chart(
    telegram_user_id,
    name,
    birth_date,
    birth_time,
    place_name,
    lat,
    lon,
    timezone,
    comment=""
):
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
                    comment
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                comment
            ))

            return dict(cur.fetchone())


def get_saved_charts(telegram_user_id=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if telegram_user_id:
                cur.execute("""
                    SELECT *
                    FROM saved_charts
                    WHERE telegram_user_id = %s
                    ORDER BY created_at DESC
                """, (telegram_user_id,))
            else:
                cur.execute("""
                    SELECT *
                    FROM saved_charts
                    ORDER BY created_at DESC
                """)

            return [dict(row) for row in cur.fetchall()]


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

            return dict(row)


def delete_saved_chart(chart_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM saved_charts
                WHERE id = %s
            """, (chart_id,))

            return cur.rowcount > 0
