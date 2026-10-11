"""
app/auth/database.py
SQLite-backed persistent user storage for CropShield AI authentication.
Handles user registration, credential verification, and optional operator-
configured bootstrap account creation.
"""

import sqlite3
import datetime
import os
from pathlib import Path
from typing import Optional, Dict, Any

from app.config.settings import settings
from app.utils.logging import get_logger
from app.auth.security import generate_salt, hash_password, verify_password

logger = get_logger("auth_db")

DB_PATH = settings.BASE_DIR / "data" / "users.db"


def get_connection() -> sqlite3.Connection:
    """Open SQLite connection with row dictionary access."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_user_db():
    """Initialize schema and optionally seed an operator-provided first account."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'specialist',
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        """)
        conn.commit()

        # Optional bootstrap account: credentials are supplied by the operator,
        # never embedded in source or created implicitly with a known password.
        seed_email = os.getenv("INITIAL_USER_EMAIL", "").strip().lower()
        seed_password = os.getenv("INITIAL_USER_PASSWORD", "")
        seed_users = ([{
            "email": seed_email,
            "name": os.getenv("INITIAL_USER_NAME", "Project Administrator").strip(),
            "role": os.getenv("INITIAL_USER_ROLE", "specialist").strip(),
            "password": seed_password,
        }] if seed_email and seed_password else [])

        for su in seed_users:
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (su["email"],))
            existing = cursor.fetchone()
            if not existing:
                salt = generate_salt()
                pw_hash = hash_password(su["password"], salt)
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                cursor.execute("""
                    INSERT INTO users (email, name, role, password_hash, salt, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (su["email"].lower(), su["name"], su["role"], pw_hash, salt, now_iso))
                logger.info(f"Seeded default user credentials for {su['email']}")
        conn.commit()
    except Exception as e:
        logger.error(f"Error initializing user DB: {e}")
        raise
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetch user record by email address (case-insensitive)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def create_user(email: str, password: str, name: str, role: str = "specialist") -> Dict[str, Any]:
    """Register a new user with salted PBKDF2 password hash."""
    clean_email = email.strip().lower()
    clean_name = name.strip()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (clean_email,))
        if cursor.fetchone():
            raise ValueError("An account with this email address already exists. Please log in instead.")

        salt = generate_salt()
        pw_hash = hash_password(password, salt)
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        cursor.execute("""
            INSERT INTO users (email, name, role, password_hash, salt, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (clean_email, clean_name, role, pw_hash, salt, now_iso, now_iso))
        conn.commit()
        user_id = cursor.lastrowid

        return {
            "id": user_id,
            "email": clean_email,
            "name": clean_name,
            "role": role,
            "created_at": now_iso
        }
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate email and password against stored database hash."""
    user = get_user_by_email(email)
    if not user:
        return None

    if not verify_password(password, user["password_hash"], user["salt"]):
        return None

    # Update last login timestamp
    conn = get_connection()
    try:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now_iso, user["id"]))
        conn.commit()
    except Exception as e:
        logger.warning(f"Could not update last login for user {user['id']}: {e}")
    finally:
        conn.close()

    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"]
    }
