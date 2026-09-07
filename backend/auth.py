"""Authentication module for PunterEdge - PostgreSQL backed"""

import os
import hashlib
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

ADMIN_EMAIL = "info@fm8.global"

# Database connection from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

def get_db_connection():
    """Get PostgreSQL connection"""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable not set")
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Initialize database schema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(255) PRIMARY KEY,
                approved BOOLEAN DEFAULT FALSE,
                is_admin BOOLEAN DEFAULT FALSE,
                password_hash VARCHAR(255),
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token VARCHAR(255) PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires TIMESTAMP NOT NULL,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

        # Pending requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending (
                email VARCHAR(255) PRIMARY KEY,
                requested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'pending'
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_email ON sessions(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires)")

        conn.commit()
        cursor.close()
        conn.close()

        # Initialize default admin if not exists
        if not is_user_approved(ADMIN_EMAIL):
            default_password_hash = hash_password("admin123")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, approved, is_admin, password_hash) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (ADMIN_EMAIL, True, True, default_password_hash)
            )
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Initialized default admin: {ADMIN_EMAIL}")

        logger.info("Database schema initialized successfully")
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT approved FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result and result[0]
    except Exception as e:
        logger.error(f"Error checking user approval: {e}")
        return False

def create_session(email: str) -> str:
    """Create session token for user"""
    import secrets
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(days=30)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (token, email, expires) VALUES (%s, %s, %s)",
            (token, email, expires)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise

    return token

def validate_session(token: Optional[str]) -> Optional[str]:
    """Validate session token, return email if valid"""
    if not token:
        return None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email, expires FROM sessions WHERE token = %s", (token,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return None

        email, expires = result

        if datetime.fromisoformat(expires.isoformat()) < datetime.now():
            # Session expired, delete it
            cursor.execute("DELETE FROM sessions WHERE token = %s", (token,))
            conn.commit()
            cursor.close()
            conn.close()
            return None

        cursor.close()
        conn.close()
        return email
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        return None

def logout_session(token: str):
    """Remove session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = %s", (token,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging out: {e}")

def add_approved_user(email: str) -> bool:
    """Add approved user"""
    if not is_email_valid(email):
        return False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, approved) VALUES (%s, %s) ON CONFLICT (email) DO UPDATE SET approved = TRUE",
            (email, True)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False

def remove_approved_user(email: str) -> bool:
    """Remove approved user (except admin)"""
    if email == ADMIN_EMAIL:
        return False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = %s AND email != %s", (email, ADMIN_EMAIL))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error removing user: {e}")
        return False

def get_approved_users() -> list:
    """Get all approved users"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE approved = TRUE")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row[0] for row in results]
    except Exception as e:
        logger.error(f"Error getting approved users: {e}")
        return []

def is_admin(email: str) -> bool:
    """Check if user is admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return (result and result[0]) or email == ADMIN_EMAIL
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

def make_admin(email: str) -> bool:
    """Make user an admin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_admin = TRUE WHERE email = %s", (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error promoting user to admin: {e}")
        return False

def remove_admin(email: str) -> bool:
    """Remove admin privileges (except main admin)"""
    if email == ADMIN_EMAIL:
        return False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_admin = FALSE WHERE email = %s", (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error removing admin status: {e}")
        return False

def get_all_users() -> dict:
    """Get all users with their info"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email, approved, is_admin, created FROM users")
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        users = {}
        for email, approved, is_admin_flag, created in results:
            users[email] = {
                "approved": approved,
                "is_admin": is_admin_flag or email == ADMIN_EMAIL,
                "created": created.isoformat() if created else ""
            }
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return {}

def request_access(email: str) -> bool:
    """Create a pending access request"""
    if not is_email_valid(email):
        return False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if already approved or pending
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        cursor.execute("SELECT email FROM pending WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        cursor.execute(
            "INSERT INTO pending (email, status) VALUES (%s, %s)",
            (email, "pending")
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error requesting access: {e}")
        return False

def get_pending_requests() -> list:
    """Get all pending access requests"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email, requested FROM pending WHERE status = %s", ("pending",))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            {"email": row[0], "requested": row[1].isoformat() if row[1] else ""}
            for row in results
        ]
    except Exception as e:
        logger.error(f"Error getting pending requests: {e}")
        return []

def approve_request(email: str) -> bool:
    """Approve a pending access request"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if pending exists
        cursor.execute("SELECT email FROM pending WHERE email = %s", (email,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return False

        # Add to approved users
        if add_approved_user(email):
            cursor.execute("DELETE FROM pending WHERE email = %s", (email,))
            conn.commit()
            cursor.close()
            conn.close()
            return True

        cursor.close()
        conn.close()
        return False
    except Exception as e:
        logger.error(f"Error approving request: {e}")
        return False

def reject_request(email: str) -> bool:
    """Reject a pending access request"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending WHERE email = %s", (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error rejecting request: {e}")
        return False

def verify_admin_password(password: str) -> bool:
    """Verify admin password for info@fm8.global"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = %s", (ADMIN_EMAIL,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return False

        password_hash = result[0]
        return verify_password(password, password_hash) if password_hash else False
    except Exception as e:
        logger.error(f"Error verifying admin password: {e}")
        return False

def set_admin_password(password: str) -> bool:
    """Set a new admin password"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (hash_password(password), ADMIN_EMAIL)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error setting admin password: {e}")
        return False
