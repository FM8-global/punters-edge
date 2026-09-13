#!/usr/bin/env python3
"""
Batch script to send welcome/notification emails to existing approved users.
This is useful for notifying users who were approved before email notifications were implemented.

Usage:
    python send_notifications_to_existing_users.py [--dry-run]

Options:
    --dry-run: Show what would be sent without actually sending emails
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_all_users
from email_service import send_approval_email, ENABLE_EMAIL
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def send_welcome_to_user(email: str, dry_run: bool = False) -> bool:
    """Send welcome notification to an existing approved user"""

    if not ENABLE_EMAIL:
        logger.warning(f"Email is disabled - cannot send to {email}")
        return False

    if dry_run:
        logger.info(f"[DRY-RUN] Would send welcome email to: {email}")
        return True

    try:
        # Send a generic welcome email (reuse approval email structure)
        logger.info(f"Sending welcome email to: {email}")
        return send_approval_email(email, "[Existing User - Please Set/Confirm Your Password]")
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {e}")
        return False


def main():
    """Main function to send batch emails"""

    dry_run = "--dry-run" in sys.argv

    if not ENABLE_EMAIL:
        logger.error("ERROR: Email notifications are not enabled!")
        logger.error("Set ENABLE_EMAIL=true and configure SMTP settings to enable emails.")
        sys.exit(1)

    logger.info("=" * 70)
    logger.info("PunterEdge - Batch Email Notification Script")
    logger.info("=" * 70)

    if dry_run:
        logger.info("Running in DRY-RUN mode - no emails will actually be sent")

    # Get all approved users
    logger.info("Fetching all approved users...")
    all_users = get_all_users()

    if not all_users:
        logger.info("No users found in system")
        sys.exit(0)

    approved_users = [u for u in all_users.values() if u.get('approved')]

    if not approved_users:
        logger.info("No approved users found")
        sys.exit(0)

    logger.info(f"Found {len(approved_users)} approved users")
    logger.info("-" * 70)

    sent_count = 0
    failed_count = 0

    for user in approved_users:
        email = user.get('email')
        if not email:
            logger.warning("Skipping user with no email")
            continue

        logger.info(f"Processing: {email}")

        if send_welcome_to_user(email, dry_run):
            sent_count += 1
        else:
            failed_count += 1

    logger.info("-" * 70)
    logger.info(f"Results: {sent_count} successful, {failed_count} failed")

    if dry_run:
        logger.info("DRY-RUN completed - no emails were actually sent")
    else:
        logger.info("Batch email notification complete!")

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
