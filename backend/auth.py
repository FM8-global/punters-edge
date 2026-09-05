"""Authentication module for PunterEdge"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Set

# Simple file-based auth (can upgrade to DB later)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
ADMIN_EMAIL = "info@fm8.global"


def load_users() -> dict:
    """Load approved users from file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {ADMIN_EMAIL: {"approved": True, "created": datetime.now().isoformat()}}


def save_users(users: dict):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def load_sessions() -> dict:
    """Load active sessions"""
    if SESSIONS_FILE.exists():
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_sessions(sessions: dict):
    """Save sessions"""
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)


def is_email_valid(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email


def is_user_approved(email: str) -> bool:
    """Check if email is approved"""
    users = load_users()
    return email in users and users[email].get("approved", False)


def create_session(email: str) -> str:
    """Create session token for user"""
    import secrets
    token = secrets.token_urlsafe(32)
    sessions = load_sessions()

    sessions[token] = {
        "email": email,
        "created": datetime.now().isoformat(),
        "expires": (datetime.now() + timedelta(days=30)).isoformat()
    }
    save_sessions(sessions)
    return token


def validate_session(token: Optional[str]) -> Optional[str]:
    """Validate session token, return email if valid"""
    if not token:
        return None

    sessions = load_sessions()

    if token not in sessions:
        return None

    session = sessions[token]
    expires = datetime.fromisoformat(session["expires"])

    if datetime.now() > expires:
        # Session expired, remove it
        del sessions[token]
        save_sessions(sessions)
        return None

    return session["email"]


def logout_session(token: str):
    """Remove session"""
    sessions = load_sessions()
    if token in sessions:
        del sessions[token]
        save_sessions(sessions)


def add_approved_user(email: str) -> bool:
    """Add approved user"""
    if not is_email_valid(email):
        return False

    users = load_users()
    users[email] = {
        "approved": True,
        "created": datetime.now().isoformat()
    }
    save_users(users)
    return True


def remove_approved_user(email: str) -> bool:
    """Remove approved user (except admin)"""
    if email == ADMIN_EMAIL:
        return False  # Can't remove admin

    users = load_users()
    if email in users:
        del users[email]
        save_users(users)
        return True
    return False


def get_approved_users() -> list:
    """Get all approved users"""
    users = load_users()
    return [email for email, data in users.items() if data.get("approved", False)]


def is_admin(email: str) -> bool:
    """Check if user is admin"""
    return email == ADMIN_EMAIL
