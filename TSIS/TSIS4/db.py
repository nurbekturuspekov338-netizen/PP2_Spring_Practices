# db.py — PostgreSQL integration via psycopg2

import psycopg2
from config import DB_DSN

# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def get_connection():
    """Return a new psycopg2 connection (caller is responsible for closing)."""
    return psycopg2.connect(DB_DSN)


def init_db():
    """Create tables if they don't exist yet."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()


# ── Player helpers ─────────────────────────────────────────────────────────────

def get_or_create_player(username: str) -> int:
    """Return the player's id, creating a row if needed."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) "
                "ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username "
                "RETURNING id",
                (username,)
            )
            row = cur.fetchone()
        conn.commit()
    return row[0]


def get_personal_best(player_id: int) -> int:
    """Return the player's highest score ever (0 if none)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
                (player_id,)
            )
            return cur.fetchone()[0]


# ── Session helpers ────────────────────────────────────────────────────────────

def save_session(player_id: int, score: int, level_reached: int):
    """Persist a finished game session."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached) "
                "VALUES (%s, %s, %s)",
                (player_id, score, level_reached)
            )
        conn.commit()


# ── Leaderboard ────────────────────────────────────────────────────────────────

def get_top10():
    """
    Return top-10 all-time rows:
    [(rank, username, score, level_reached, played_at), ...]
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at::DATE
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10
            """)
            return cur.fetchall()
