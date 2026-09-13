"""Email service for PunterEdge notifications"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@puntersedge.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "PunterEdge Admin")
ENABLE_EMAIL = os.getenv("ENABLE_EMAIL", "false").lower() == "true"


def send_approval_email(user_email: str, temp_password: str) -> bool:
    """Send approval email with temporary password to user"""
    if not ENABLE_EMAIL:
        logger.info(f"Email disabled - would send approval to {user_email}")
        return True

    if not SENDER_PASSWORD:
        logger.warning("Email enabled but SENDER_PASSWORD not configured")
        return False

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "PunterEdge Access Approved - Set Your Password"
        msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg["To"] = user_email

        # Plain text version
        text_content = f"""Welcome to PunterEdge!

Your access has been approved. You can now log in using:

Email: {user_email}
Temporary Password: {temp_password}

IMPORTANT SECURITY NOTE:
1. Log in with the email and temporary password above
2. On your first login, you will be prompted to change your password
3. Please set a strong, unique password immediately
4. Never share your password with anyone

If you have any issues logging in, contact the admin at info@fm8.global

Best regards,
PunterEdge Admin Team
"""

        # HTML version
        html_content = f"""<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #667eea;">Welcome to PunterEdge! 🎉</h2>

        <p>Your access has been approved. You can now log in using:</p>

        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Email:</strong> {user_email}</p>
            <p><strong>Temporary Password:</strong> <code style="background: #e0e0e0; padding: 5px; border-radius: 3px;">{temp_password}</code></p>
        </div>

        <h3 style="color: #d97706;">⚠️ IMPORTANT SECURITY NOTE:</h3>
        <ol>
            <li>Log in with the email and temporary password above</li>
            <li>On your first login, you will be prompted to change your password</li>
            <li>Please set a strong, unique password immediately</li>
            <li>Never share your password with anyone</li>
        </ol>

        <p>If you have any issues logging in, contact the admin at <strong>info@fm8.global</strong></p>

        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="color: #999; font-size: 12px;">
            Best regards,<br>
            PunterEdge Admin Team
        </p>
    </div>
</body>
</html>
"""

        # Attach both versions
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        logger.info(f"Approval email sent successfully to {user_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send approval email to {user_email}: {e}")
        return False


def send_user_created_email(user_email: str, password: str, created_by: str) -> bool:
    """Send email to user when manually created by admin"""
    if not ENABLE_EMAIL:
        logger.info(f"Email disabled - would send creation email to {user_email}")
        return True

    if not SENDER_PASSWORD:
        logger.warning("Email enabled but SENDER_PASSWORD not configured")
        return False

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your PunterEdge Account Has Been Created"
        msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg["To"] = user_email

        # Plain text version
        text_content = f"""Hello,

Your PunterEdge account has been created by {created_by}.

Login Credentials:
Email: {user_email}
Password: {password}

To get started:
1. Visit https://punters-edge-production.up.railway.app
2. Log in with your email and password
3. You can change your password at any time in your account settings

If you have any questions, contact the admin at info@fm8.global

Best regards,
PunterEdge Team
"""

        # HTML version
        html_content = f"""<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #667eea;">Your PunterEdge Account is Ready! 🚀</h2>

        <p>Your PunterEdge account has been created by <strong>{created_by}</strong>.</p>

        <h3 style="color: #667eea;">Login Credentials:</h3>
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Email:</strong> {user_email}</p>
            <p><strong>Password:</strong> <code style="background: #e0e0e0; padding: 5px; border-radius: 3px;">{password}</code></p>
        </div>

        <h3 style="color: #667eea;">Getting Started:</h3>
        <ol>
            <li>Visit <a href="https://punters-edge-production.up.railway.app" style="color: #667eea;">PunterEdge</a></li>
            <li>Log in with your email and password</li>
            <li>You can change your password anytime in your account settings</li>
        </ol>

        <p>If you have any questions, contact the admin at <strong>info@fm8.global</strong></p>

        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="color: #999; font-size: 12px;">
            Best regards,<br>
            PunterEdge Team
        </p>
    </div>
</body>
</html>
"""

        # Attach both versions
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        logger.info(f"User creation email sent successfully to {user_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send creation email to {user_email}: {e}")
        return False
