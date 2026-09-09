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

# Local development fallback - in-memory storage
_local_sessions = {}  # {token: {"email": email, "expires": datetime}}
_local_approved_users = set()  # {email1, email2, ...}
_local_pending_requests = {}  # {email: requested_timestamp}
_local_user_passwords = {}  # {email: password_hash}

def get_db_connection():
    """Get PostgreSQL connection"""
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable not set")
        return None
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def init_db():
    """Initialize database schema"""
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not set - auth disabled (use Render for PostgreSQL)")
        return

    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Cannot initialize database - connection failed")
            raise RuntimeError("DATABASE_URL environment variable not set")
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

        # CRITICAL: Ensure admin password is set correctly
        # Get a fresh connection for setting the admin password
        default_password_hash = hash_password("admin123")

        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO users (email, approved, is_admin, password_hash)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (email) DO UPDATE SET
                       password_hash = %s,
                       approved = TRUE,
                       is_admin = TRUE""",
                    (ADMIN_EMAIL, True, True, default_password_hash, default_password_hash)
                )
                conn.commit()
                cursor.close()
                conn.close()
                logger.info(f"✅ ADMIN PASSWORD SET: {ADMIN_EMAIL}")
            else:
                logger.warning("Could not set admin password - database connection failed")

        except Exception as e:
            logger.error(f"Error setting admin password: {e}")
            # Don't raise - the admin password might already be set correctly

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
        if not conn:
            logger.warning("Database not available - checking local approved users")
            return email in _local_approved_users or email == ADMIN_EMAIL
        cursor = conn.cursor()
        cursor.execute("SELECT approved FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result and result[0]
    except Exception as e:
        logger.error(f"Error checking user approval: {e}")
        # Development mode fallback
        return email in _local_approved_users or email == ADMIN_EMAIL

def create_session(email: str) -> str:
    """Create session token for user"""
    import secrets
    token = secrets.token_urlsafe(32)
    expires = datetime.now() + timedelta(days=30)

    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - using in-memory session store")
            # Store in local memory for development
            _local_sessions[token] = {"email": email, "expires": expires}
            return token
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
        # Still return token for development
        _local_sessions[token] = {"email": email, "expires": expires}

    return token

def validate_session(token: Optional[str]) -> Optional[str]:
    """Validate session token, return email if valid"""
    if not token:
        return None

    try:
        conn = get_db_connection()
        if not conn:
            # Check local session store for development
            logger.warning("Database not available - checking in-memory sessions")
            if token in _local_sessions:
                session = _local_sessions[token]
                if datetime.now() < session["expires"]:
                    return session["email"]
                else:
                    # Session expired, remove it
                    del _local_sessions[token]
            return None
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

def add_approved_user(email: str, password: str = None) -> bool:
    """Add approved user with default password"""
    if not is_email_valid(email):
        return False

    # Generate default password if not provided
    if not password:
        import secrets
        password = secrets.token_urlsafe(12)  # 12-char random password
        logger.info(f"Generated default password for {email}")

    password_hash = hash_password(password)

    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - storing approved user locally")
            _local_approved_users.add(email)
            _local_user_passwords[email] = password_hash
            return True
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, approved, password_hash) VALUES (%s, %s, %s) ON CONFLICT (email) DO UPDATE SET approved = TRUE, password_hash = %s",
            (email, True, password_hash, password_hash)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        # Development mode fallback
        _local_approved_users.add(email)
        _local_user_passwords[email] = password_hash
        return True

def remove_approved_user(email: str) -> bool:
    """Remove approved user (except admin)"""
    if email == ADMIN_EMAIL:
        return False

    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - removing approved user from local store")
            _local_approved_users.discard(email)
            return True
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = %s AND email != %s", (email, ADMIN_EMAIL))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error removing user: {e}")
        # Development mode fallback
        _local_approved_users.discard(email)
        return True

def get_approved_users() -> list:
    """Get all approved users"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - returning local approved users")
            # Always include admin
            result = list(_local_approved_users)
            if ADMIN_EMAIL not in result:
                result.append(ADMIN_EMAIL)
            return result
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE approved = TRUE")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return [row[0] for row in results]
    except Exception as e:
        logger.error(f"Error getting approved users: {e}")
        # Development mode fallback
        result = list(_local_approved_users)
        if ADMIN_EMAIL not in result:
            result.append(ADMIN_EMAIL)
        return result

def is_admin(email: str) -> bool:
    """Check if user is admin"""
    try:
        conn = get_db_connection()
        if not conn:
            # Allow info@fm8.global as admin fallback when DB unavailable
            return email == ADMIN_EMAIL
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
        if not conn:
            logger.warning("Database not available - storing pending request locally")
            # Check if already approved or pending
            if email in _local_approved_users:
                return False
            if email in _local_pending_requests:
                return False
            _local_pending_requests[email] = datetime.now()
            return True

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
        # Development mode fallback
        if email not in _local_approved_users and email not in _local_pending_requests:
            _local_pending_requests[email] = datetime.now()
            return True
        return False

def get_pending_requests() -> list:
    """Get all pending access requests"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - returning local pending requests")
            return [
                {"email": email, "requested": timestamp.isoformat()}
                for email, timestamp in _local_pending_requests.items()
            ]
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
        # Development mode fallback
        return [
            {"email": email, "requested": timestamp.isoformat()}
            for email, timestamp in _local_pending_requests.items()
        ]

def approve_request(email: str) -> bool:
    """Approve a pending access request"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - approving request locally")
            # Check if pending exists
            if email not in _local_pending_requests:
                return False
            # Add to approved users and remove from pending
            add_approved_user(email)
            _local_pending_requests.pop(email, None)
            return True

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
        # Development mode fallback
        if email in _local_pending_requests:
            add_approved_user(email)
            _local_pending_requests.pop(email, None)
            return True
        return False

def reject_request(email: str) -> bool:
    """Reject a pending access request"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - rejecting request locally")
            _local_pending_requests.pop(email, None)
            return True
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending WHERE email = %s", (email,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error rejecting request: {e}")
        # Development mode fallback
        _local_pending_requests.pop(email, None)
        return True

def verify_admin_password(password: str) -> bool:
    """Verify admin password for info@fm8.global"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - using local development password")
            # Local development fallback: accept default admin password
            return password == "admin123"
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = %s", (ADMIN_EMAIL,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            # If user doesn't exist in DB, try default password for development
            return password == "admin123"

        password_hash = result[0]
        return verify_password(password, password_hash) if password_hash else False
    except Exception as e:
        logger.error(f"Error verifying admin password: {e}")
        # Development fallback
        return password == "admin123"

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

def set_user_password(email: str, password: str) -> bool:
    """Set password for a regular user"""
    email = email.lower().strip()
    if not is_email_valid(email):
        return False

    password_hash = hash_password(password)
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - storing password locally")
            _local_user_passwords[email] = password_hash
            return True
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = %s",
            (password_hash, email)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error setting user password: {e}")
        # Fallback to local storage
        _local_user_passwords[email] = password_hash
        return True

def verify_user_password(email: str, password: str) -> bool:
    """Verify password for a regular user"""
    email = email.lower().strip()
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - checking local passwords")
            if email in _local_user_passwords:
                return verify_password(password, _local_user_passwords[email])
            return False
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result or not result[0]:
            return False

        return verify_password(password, result[0])
    except Exception as e:
        logger.error(f"Error verifying user password: {e}")
        return False
