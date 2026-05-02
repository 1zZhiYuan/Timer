"""
SQLite database layer for Timer.
Stores daily records, app usage, pomodoro sessions, and settings.
"""
import sqlite3
import os
from datetime import date, datetime, timedelta
from typing import Optional


DB_DIR = os.path.join(os.path.expanduser("~"), ".timer")
DB_PATH = os.path.join(DB_DIR, "timer.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS daily_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL UNIQUE,
            total_seconds INTEGER NOT NULL DEFAULT 0,
            target_seconds INTEGER NOT NULL DEFAULT 0,
            session_intervals TEXT DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS app_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL,
            app_name TEXT NOT NULL,
            window_title TEXT DEFAULT '',
            total_seconds INTEGER NOT NULL DEFAULT 0,
            category TEXT NOT NULL DEFAULT 'other',
            UNIQUE(record_date, app_name)
        );

        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT NOT NULL,
            completed_count INTEGER NOT NULL DEFAULT 0,
            focus_minutes INTEGER NOT NULL DEFAULT 25,
            break_minutes INTEGER NOT NULL DEFAULT 5,
            started_at TEXT,
            ended_at TEXT
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_app_usage_date ON app_usage(record_date);
        CREATE INDEX IF NOT EXISTS idx_daily_records_date ON daily_records(record_date);
    """)
    conn.commit()
    conn.close()


# ─── Daily Records ────────────────────────────────────────────────────────────

def get_or_create_record(record_date: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_records WHERE record_date = ?", (record_date,))
    row = cursor.fetchone()
    if row:
        result = dict(row)
    else:
        cursor.execute(
            "INSERT INTO daily_records (record_date, total_seconds) VALUES (?, 0)",
            (record_date,),
        )
        conn.commit()
        result = {"record_date": record_date, "total_seconds": 0, "target_seconds": 0, "session_intervals": "[]"}
    conn.close()
    return result


def update_daily_seconds(record_date: str, total_seconds: int, intervals_json: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    if intervals_json:
        cursor.execute(
            "UPDATE daily_records SET total_seconds = ?, session_intervals = ?, updated_at = datetime('now','localtime') WHERE record_date = ?",
            (total_seconds, intervals_json, record_date),
        )
    else:
        cursor.execute(
            "UPDATE daily_records SET total_seconds = ?, updated_at = datetime('now','localtime') WHERE record_date = ?",
            (total_seconds, record_date),
        )
    conn.commit()
    conn.close()


def set_daily_target(record_date: str, target_seconds: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO daily_records (record_date, target_seconds, total_seconds) VALUES (?, ?, 0) "
        "ON CONFLICT(record_date) DO UPDATE SET target_seconds = ?",
        (record_date, target_seconds, target_seconds),
    )
    conn.commit()
    conn.close()


def get_month_records(year: int, month: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    prefix = f"{year:04d}-{month:02d}"
    cursor.execute(
        "SELECT * FROM daily_records WHERE record_date LIKE ? ORDER BY record_date",
        (prefix + "%",),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_records_in_range(start_date: str, end_date: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM daily_records WHERE record_date >= ? AND record_date <= ? ORDER BY record_date",
        (start_date, end_date),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_records(limit: int = 90) -> list[dict]:
    """Get the most recent N daily records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM daily_records ORDER BY record_date DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows[::-1]]


def get_total_stats() -> dict:
    """Get aggregate stats: total days, total seconds, max streak, days met target."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(total_seconds),0) as tot FROM daily_records")
    row = cursor.fetchone()
    total_days = row["cnt"]
    total_seconds = row["tot"]
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM daily_records WHERE target_seconds > 0 AND total_seconds >= target_seconds"
    )
    days_met_target = cursor.fetchone()["cnt"]
    cursor.execute("SELECT record_date FROM daily_records ORDER BY record_date")
    rows = cursor.fetchall()
    conn.close()

    # Calculate best streak
    dates = sorted(set(r["record_date"] for r in rows))
    best_streak = cur_streak = 0
    from datetime import datetime, timedelta
    for i, ds in enumerate(dates):
        if i == 0:
            cur_streak = 1
        else:
            prev = datetime.strptime(dates[i-1], "%Y-%m-%d").date()
            cur = datetime.strptime(ds, "%Y-%m-%d").date()
            if (cur - prev).days == 1:
                cur_streak += 1
            else:
                cur_streak = 1
        best_streak = max(best_streak, cur_streak)

    return {
        "total_days": total_days,
        "total_seconds": total_seconds,
        "days_met_target": days_met_target,
        "best_streak": best_streak,
        "max_streak_days": best_streak,
    }


def get_early_bird_count() -> int:
    """Count days with sessions starting before 08:00."""
    import json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_intervals FROM daily_records WHERE session_intervals != '[]'")
    rows = cursor.fetchall()
    conn.close()
    count = 0
    for r in rows:
        try:
            intervals = json.loads(r["session_intervals"])
            for iv in intervals:
                h = datetime.fromisoformat(iv["start"]).hour
                if h < 8:
                    count += 1
                    break
        except Exception:
            continue
    return count


def get_night_owl_count() -> int:
    """Count days with sessions starting after 22:00."""
    import json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_intervals FROM daily_records WHERE session_intervals != '[]'")
    rows = cursor.fetchall()
    conn.close()
    count = 0
    for r in rows:
        try:
            intervals = json.loads(r["session_intervals"])
            for iv in intervals:
                h = datetime.fromisoformat(iv["start"]).hour
                if h >= 22:
                    count += 1
                    break
        except Exception:
            continue
    return count


def get_streak_count() -> int:
    """Calculate consecutive days where daily target was met, going backwards
    from yesterday (today is excluded since the day may not be over)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT record_date, total_seconds, target_seconds FROM daily_records "
        "WHERE target_seconds > 0 ORDER BY record_date DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return 0
    streak = 0
    today = date.today()
    check = today - timedelta(days=1)  # start from yesterday
    # Also include today if it meets the target
    for r in rows:
        rd = datetime.strptime(r["record_date"], "%Y-%m-%d").date()
        if rd < check:
            break
        if rd == check or (rd == today and r["total_seconds"] >= r["target_seconds"]):
            if r["total_seconds"] >= r["target_seconds"]:
                streak += 1
                check -= timedelta(days=1)
            else:
                break
    return streak


# ─── App Usage ────────────────────────────────────────────────────────────────

def record_app_usage(record_date: str, app_name: str, window_title: str, seconds_delta: int, category: str = "other"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO app_usage (record_date, app_name, window_title, total_seconds, category) "
        "VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(record_date, app_name) DO UPDATE SET "
        "total_seconds = total_seconds + ?, window_title = ?",
        (record_date, app_name, window_title, seconds_delta, category, seconds_delta, window_title),
    )
    conn.commit()
    conn.close()


def get_app_usage(date_str: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM app_usage WHERE record_date = ? ORDER BY total_seconds DESC",
        (date_str,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_app_usage_range(start_date: str, end_date: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT app_name, SUM(total_seconds) as total_seconds, category FROM app_usage "
        "WHERE record_date >= ? AND record_date <= ? GROUP BY app_name ORDER BY total_seconds DESC",
        (start_date, end_date),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Pomodoro ─────────────────────────────────────────────────────────────────

def save_pomodoro_session(record_date: str, focus_minutes: int, break_minutes: int, completed_count: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pomodoro_sessions (record_date, focus_minutes, break_minutes, completed_count) "
        "VALUES (?, ?, ?, ?)",
        (record_date, focus_minutes, break_minutes, completed_count),
    )
    conn.commit()
    conn.close()


def get_pomodoro_sessions(start_date: str, end_date: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM pomodoro_sessions WHERE record_date >= ? AND record_date <= ? ORDER BY record_date",
        (start_date, end_date),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── Settings ─────────────────────────────────────────────────────────────────

def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
        (key, value, value),
    )
    conn.commit()
    conn.close()


# ─── Data Export ──────────────────────────────────────────────────────────────

def export_all_records() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_records ORDER BY record_date DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def export_app_usage_all() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM app_usage ORDER BY record_date DESC, total_seconds DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
