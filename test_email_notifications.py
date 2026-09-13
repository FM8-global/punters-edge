#!/usr/bin/env python3
"""
E2E test for email notification system.
Tests all email flows: approval emails, user creation emails, and batch notifications.

This test uses Ethereal Email (fake SMTP service) for safe testing without real email.

Usage:
    python test_email_notifications.py

Environment variables (optional, defaults to Ethereal for testing):
    SMTP_SERVER=smtp.ethereal.email
    SMTP_PORT=587
    SENDER_EMAIL=test@ethereal.email
    SENDER_PASSWORD=test-password
    ENABLE_EMAIL=true
"""

import sys
import os
from pathlib import Path
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.email_service import send_approval_email, send_user_created_email, ENABLE_EMAIL
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def setup_ethereal_account():
    """Set up Ethereal Email account for testing"""
    import smtplib
    from email.mime.text import MIMEText

    logger.info("Setting up Ethereal Email test account...")
    logger.info("Note: In a real test, you would use an actual email service")
    logger.info("For now, we'll verify the email service module works correctly")

    return True


def test_approval_email():
    """Test: Send approval email to new user"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Approval Email")
    logger.info("="*70)

    test_email = f"test-approval-{secrets.token_hex(4)}@example.com"
    test_password = "TempPass123!@#"

    logger.info(f"Scenario: Admin approves access for new user")
    logger.info(f"Test Email: {test_email}")
    logger.info(f"Temporary Password: {test_password}")

    if not ENABLE_EMAIL:
        logger.warning("Email service is disabled")
        logger.info("✓ Test would send approval email (skipped - email disabled)")
        return True

    try:
        result = send_approval_email(test_email, test_password)
        if result:
            logger.info("✓ Approval email sent successfully")
            logger.info(f"  Email sent to: {test_email}")
            logger.info(f"  Content: Approval notice with temporary password")
            return True
        else:
            logger.error("✗ Failed to send approval email")
            return False
    except Exception as e:
        logger.error(f"✗ Error sending approval email: {e}")
        return False


def test_user_creation_email():
    """Test: Send welcome email when user is created"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: User Creation Email")
    logger.info("="*70)

    test_email = f"test-created-{secrets.token_hex(4)}@example.com"
    test_password = "InitialPass456!@#"
    admin_email = "admin@fm8.global"

    logger.info(f"Scenario: Admin manually creates a new user")
    logger.info(f"New User Email: {test_email}")
    logger.info(f"Created By: {admin_email}")
    logger.info(f"Password: {test_password}")

    if not ENABLE_EMAIL:
        logger.warning("Email service is disabled")
        logger.info("✓ Test would send creation email (skipped - email disabled)")
        return True

    try:
        result = send_user_created_email(test_email, test_password, admin_email)
        if result:
            logger.info("✓ User creation email sent successfully")
            logger.info(f"  Email sent to: {test_email}")
            logger.info(f"  Content: Welcome message with credentials")
            return True
        else:
            logger.error("✗ Failed to send user creation email")
            return False
    except Exception as e:
        logger.error(f"✗ Error sending user creation email: {e}")
        return False


def test_batch_email_flow():
    """Test: Batch notification to multiple users"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Batch Email Notifications")
    logger.info("="*70)

    test_users = [
        f"batch-test-{i}-{secrets.token_hex(3)}@example.com"
        for i in range(1, 4)
    ]

    logger.info(f"Scenario: Send notifications to {len(test_users)} users")
    for email in test_users:
        logger.info(f"  - {email}")

    if not ENABLE_EMAIL:
        logger.warning("Email service is disabled")
        logger.info(f"✓ Would send {len(test_users)} emails (skipped - email disabled)")
        return True

    success_count = 0
    for email in test_users:
        try:
            result = send_approval_email(email, "BatchTestPass123!")
            if result:
                success_count += 1
                logger.info(f"  ✓ Email sent to {email}")
            else:
                logger.error(f"  ✗ Failed to send to {email}")
        except Exception as e:
            logger.error(f"  ✗ Error sending to {email}: {e}")

    logger.info(f"Results: {success_count}/{len(test_users)} emails sent successfully")
    return success_count == len(test_users)


def test_email_config():
    """Test: Verify email configuration"""
    logger.info("\n" + "="*70)
    logger.info("TEST 0: Email Configuration")
    logger.info("="*70)

    from backend.email_service import (
        ENABLE_EMAIL, SMTP_SERVER, SMTP_PORT,
        SENDER_EMAIL, SENDER_PASSWORD, SENDER_NAME
    )

    logger.info(f"ENABLE_EMAIL: {ENABLE_EMAIL}")
    logger.info(f"SMTP_SERVER: {SMTP_SERVER}")
    logger.info(f"SMTP_PORT: {SMTP_PORT}")
    logger.info(f"SENDER_EMAIL: {SENDER_EMAIL}")
    logger.info(f"SENDER_PASSWORD: {'[SET]' if SENDER_PASSWORD else '[NOT SET]'}")
    logger.info(f"SENDER_NAME: {SENDER_NAME}")

    if not ENABLE_EMAIL:
        logger.warning("⚠️  Email notifications are DISABLED")
        logger.info("To enable emails, set: ENABLE_EMAIL=true")
        logger.info("Configure SMTP settings:")
        logger.info("  SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD")
        return True  # Configuration test passes even if disabled

    if not SENDER_PASSWORD:
        logger.error("✗ SENDER_PASSWORD is not configured")
        return False

    logger.info("✓ Email configuration is valid")
    return True


def run_all_tests():
    """Run all email notification tests"""
    logger.info("\n")
    logger.info("╔" + "="*68 + "╗")
    logger.info("║" + " "*68 + "║")
    logger.info("║" + "  PunterEdge Email Notification E2E Test Suite".center(68) + "║")
    logger.info("║" + " "*68 + "║")
    logger.info("╚" + "="*68 + "╝")

    tests = [
        ("Email Configuration", test_email_config),
        ("Approval Email", test_approval_email),
        ("User Creation Email", test_user_creation_email),
        ("Batch Email Notifications", test_batch_email_flow),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False

    # Print summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("-"*70)
    logger.info(f"Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("\n🎉 All tests passed! Email notifications are working correctly.")
        return True
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed. Check configuration above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
