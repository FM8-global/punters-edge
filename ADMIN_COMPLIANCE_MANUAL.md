# PunterEdge Admin Compliance Manual

**Version:** 1.0  
**Date:** 2026-09-09  
**Purpose:** Complete guide for administrators managing compliance requirements

⚠️ **CRITICAL DISCLAIMER**

This manual provides guidance on implemented compliance features. **It is NOT a substitute for legal advice.** Before deploying this application publicly:

- Consult with a qualified Australian gambling law attorney
- Verify compliance with all applicable state/territory regulations
- Implement any additional legal requirements not covered by this system
- Establish proper licensing where required

---

## Table of Contents

1. [Admin Dashboard Overview](#admin-dashboard-overview)
2. [User Management & Approval Workflow](#user-management--approval-workflow)
3. [Age Verification & KYC](#age-verification--kyc)
4. [Responsible Gambling Features](#responsible-gambling-features)
5. [Self-Exclusion Management](#self-exclusion-management)
6. [Compliance Monitoring & Reporting](#compliance-monitoring--reporting)
7. [Audit Trails & Data Protection](#audit-trails--data-protection)
8. [Emergency Procedures](#emergency-procedures)
9. [Compliance Checklist](#compliance-checklist)

---

## Admin Dashboard Overview

### Accessing Admin Dashboard

**Login Required:**
- Email: Your admin email (e.g., info@fm8.global)
- Password: Your secure admin password
- Access: http://localhost:8000 (local) or your deployed domain

### Main Tabs

| Tab | Purpose | Key Features |
|-----|---------|--------------|
| **Overview** | Dashboard summary | Races today, predictions, quick stats |
| **User Management** | User administration | Add users, approve requests, manage access |
| **Outcomes** | Performance analytics | Horse performance, user performance, reports |

### Required Admin Permissions

- User approval authority
- Compliance data access
- Audit trail viewing
- Report generation
- Settings management

---

## User Management & Approval Workflow

### New User Signup Flow

**Step 1: User Initiates Signup**
- User clicks "Request Access Here" on login page
- User enters email address
- User enters date of birth (for age verification)

**Step 2: Age Verification**
- System calculates user's age from DOB
- If age < 18: Request rejected immediately
- If age ≥ 18: Request approved and sent to pending queue
- Notification: "Age verified and access request submitted!"

**Step 3: Admin Reviews Pending Request**
- Admin logs in to dashboard
- Navigates to: User Management > Pending Access Requests
- Reviews applicant email and request date

**Step 4: Admin Approves or Rejects**
- **APPROVE:** User immediately gains access and can login
- **REJECT:** User is notified and can reapply

### Admin Manual User Addition

**To add a user without signup flow:**

1. Go to: Admin Dashboard > User Management
2. Enter email in "Add New User" field
3. Click "ADD USER"
4. User account is created and activated immediately
5. User can login without age verification (use with caution)

⚠️ **WARNING:** Manual user addition bypasses age verification. Only use for known-age users or testing.

---

## Age Verification & KYC

### Age Verification Requirements

**Australian Law:** All users must be 18+ to engage in gambling activities

**Implementation:**
- Client-side: User enters date of birth in signup form
- Server-side: System calculates age and validates (18+)
- Storage: Date of birth securely stored in `kyc_data` table
- Audit: Verification timestamp recorded

### Date of Birth Format

- **Format:** DD/MM/YYYY (displayed to user as calendar picker)
- **Validation:** Must be a valid calendar date
- **Age Check:** Current date minus DOB must be ≥ 18 years

### Viewing KYC Data

**Current Status:** Manual review required
- Access database directly or request developer report
- Fields: `email`, `date_of_birth`, `verified_age`, `verification_date`

**Recommended Admin Feature (To Be Added):**
```
Admin Dashboard > Compliance > KYC Data
- View all users' age verification status
- Export audit trail for regulatory review
- Flag suspicious entries
```

### Handling Age Verification Failures

**If user is under 18:**
- Signup automatically rejected
- User sees: "You must be 18 years or older"
- User can retry after birthday
- Attempt logged for audit trail

---

## Responsible Gambling Features

### Betting Limits

**Types of Limits Available:**

1. **Daily Limit** - Max amount per calendar day
2. **Weekly Limit** - Max amount per 7 days
3. **Monthly Limit** - Max amount per 30 days
4. **Session Duration** - Max minutes per login session

**Default Recommendations (AUD):**
- Daily: $500 (conservative)
- Weekly: $2,000
- Monthly: $5,000
- Session: 2-3 hours (120-180 minutes)

### Setting User Limits

**Current Status:** Backend-only implementation
- Limits stored in `responsible_gambling` table
- Requires database query or API call to set

**To Set Limits (Developer Assistance Required):**
```python
set_betting_limits(
    email="user@example.com",
    daily_limit=500.00,
    weekly_limit=2000.00,
    monthly_limit=5000.00,
    session_minutes=120
)
```

**Recommended Admin Interface (To Be Added):**
```
Admin Dashboard > User Management > [User Email] > Betting Limits
- Input fields for each limit type
- Save button to update limits
- View current limits per user
- Edit existing limits
```

### Monitoring Compliance

**Admin Should Monitor:**
- Users consistently hitting daily limits
- Users exceeding weekly/monthly limits
- Unusual betting patterns
- Users requesting limit increases frequently

**Action Steps:**
1. Review user's betting activity
2. Contact user if patterns are concerning
3. Suggest lower limits
4. Document all interventions

---

## Self-Exclusion Management

### What is Self-Exclusion?

**Legal Requirement:** Users must be able to voluntarily exclude themselves from gambling

**Duration:** Minimum 6 months, maximum 12 months (Australian standard)

**Effect:** Account is completely blocked; user cannot place any bets

### Self-Exclusion Process

**User-Initiated:**
1. User logs into account
2. Settings > Responsible Gambling
3. Click "Request Self-Exclusion"
4. Select duration (6-12 months)
5. Confirm request
6. Account immediately blocked

**Admin-Initiated (Protective):**
- Admin can force self-exclusion if user shows problem gambling
- Requires careful documentation
- Should be explained to user

### Viewing Self-Exclusion Status

**Current Status:** Backend-only
- Data in `self_exclusion_requests` table
- Status: 'active', 'expired', 'cancelled'

**Recommended Admin Dashboard Feature:**
```
Admin Dashboard > Compliance > Self-Exclusions
- List of active exclusions with end dates
- Archived/expired exclusions
- Option to manually extend or remove (with audit)
```

### Readmitting After Self-Exclusion

**Automatic:** After exclusion period expires, user can login and resume

**Early Readmission:** Not recommended, but requires:
1. Admin manual override
2. Audit log entry
3. Documentation of reason
4. Potential legal consultation

---

## Compliance Monitoring & Reporting

### Betting Activity Audit Trail

**What is Logged:**
- User email
- Bet amount
- Horse name and race details
- Odds and predicted odds
- Bet timestamp
- Outcome (win, place, loss)
- ROI calculation
- Payoff amount

**Access Current Logs:** Database query required

**Recommended Feature:**
```
Admin Dashboard > Compliance > Betting Activity
- Filter by user, date range, horse, outcome
- Export to CSV for regulatory reporting
- Flag suspicious patterns
```

### Compliance Alerts

**System Should Generate Alerts For:**
- First-time age verification failures
- Betting limit breaches
- Unusual win rates (potential fraud investigation)
- Account lockouts or security events
- Self-exclusion requests
- Multiple failed logins

**Current Status:** Alert framework in `compliance_alerts` table

**Recommended Admin Dashboard:**
```
Admin Dashboard > Compliance > Alerts
- Real-time notification center
- Filter by severity (info, warning, critical)
- Mark as reviewed/investigated
- Assign to admin user
```

### Monthly Compliance Report

**Should Include:**
1. **User Metrics**
   - New users approved
   - Age verifications completed
   - Users active during period
   - User retention rate

2. **Betting Metrics**
   - Total bets placed
   - Total winnings distributed
   - Average ROI per user
   - Most profitable horses

3. **Compliance Metrics**
   - Age verification failures
   - Betting limit breaches
   - Self-exclusions
   - Suspicious activity alerts

4. **Regulatory Data**
   - Complete audit trail export
   - KYC data summary
   - Self-exclusion status
   - Incident log

---

## Audit Trails & Data Protection

### What is Audited

**User Events:**
- Login/logout
- Signup approval/rejection
- Password changes
- Account settings changes
- Self-exclusion requests

**Betting Events:**
- Bet placement
- Bet outcome recording
- Limit breaches
- Unusual activity

**Admin Events:**
- User approvals
- Limit modifications
- Self-exclusion overrides
- Report generation
- Data exports

### Data Protection Measures

**Passwords:**
- SHA256 hashed (never stored plaintext)
- Salted hashing recommended (future improvement)
- Admin password: "admin123" (CHANGE IMMEDIATELY in production)

**Personal Data:**
- Date of birth: Encrypted at rest (when DB available)
- Email: Stored in plain (standard practice)
- Session tokens: Cryptographically random

**Access Control:**
- Admin-only routes require email header validation
- Sessions expire after 30 days of inactivity
- Database credentials stored in environment variables

### Development Mode Warning

**When DATABASE_URL not set:**
- System uses in-memory storage
- Data is NOT persisted
- Session data lost on server restart
- ⚠️ **FOR DEVELOPMENT ONLY**

**Production Setup:**
- PostgreSQL database REQUIRED
- Database encrypted at rest
- Regular backups
- Access logs

---

## Emergency Procedures

### Account Lockout (Suspected Fraud)

**If user account shows suspicious activity:**

1. **Immediate Action:** Disable user account
   - Remove from approved users list
   - Document reason and timestamp

2. **Investigation:**
   - Review betting history
   - Check for duplicate accounts
   - Verify all bets are valid

3. **Resolution:**
   - Contact user (if legitimate)
   - File suspicious activity report if needed
   - Restore account or close permanently

### Betting Limit Breach

**If user exceeds limits:**

1. **Alert Generated:** Check compliance dashboard
2. **Investigation:** Review last bets
3. **Contact User:** Explain limits, offer self-exclusion
4. **Escalate if Repeated:** May indicate problem gambling

### Data Breach Response

**If unauthorized access suspected:**

1. **Isolate System:** Stop accepting bets immediately
2. **Notify Users:** Email all affected users
3. **Reset Sessions:** Force logout all users
4. **Change Admin Password:** Update credentials
5. **Database Audit:** Review access logs
6. **Legal Consultation:** Consult attorney
7. **Regulatory Notification:** Notify relevant authorities if required

---

## Compliance Checklist

### Pre-Launch Checklist

- [ ] **Legal Review:** Attorney review of compliance features
- [ ] **Licensing:** Confirm required licensing obtained
- [ ] **AML/CTF:** Enhanced customer due diligence implemented
- [ ] **Age Verification:** System tested with various ages
- [ ] **Betting Limits:** Default limits set appropriately
- [ ] **Self-Exclusion:** Feature tested end-to-end
- [ ] **Data Protection:** Database encryption enabled
- [ ] **Audit Logging:** Verify all events logged
- [ ] **Admin Training:** All admins trained on procedures
- [ ] **Privacy Policy:** Website privacy policy current
- [ ] **Terms of Service:** Gambling terms clearly stated
- [ ] **Responsible Gambling:** Help links and resources visible
- [ ] **State Compliance:** Verified with all state requirements

### Monthly Compliance Tasks

- [ ] Review pending user approvals (minimum weekly)
- [ ] Monitor suspicious activity alerts
- [ ] Review betting limit breaches
- [ ] Check self-exclusion status
- [ ] Generate compliance report
- [ ] Audit user KYC data
- [ ] Verify database backups completed
- [ ] Review access logs
- [ ] Update responsible gambling resources
- [ ] Document any compliance incidents

### Quarterly Compliance Tasks

- [ ] Full audit trail export and review
- [ ] User activity analysis
- [ ] Regulatory requirement check (state-by-state)
- [ ] Security assessment
- [ ] Staff training refresher
- [ ] Update compliance procedures as needed
- [ ] Legal consultation on any new regulations

### Annual Compliance Tasks

- [ ] Comprehensive audit
- [ ] Third-party compliance review (recommended)
- [ ] Full legal review
- [ ] System penetration testing
- [ ] Policy updates and renewal
- [ ] Board/stakeholder reporting
- [ ] Plan for upcoming regulatory changes

---

## Contact & Support

### For Technical Issues
- Developer: [Technical contact]
- Issues: [Support email/system]

### For Compliance Questions
- Legal counsel: [Attorney contact]
- Regulatory authorities: [State-specific contacts]

### State Regulatory Contacts

| State | Authority | Website |
|-------|-----------|---------|
| NSW | Liquor & Gaming NSW | www.liquorandgaming.nsw.gov.au |
| VIC | VGCCC | www.vgccc.vic.gov.au |
| QLD | Office of Liquor & Gaming | www.olgr.qld.gov.au |
| WA | Department of Local Government | www.dlgsc.wa.gov.au |
| SA | Gambling Supervision Branch | www.sa.gov.au/gambling |
| TAS | Tasmanian Gambling Commission | www.gambleaware.asn.au |
| ACT | ACT Gambling & Racing | www.gambling.act.gov.au |
| NT | NT Racing Commission | www.nt.gov.au/racing |

---

## Appendix: System Limits & Features

### Current Implementation Status

✅ **Implemented:**
- Age verification (18+ check)
- KYC data storage (email, DOB)
- Session management (30-day tokens)
- Audit logging framework
- Betting activity tracking
- Self-exclusion requests
- Betting limit storage capability

🔄 **Recommended Additions:**
- Compliance dashboard in admin UI
- Real-time alert notifications
- Monthly/quarterly report generation
- Enhanced data encryption
- Anomaly detection for fraud
- Regular compliance testing framework

❌ **Out of Scope (Requires Legal Setup):**
- Licensing & registration
- AML/CTF customer due diligence
- Suspicious Activity Reporting (SAR)
- State-specific compliance rules
- Insurance requirements
- Responsible Gambling Council resources

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-09  
**Next Review:** 2026-12-09 (quarterly)

---

*This manual should be reviewed and updated quarterly to reflect regulatory changes and system improvements.*
