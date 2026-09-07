"""Australian Gambling Compliance Module for PunterEdge

IMPORTANT DISCLAIMER:
This module provides general compliance features for Australian gambling regulations.
It is NOT a substitute for legal advice. You MUST work with a qualified legal expert
specializing in Australian gambling law to ensure full compliance with:
- Federal Interactive Gambling Act 2001 (IGA)
- State/Territory gambling regulations
- AML/CTF Act 2006
- Your specific licensing requirements

Compliance requirements vary by state and licensing status.
"""

import psycopg2
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")

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

def init_compliance_tables():
    """Initialize compliance tracking tables"""
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not set - compliance tracking disabled (use Render for PostgreSQL)")
        return

    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Cannot initialize compliance tables - connection failed")
            return
        cursor = conn.cursor()

        # Compliance/KYC data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kyc_data (
                email VARCHAR(255) PRIMARY KEY,
                date_of_birth DATE,
                verified_age BOOLEAN DEFAULT FALSE,
                verified_identity BOOLEAN DEFAULT FALSE,
                verification_date TIMESTAMP,
                verification_method VARCHAR(255),
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

        # Responsible gambling settings per user
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS responsible_gambling (
                email VARCHAR(255) PRIMARY KEY,
                daily_limit DECIMAL(10, 2),
                weekly_limit DECIMAL(10, 2),
                monthly_limit DECIMAL(10, 2),
                session_limit_minutes INTEGER,
                self_excluded BOOLEAN DEFAULT FALSE,
                self_excluded_until TIMESTAMP,
                deposit_limit DECIMAL(10, 2),
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

        # Betting activity logs for audit trail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS betting_activity_log (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                action VARCHAR(255),
                amount DECIMAL(10, 2),
                bet_details JSONB,
                ip_address VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

        # Self-exclusion requests
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS self_exclusion_requests (
                email VARCHAR(255) PRIMARY KEY,
                requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exclusion_period_days INTEGER DEFAULT 6*30,
                end_date TIMESTAMP,
                reason VARCHAR(255),
                status VARCHAR(50) DEFAULT 'active',
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

        # Compliance alerts and incidents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_alerts (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255),
                alert_type VARCHAR(255),
                description TEXT,
                severity VARCHAR(50),
                resolved BOOLEAN DEFAULT FALSE,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_date TIMESTAMP
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_kyc_verified ON kyc_data(verified_age, verified_identity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_betting_activity_email ON betting_activity_log(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_betting_activity_timestamp ON betting_activity_log(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_self_exclusion_status ON self_exclusion_requests(status)")

        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Compliance tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing compliance tables: {e}")
        raise

def verify_age(email: str, date_of_birth: str) -> bool:
    """
    Verify user is 18+ years old (required for Australian gambling)

    Args:
        email: User email
        date_of_birth: ISO format date (YYYY-MM-DD)

    Returns:
        True if user is 18+, False otherwise
    """
    try:
        dob = datetime.fromisoformat(date_of_birth).date()
        today = datetime.now().date()
        age = (today.year - dob.year) - ((today.month, today.day) < (dob.month, dob.day))

        if age >= 18:
            # Store verification in database
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO kyc_data (email, date_of_birth, verified_age, verification_date, verification_method)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (email) DO UPDATE SET verified_age = TRUE, verification_date = CURRENT_TIMESTAMP""",
                (email, dob, True, datetime.now(), "age_verification")
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    except Exception as e:
        logger.error(f"Error verifying age: {e}")
        return False

def is_age_verified(email: str) -> bool:
    """Check if user has been age verified"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT verified_age FROM kyc_data WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result and result[0]
    except Exception as e:
        logger.error(f"Error checking age verification: {e}")
        return False

def set_betting_limits(email: str, daily_limit: float = None, weekly_limit: float = None,
                      monthly_limit: float = None, session_minutes: int = None) -> bool:
    """Set responsible gambling limits for user (Australian requirement)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO responsible_gambling (email, daily_limit, weekly_limit, monthly_limit, session_limit_minutes)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (email) DO UPDATE SET
               daily_limit = COALESCE(%s, daily_limit),
               weekly_limit = COALESCE(%s, weekly_limit),
               monthly_limit = COALESCE(%s, monthly_limit),
               session_limit_minutes = COALESCE(%s, session_limit_minutes),
               last_modified = CURRENT_TIMESTAMP""",
            (email, daily_limit, weekly_limit, monthly_limit, session_minutes,
             daily_limit, weekly_limit, monthly_limit, session_minutes)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error setting betting limits: {e}")
        return False

def get_betting_limits(email: str) -> Dict:
    """Get user's betting limits"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT daily_limit, weekly_limit, monthly_limit, session_limit_minutes FROM responsible_gambling WHERE email = %s",
            (email,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return {
                "daily_limit": float(result[0]) if result[0] else None,
                "weekly_limit": float(result[1]) if result[1] else None,
                "monthly_limit": float(result[2]) if result[2] else None,
                "session_minutes": result[3]
            }
        return {}
    except Exception as e:
        logger.error(f"Error getting betting limits: {e}")
        return {}

def request_self_exclusion(email: str, duration_days: int = 180, reason: str = None) -> bool:
    """Request self-exclusion from gambling (Australian responsible gambling feature)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        end_date = datetime.now() + timedelta(days=duration_days)

        cursor.execute(
            """INSERT INTO self_exclusion_requests (email, exclusion_period_days, end_date, reason, status)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (email) DO UPDATE SET
               status = 'active',
               end_date = %s,
               requested_date = CURRENT_TIMESTAMP""",
            (email, duration_days, end_date, reason, 'active', end_date)
        )

        # Update responsible gambling table
        cursor.execute(
            "UPDATE responsible_gambling SET self_excluded = TRUE, self_excluded_until = %s WHERE email = %s",
            (end_date, email)
        )

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error requesting self-exclusion: {e}")
        return False

def is_self_excluded(email: str) -> bool:
    """Check if user has active self-exclusion"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status, end_date FROM self_exclusion_requests WHERE email = %s",
            (email,)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            status, end_date = result
            if status == 'active':
                if datetime.fromisoformat(end_date.isoformat()) > datetime.now():
                    return True
                # Exclusion period expired, mark as inactive
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE self_exclusion_requests SET status = 'expired' WHERE email = %s", (email,))
                conn.commit()
                cursor.close()
                conn.close()
        return False
    except Exception as e:
        logger.error(f"Error checking self-exclusion: {e}")
        return False

def log_betting_activity(email: str, action: str, amount: float = None,
                        bet_details: dict = None, ip_address: str = None) -> bool:
    """Log betting activity for audit trail (compliance requirement)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        import json
        cursor.execute(
            """INSERT INTO betting_activity_log (email, action, amount, bet_details, ip_address)
               VALUES (%s, %s, %s, %s, %s)""",
            (email, action, amount, json.dumps(bet_details or {}), ip_address)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error logging betting activity: {e}")
        return False

def get_compliance_report(email: str) -> Dict:
    """Get compliance report for user (admin use)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get KYC data
        cursor.execute("SELECT verified_age, verified_identity, verification_date FROM kyc_data WHERE email = %s", (email,))
        kyc = cursor.fetchone()

        # Get responsible gambling settings
        cursor.execute(
            "SELECT daily_limit, weekly_limit, monthly_limit, session_limit_minutes, self_excluded FROM responsible_gambling WHERE email = %s",
            (email,)
        )
        rg = cursor.fetchone()

        # Get self-exclusion status
        cursor.execute(
            "SELECT status, end_date FROM self_exclusion_requests WHERE email = %s",
            (email,)
        )
        se = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "email": email,
            "age_verified": kyc[0] if kyc else False,
            "identity_verified": kyc[1] if kyc else False,
            "verification_date": kyc[2].isoformat() if kyc and kyc[2] else None,
            "betting_limits": {
                "daily": float(rg[0]) if rg and rg[0] else None,
                "weekly": float(rg[1]) if rg and rg[1] else None,
                "monthly": float(rg[2]) if rg and rg[2] else None,
                "session_minutes": rg[3] if rg else None
            },
            "self_excluded": rg[4] if rg else False,
            "exclusion_status": se[0] if se else None,
            "exclusion_end_date": se[1].isoformat() if se and se[1] else None
        }
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        return {}

def create_compliance_alert(email: str, alert_type: str, description: str, severity: str = "info") -> bool:
    """Create compliance alert for audit trail"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO compliance_alerts (email, alert_type, description, severity)
               VALUES (%s, %s, %s, %s)""",
            (email, alert_type, description, severity)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating compliance alert: {e}")
        return False
