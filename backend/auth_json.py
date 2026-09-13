"""Authentication module for PunterEdge - JSON file backed (for local testing)"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "info@fm8.global"
DATA_DIR = Path(__file__).parent / "data"
USERS_FILE = DATA_DIR / "users.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"
PENDING_FILE = DATA_DIR / "pending.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

def load_json_file(filepath: Path, default=None):
    """Load JSON file or return default"""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return default or {}

def save_json_file(filepath: Path, data: dict):
    """Save data to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False

def init_db():
    """Initialize database schema (JSON files)"""
    try:
        # Initialize users file if not exists
        if not USERS_FILE.exists():
            users = {
                ADMIN_EMAIL: {
                    "approved": True,
                    "is_admin": True,
                    "password_hash": hash_password("admin123"),
                    "created": datetime.now().isoformat()
                }
            }
            save_json_file(USERS_FILE, users)
            logger.info(f"Initialized default admin: {ADMIN_EMAIL}")

        # Initialize sessions file if not exists
        if not SESSIONS_FILE.exists():
            save_json_file(SESSIONS_FILE, {})

        # Initialize pending file if not exists
        if not PENDING_FILE.exists():
            save_json_file(PENDING_FILE, {})

        logger.info("Database (JSON files) initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

def is_email_valid(email: str) -> bool:
    """Basic email validation"""
    return "@" in email and "." in email

def is_user_approved(email: str) -> bool:
    """Check if email is approved"""
    try:
        users = load_json_file(USERS_FILE)
        user = users.get(email)
        return user and user.get("approved", False)
    except Exception as e:
        logger.error(f"Error checking user approval: {e}")
        return False

def create_session(email: str) -> str:
    """Create session token for user"""
    import secrets
    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(days=30)).isoformat()

    try:
        sessions = load_json_file(SESSIONS_FILE)
        sessions[token] = {
            "email": email,
            "created": datetime.now().isoformat(),
            "expires": expires
        }
        save_json_file(SESSIONS_FILE, sessions)
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise

    return token

def validate_session(token: Optional[str]) -> Optional[str]:
    """Validate session token, return email if valid"""
    if not token:
        return None

    try:
        sessions = load_json_file(SESSIONS_FILE)
        session = sessions.get(token)

        if not session:
            return None

        expires = datetime.fromisoformat(session["expires"])

        if expires < datetime.now():
            # Session expired, delete it
            del sessions[token]
            save_json_file(SESSIONS_FILE, sessions)
            return None

        return session.get("email")
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        return None

def logout_session(token: str):
    """Remove session"""
    try:
        sessions = load_json_file(SESSIONS_FILE)
        if token in sessions:
            del sessions[token]
            save_json_file(SESSIONS_FILE, sessions)
    except Exception as e:
        logger.error(f"Error logging out: {e}")

def add_approved_user(email: str) -> bool:
    """Add approved user"""
    if not is_email_valid(email):
        return False

    try:
        users = load_json_file(USERS_FILE)
        if email in users:
            users[email]["approved"] = True
        else:
            users[email] = {
                "approved": True,
                "is_admin": False,
                "password_hash": None,
                "created": datetime.now().isoformat()
            }
        return save_json_file(USERS_FILE, users)
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False

def remove_approved_user(email: str) -> bool:
    """Remove approved user (except admin)"""
    if email == ADMIN_EMAIL:
        return False

    try:
        users = load_json_file(USERS_FILE)
        if email in users:
            del users[email]
            return save_json_file(USERS_FILE, users)
        return True
    except Exception as e:
        logger.error(f"Error removing user: {e}")
        return False

def get_approved_users() -> list:
    """Get all approved users"""
    try:
        users = load_json_file(USERS_FILE)
        return [email for email, user in users.items() if user.get("approved", False)]
    except Exception as e:
        logger.error(f"Error getting approved users: {e}")
        return []

def is_admin(email: str) -> bool:
    """Check if user is admin"""
    try:
        if email == ADMIN_EMAIL:
            return True
        users = load_json_file(USERS_FILE)
        user = users.get(email)
        return user and user.get("is_admin", False)
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

def make_admin(email: str) -> bool:
    """Make user an admin"""
    try:
        users = load_json_file(USERS_FILE)
        if email not in users:
            users[email] = {
                "approved": True,
                "is_admin": True,
                "password_hash": None,
                "created": datetime.now().isoformat()
            }
        else:
            users[email]["is_admin"] = True
        return save_json_file(USERS_FILE, users)
    except Exception as e:
        logger.error(f"Error promoting user to admin: {e}")
        return False

def remove_admin(email: str) -> bool:
    """Remove admin privileges (except main admin)"""
    if email == ADMIN_EMAIL:
        return False

    try:
        users = load_json_file(USERS_FILE)
        if email in users:
            users[email]["is_admin"] = False
            return save_json_file(USERS_FILE, users)
        return True
    except Exception as e:
        logger.error(f"Error removing admin status: {e}")
        return False

def get_all_users() -> dict:
    """Get all users with their info"""
    try:
        users = load_json_file(USERS_FILE)
        result = {}
        for email, user in users.items():
            result[email] = {
                "approved": user.get("approved", False),
                "is_admin": user.get("is_admin", False) or email == ADMIN_EMAIL,
                "created": user.get("created", "")
            }
        return result
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return {}

def request_access(email: str) -> bool:
    """Create a pending access request"""
    if not is_email_valid(email):
        return False

    try:
        users = load_json_file(USERS_FILE)
        pending = load_json_file(PENDING_FILE)

        # Check if already approved or pending
        if email in users or email in pending:
            return False

        pending[email] = {
            "requested": datetime.now().isoformat(),
            "status": "pending"
        }
        return save_json_file(PENDING_FILE, pending)
    except Exception as e:
        logger.error(f"Error requesting access: {e}")
        return False

def get_pending_requests() -> list:
    """Get all pending access requests"""
    try:
        pending = load_json_file(PENDING_FILE)
        return [
            {"email": email, "requested": data.get("requested", "")}
            for email, data in pending.items()
            if data.get("status") == "pending"
        ]
    except Exception as e:
        logger.error(f"Error getting pending requests: {e}")
        return []

def approve_request(email: str) -> tuple:
    """Approve a pending access request and return generated password"""
    try:
        import secrets
        # Generate temporary password
        temp_password = secrets.token_urlsafe(12)

        pending = load_json_file(PENDING_FILE)

        if email not in pending:
            return False, None

        # Add to approved users with password
        if add_approved_user(email, temp_password):
            del pending[email]
            if save_json_file(PENDING_FILE, pending):
                return True, temp_password
            return False, None

        return False, None
    except Exception as e:
        logger.error(f"Error approving request: {e}")
        return False, None

def reject_request(email: str) -> bool:
    """Reject a pending access request"""
    try:
        pending = load_json_file(PENDING_FILE)
        if email in pending:
            del pending[email]
            return save_json_file(PENDING_FILE, pending)
        return True
    except Exception as e:
        logger.error(f"Error rejecting request: {e}")
        return False

def verify_admin_password(password: str) -> bool:
    """Verify admin password for info@fm8.global"""
    try:
        users = load_json_file(USERS_FILE)
        user = users.get(ADMIN_EMAIL)

        if not user:
            return False

        password_hash = user.get("password_hash")
        return verify_password(password, password_hash) if password_hash else False
    except Exception as e:
        logger.error(f"Error verifying admin password: {e}")
        return False

def set_admin_password(password: str) -> bool:
    """Set a new admin password"""
    try:
        users = load_json_file(USERS_FILE)
        if ADMIN_EMAIL in users:
            users[ADMIN_EMAIL]["password_hash"] = hash_password(password)
            return save_json_file(USERS_FILE, users)
        return False
    except Exception as e:
        logger.error(f"Error setting admin password: {e}")
        return False
