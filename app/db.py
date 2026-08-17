from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("PHOENIX_DB", BASE_DIR / "data" / "phoenix.db"))
SCHEMA_PATH = BASE_DIR / "database.sql"

DEFAULT_SETTINGS = {
    "company_name": "Remarkable Home Improvement",
    "registration_number": "PA151285",
    "company_email": "remarkablehome@yahoo.com",
    "business_hours": "9:00 AM–5:00 PM",
    "tagline": "Craftsmanship you can trust.",
    "default_state": "PA",
    "material_tax_rate": "0.06",
    "target_gross_margin": "0.30",
    "small_job_margin": "0.35",
    "high_risk_margin": "0.40",
    "deposit_percent": "0.40",
    "mid_project_percent": "0.30",
    "final_percent": "0.30",
    "default_warranty_term": "1 year",
    "payment_methods": "Cash,Check",
    "current_user": "Ryan",
}


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA_PATH.read_text())
        for key, value in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO app_settings(key, value) VALUES (?, ?)",
                (key, value),
            )
        conn.commit()


def get_settings() -> dict[str, str]:
    with db() as conn:
        rows = conn.execute("SELECT key, value FROM app_settings").fetchall()
    return {row["key"]: row["value"] for row in rows}


def next_id(prefix: str, width: int) -> str:
    year = datetime.now().year
    with db() as conn:
        row = conn.execute(
            "SELECT last_number FROM id_sequences WHERE prefix=? AND year=?",
            (prefix, year),
        ).fetchone()
        number = (row["last_number"] if row else 0) + 1
        conn.execute(
            "INSERT INTO id_sequences(prefix, year, last_number) VALUES (?, ?, ?) "
            "ON CONFLICT(prefix, year) DO UPDATE SET last_number=excluded.last_number",
            (prefix, year, number),
        )
    return f"{prefix}-{year}-{number:0{width}d}"
