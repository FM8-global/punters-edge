"""Australian Gambling Compliance Module for PunterEdge - JSON backed (testing)

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

from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
KYC_FILE = DATA_DIR / "kyc.json"
RG_FILE = DATA_DIR / "responsible_gambling.json"
ACTIVITY_FILE = DATA_DIR / "betting_activity.json"
ALERTS_FILE = DATA_DIR / "compliance_alerts.json"

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

def init_compliance_tables():
    """Initialize compliance tracking tables (JSON files)"""
    try:
        # Ensure all compliance JSON files exist
        if not KYC_FILE.exists():
            save_json_file(KYC_FILE, {})
        if not RG_FILE.exists():
            save_json_file(RG_FILE, {})
        if not ACTIVITY_FILE.exists():
            save_json_file(ACTIVITY_FILE, {})
        if not ALERTS_FILE.exists():
            save_json_file(ALERTS_FILE, {})

        logger.info("Compliance tables (JSON files) initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing compliance tables: {e}")
        raise

def verify_age(email: str, date_of_birth: str) -> bool:
    """Verify user age (18+ for gambling)"""
    try:
        dob = datetime.fromisoformat(date_of_birth)
        age = (datetime.now() - dob).days // 365

        if age < 18:
            return False

        kyc = load_json_file(KYC_FILE)
        kyc[email] = {
            "date_of_birth": date_of_birth,
            "verified_age": True,
            "verified_identity": kyc.get(email, {}).get("verified_identity", False),
            "verification_date": datetime.now().isoformat(),
            "verification_method": "date_of_birth"
        }
        save_json_file(KYC_FILE, kyc)
        return True
    except Exception as e:
        logger.error(f"Error verifying age: {e}")
        return False

def is_age_verified(email: str) -> bool:
    """Check if user age is verified"""
    try:
        kyc = load_json_file(KYC_FILE)
        user_kyc = kyc.get(email, {})
        return user_kyc.get("verified_age", False)
    except Exception as e:
        logger.error(f"Error checking age verification: {e}")
        return False

def is_self_excluded(email: str) -> bool:
    """Check if user has self-excluded"""
    try:
        rg = load_json_file(RG_FILE)
        user_rg = rg.get(email, {})

        if not user_rg.get("self_excluded", False):
            return False

        # Check if exclusion period has expired
        excluded_until = user_rg.get("self_excluded_until")
        if excluded_until:
            excluded_until_dt = datetime.fromisoformat(excluded_until)
            if excluded_until_dt > datetime.now():
                return True
            else:
                # Exclusion period expired, remove it
                user_rg["self_excluded"] = False
                rg[email] = user_rg
                save_json_file(RG_FILE, rg)
                return False

        return True
    except Exception as e:
        logger.error(f"Error checking self-exclusion: {e}")
        return False

def set_betting_limits(email: str, daily_limit: Optional[float] = None,
                       weekly_limit: Optional[float] = None,
                       monthly_limit: Optional[float] = None,
                       session_minutes: Optional[int] = None) -> bool:
    """Set betting limits for user"""
    try:
        rg = load_json_file(RG_FILE)

        if email not in rg:
            rg[email] = {}

        if daily_limit is not None:
            rg[email]["daily_limit"] = daily_limit
        if weekly_limit is not None:
            rg[email]["weekly_limit"] = weekly_limit
        if monthly_limit is not None:
            rg[email]["monthly_limit"] = monthly_limit
        if session_minutes is not None:
            rg[email]["session_limit_minutes"] = session_minutes

        rg[email]["last_modified"] = datetime.now().isoformat()
        return save_json_file(RG_FILE, rg)
    except Exception as e:
        logger.error(f"Error setting betting limits: {e}")
        return False

def get_betting_limits(email: str) -> dict:
    """Get betting limits for user"""
    try:
        rg = load_json_file(RG_FILE)
        return rg.get(email, {})
    except Exception as e:
        logger.error(f"Error getting betting limits: {e}")
        return {}

def request_self_exclusion(email: str, duration_days: int = 180,
                          reason: Optional[str] = None) -> bool:
    """Request self-exclusion"""
    try:
        rg = load_json_file(RG_FILE)

        if email not in rg:
            rg[email] = {}

        rg[email]["self_excluded"] = True
        rg[email]["self_excluded_until"] = (
            datetime.now() + timedelta(days=duration_days)
        ).isoformat()
        rg[email]["last_modified"] = datetime.now().isoformat()

        result = save_json_file(RG_FILE, rg)

        # Log the self-exclusion request
        if result and reason:
            log_betting_activity(email, "self_exclusion_request",
                                {"reason": reason, "duration_days": duration_days})

        return result
    except Exception as e:
        logger.error(f"Error requesting self-exclusion: {e}")
        return False

def log_betting_activity(email: str, action: str, details: dict,
                        amount: Optional[float] = None,
                        ip_address: Optional[str] = None) -> bool:
    """Log betting activity for audit trail"""
    try:
        activity = load_json_file(ACTIVITY_FILE)

        if email not in activity:
            activity[email] = []

        activity[email].append({
            "action": action,
            "amount": amount,
            "bet_details": details,
            "ip_address": ip_address,
            "timestamp": datetime.now().isoformat()
        })

        return save_json_file(ACTIVITY_FILE, activity)
    except Exception as e:
        logger.error(f"Error logging betting activity: {e}")
        return False

def get_compliance_report(email: str) -> dict:
    """Get compliance report for user"""
    try:
        kyc = load_json_file(KYC_FILE)
        rg = load_json_file(RG_FILE)
        activity = load_json_file(ACTIVITY_FILE)

        kyc_data = kyc.get(email, {})
        rg_data = rg.get(email, {})
        activity_data = activity.get(email, [])

        return {
            "kyc": kyc_data,
            "responsible_gambling": rg_data,
            "activity_log": activity_data[-10:] if activity_data else []  # Last 10 activities
        }
    except Exception as e:
        logger.error(f"Error getting compliance report: {e}")
        return {}

def create_compliance_alert(alert_type: str, email: str,
                           message: str, severity: str = "info") -> bool:
    """Create compliance alert"""
    try:
        alerts = load_json_file(ALERTS_FILE)

        if email not in alerts:
            alerts[email] = []

        alerts[email].append({
            "type": alert_type,
            "message": message,
            "severity": severity,
            "created": datetime.now().isoformat()
        })

        return save_json_file(ALERTS_FILE, alerts)
    except Exception as e:
        logger.error(f"Error creating compliance alert: {e}")
        return False
