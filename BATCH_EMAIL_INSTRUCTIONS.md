# Batch Email Notifications Script

This script allows you to send welcome/notification emails to all existing approved users in the system.

## Use Cases

- **Initial deployment**: Notify all users who were approved before email notifications were added
- **Re-engagement**: Send a notification to remind users about the app
- **Communication**: Keep users informed about the system

## Prerequisites

Email notifications must be enabled in your environment. Set these variables:

```bash
export ENABLE_EMAIL=true
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SENDER_EMAIL=your-email@example.com
export SENDER_PASSWORD=your-app-password
export SENDER_NAME="PunterEdge Admin"
```

## Running the Script

### 1. Dry Run (Recommended First Step)

Test what would be sent without actually sending emails:

```bash
cd backend
python scripts/send_notifications_to_existing_users.py --dry-run
```

Output will show:
- Number of approved users found
- Email addresses that would receive notifications
- Summary of what would be sent

### 2. Send Actual Emails

Once you've verified with dry-run, send the actual emails:

```bash
cd backend
python scripts/send_notifications_to_existing_users.py
```

The script will:
1. Fetch all approved users from the database
2. Send a welcome notification email to each user
3. Log success/failure for each email
4. Display a summary at the end

## Example Output

```
======================================================================
PunterEdge - Batch Email Notification Script
======================================================================
Fetching all approved users...
Found 5 approved users
----------------------------------------------------------------------
Processing: info@fm8.global
Sending welcome email to: info@fm8.global
Processing: peter@fm8.global
Sending welcome email to: peter@fm8.global
Processing: mick@fm8.global
Sending welcome email to: mick@fm8.global
Processing: leon@fm8.global
Sending welcome email to: leon@fm8.global
Processing: ben@fm8.global
Sending welcome email to: ben@fm8.global
----------------------------------------------------------------------
Results: 5 successful, 0 failed
Batch email notification complete!
======================================================================
```

## Troubleshooting

### "Email is disabled" Error

**Problem**: Script says email notifications are not enabled

**Solution**: Set the `ENABLE_EMAIL` environment variable:
```bash
export ENABLE_EMAIL=true
```

### SMTP Authentication Errors

**Problem**: Script fails with authentication error

**Solution**: Verify your SMTP credentials:
- For Gmail: Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password
- Check SMTP_SERVER and SMTP_PORT are correct for your email provider
- Verify SENDER_EMAIL matches the account being authenticated

### Some Emails Failed

**Problem**: Script shows some emails failed to send

**Solution**: 
- Check the error message in the log
- Verify email addresses are valid
- Try running again - may be temporary network issue
- Check SMTP server status

## Email Content

The notification email includes:
- Welcome message
- Information about the app
- Instructions to log in
- Security notes
- Support contact information

## Notes

- The script processes emails sequentially (not in parallel)
- Each email is logged with its result
- Failed emails don't stop the process - all other emails are still sent
- Always run with `--dry-run` first to verify before sending live emails
- The script is safe to run multiple times - duplicate emails won't break anything

## Running from Docker/Railway

If running in a containerized environment (like Railway), ensure environment variables are set in your deployment configuration:

**Railway:**
1. Go to your project
2. Select the service
3. Go to Variables
4. Add the email configuration variables
5. Redeploy or run the script after the variables take effect

## Schedule as Automated Task

To run this periodically (e.g., weekly reminder), you can set up a cron job:

```bash
# Send email notifications every Monday at 9am
0 9 * * 1 cd /app && python backend/scripts/send_notifications_to_existing_users.py
```

Or use a task scheduler service like:
- Unix/Linux: `crontab -e`
- Windows Task Scheduler
- Cloud services: AWS Lambda, Google Cloud Scheduler, Azure Functions

## Related Files

- `backend/email_service.py` - Email sending implementation
- `backend/auth.py` - User data retrieval
- `backend/main.py` - API endpoints for email notifications

## Questions?

For issues or questions about the script, check:
1. Email configuration (SMTP settings correct?)
2. User database has approved users
3. Email service is enabled (ENABLE_EMAIL=true)
4. Review the detailed log output for specific error messages
