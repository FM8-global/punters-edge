"""Authentication module for PunterEdge"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Set

# Simple file-based auth (can upgrade to DB later)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
PENDING_FILE = DATA_DIR / "pending.json"
ADMIN_EMAIL = "info@fm8.global"


def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == password_hash


def load_users() -> dict:
    """Load approved users from file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    # Create default admin with password (default: admin123)
    default_password_hash = hash_password("admin123")
    return {
        ADMIN_EMAIL: {
            "approved": True,
            "created": datetime.now().isoformat(),
            "password_hash": default_password_hash
        }
    }


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
    users = load_users()
    if email not in users:
        return False
    return users[email].get("is_admin", False) or email == ADMIN_EMAIL


def make_admin(email: str) -> bool:
    """Make user an admin (requires calling user to be admin)"""
    users = load_users()
    if email not in users:
        return False
    users[email]["is_admin"] = True
    save_users(users)
    return True


def remove_admin(email: str) -> bool:
    """Remove admin privileges (except main admin)"""
    if email == ADMIN_EMAIL:
        return False  # Can't remove main admin

    users = load_users()
    if email in users:
        users[email]["is_admin"] = False
        save_users(users)
        return True
    return False


def get_all_users() -> dict:
    """Get all users with their info"""
    return load_users()


def load_pending() -> dict:
    """Load pending access requests"""
    if PENDING_FILE.exists():
        with open(PENDING_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_pending(pending: dict):
    """Save pending requests"""
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=2)


def request_access(email: str) -> bool:
    """Create a pending access request"""
    if not is_email_valid(email):
        return False

    # Check if already approved or pending
    users = load_users()
    if email in users:
        return False  # User already exists

    pending = load_pending()
    if email in pending:
        return False  # Already pending

    pending[email] = {
        "requested": datetime.now().isoformat(),
        "status": "pending"
    }
    save_pending(pending)
    return True


def get_pending_requests() -> list:
    """Get all pending access requests"""
    pending = load_pending()
    return [
        {"email": email, "requested": data.get("requested", "")}
        for email, data in pending.items()
        if data.get("status") == "pending"
    ]


def approve_request(email: str) -> bool:
    """Approve a pending access request"""
    pending = load_pending()
    if email not in pending:
        return False

    # Add to approved users
    if add_approved_user(email):
        # Remove from pending
        del pending[email]
        save_pending(pending)
        return True
    return False


def reject_request(email: str) -> bool:
    """Reject a pending access request"""
    pending = load_pending()
    if email not in pending:
        return False

    del pending[email]
    save_pending(pending)
    return True


def verify_admin_password(password: str) -> bool:
    """Verify admin password for info@fm8.global"""
    users = load_users()
    if ADMIN_EMAIL not in users:
        return False

    password_hash = users[ADMIN_EMAIL].get("password_hash")
    if not password_hash:
        return False

    return verify_password(password, password_hash)


def set_admin_password(password: str) -> bool:
    """Set a new admin password"""
    users = load_users()
    if ADMIN_EMAIL not in users:
        return False

    users[ADMIN_EMAIL]["password_hash"] = hash_password(password)
    save_users(users)
    return True
