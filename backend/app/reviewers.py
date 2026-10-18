import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
import sqlite3

from app.db import now, get_conn

_DUMMY_SALT = os.urandom(16)
_DUMMY_HASH = f"scrypt$16384$8$1${_DUMMY_SALT.hex()}${hashlib.scrypt(b'dummy-auth-salt', salt=_DUMMY_SALT, n=16384, r=8, p=1).hex()}"


def hash_password(password: str) -> str:
    """Hash password using scrypt with random 16-byte salt."""
    n = 2**14
    r = 8
    p = 1
    salt = os.urandom(16)
    derived = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p)
    return f"scrypt${n}${r}${p}${salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored scrypt hash string safely."""
    try:
        parts = stored.split("$")
        if len(parts) != 6 or parts[0] != "scrypt":
            return False
        n = int(parts[1])
        r = int(parts[2])
        p = int(parts[3])
        salt = bytes.fromhex(parts[4])
        expected = bytes.fromhex(parts[5])
        computed = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=n, r=r, p=p)
        return hmac.compare_digest(computed, expected)
    except Exception:
        return False


def create_reviewer(
    conn: sqlite3.Connection,
    username: str,
    password: str,
    display_name: str | None = None,
    role: str = "reviewer",
) -> dict:
    """Create a reviewer account and return reviewer record without password hash."""
    if not isinstance(username, str):
        raise ValueError("Username must be a string")
    norm_username = username.strip().lower()
    if not norm_username:
        raise ValueError("Username cannot be empty")
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if role not in ("reviewer", "admin"):
        raise ValueError(f"Invalid role: {role!r}")

    disp_name = display_name if display_name is not None else norm_username
    existing = conn.execute(
        "SELECT 1 FROM reviewers WHERE username = ?", (norm_username,)
    ).fetchone()
    if existing:
        raise ValueError("username already exists")

    pwd_hash = hash_password(password)
    created = now()
    try:
        cur = conn.execute(
            """
            INSERT INTO reviewers (username, display_name, role, password_hash, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (norm_username, disp_name, role, pwd_hash, created),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        raise ValueError("username already exists")

    return {
        "reviewer_id": cur.lastrowid,
        "username": norm_username,
        "display_name": disp_name,
        "role": role,
        "is_active": 1,
        "created_at": created,
    }


def get_reviewer(conn: sqlite3.Connection, reviewer_id: int) -> dict | None:
    """Get reviewer by id without password hash."""
    row = conn.execute(
        "SELECT reviewer_id, username, display_name, role, is_active, created_at "
        "FROM reviewers WHERE reviewer_id = ?",
        (reviewer_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "reviewer_id": row["reviewer_id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "role": row["role"],
        "is_active": row["is_active"],
        "created_at": row["created_at"],
    }


def get_reviewer_by_username(conn: sqlite3.Connection, username: str) -> dict | None:
    """Get reviewer by username without password hash."""
    norm = username.strip().lower() if isinstance(username, str) else ""
    row = conn.execute(
        "SELECT reviewer_id, username, display_name, role, is_active, created_at "
        "FROM reviewers WHERE username = ?",
        (norm,),
    ).fetchone()
    if not row:
        return None
    return {
        "reviewer_id": row["reviewer_id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "role": row["role"],
        "is_active": row["is_active"],
        "created_at": row["created_at"],
    }


def list_reviewers(conn: sqlite3.Connection, include_inactive: bool = False) -> list[dict]:
    """List reviewers without password hashes."""
    if include_inactive:
        sql = (
            "SELECT reviewer_id, username, display_name, role, is_active, created_at "
            "FROM reviewers ORDER BY reviewer_id"
        )
    else:
        sql = (
            "SELECT reviewer_id, username, display_name, role, is_active, created_at "
            "FROM reviewers WHERE is_active = 1 ORDER BY reviewer_id"
        )
    rows = conn.execute(sql).fetchall()
    return [
        {
            "reviewer_id": r["reviewer_id"],
            "username": r["username"],
            "display_name": r["display_name"],
            "role": r["role"],
            "is_active": r["is_active"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def set_reviewer_active(conn: sqlite3.Connection, reviewer_id: int, active: bool) -> None:
    """Set active status of a reviewer."""
    row = conn.execute("SELECT 1 FROM reviewers WHERE reviewer_id = ?", (reviewer_id,)).fetchone()
    if not row:
        raise KeyError(f"Unknown reviewer_id: {reviewer_id}")
    conn.execute(
        "UPDATE reviewers SET is_active = ? WHERE reviewer_id = ?",
        (1 if active else 0, reviewer_id),
    )
    conn.commit()


def authenticate(conn: sqlite3.Connection, username: str, password: str) -> dict | None:
    """Authenticate username and password with constant-time check path."""
    clean_username = username.strip().lower() if isinstance(username, str) else ""
    row = conn.execute(
        "SELECT reviewer_id, username, display_name, role, password_hash, is_active, created_at "
        "FROM reviewers WHERE username = ?",
        (clean_username,),
    ).fetchone()
    target_hash = row["password_hash"] if row else _DUMMY_HASH
    valid = verify_password(password, target_hash)
    if row and valid and row["is_active"] == 1:
        return {
            "reviewer_id": row["reviewer_id"],
            "username": row["username"],
            "display_name": row["display_name"],
            "role": row["role"],
            "is_active": row["is_active"],
            "created_at": row["created_at"],
        }
    return None


def create_session(conn: sqlite3.Connection, reviewer_id: int, ttl_hours: float = 12) -> str:
    """Generate and store a session token, returning the raw token once."""
    row = conn.execute(
        "SELECT is_active FROM reviewers WHERE reviewer_id = ?",
        (reviewer_id,),
    ).fetchone()
    if row is None or row["is_active"] != 1:
        raise KeyError(f"Unknown or inactive reviewer_id: {reviewer_id}")
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    start_dt = datetime.now(timezone.utc)
    expires_dt = start_dt + timedelta(hours=ttl_hours)
    conn.execute(
        "INSERT INTO sessions (token_hash, reviewer_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token_hash, reviewer_id, start_dt.isoformat(), expires_dt.isoformat()),
    )
    conn.commit()
    return token


def get_session_reviewer(conn: sqlite3.Connection, token: str) -> dict | None:
    """Look up active reviewer for a session token, purging expired sessions."""
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    current_time = now()
    conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (current_time,))
    conn.commit()
    row = conn.execute(
        """
        SELECT r.reviewer_id, r.username, r.display_name, r.role, r.is_active, r.created_at
        FROM sessions s
        JOIN reviewers r ON r.reviewer_id = s.reviewer_id
        WHERE s.token_hash = ?
        """,
        (token_hash,),
    ).fetchone()
    if not row or row["is_active"] != 1:
        return None
    return {
        "reviewer_id": row["reviewer_id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "role": row["role"],
        "is_active": row["is_active"],
        "created_at": row["created_at"],
    }


def delete_session(conn: sqlite3.Connection, token: str) -> None:
    """Delete session by token."""
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    conn.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
    conn.commit()
