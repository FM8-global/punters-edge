# PunterEdge Australian Gambling Compliance Guide

⚠️ **CRITICAL DISCLAIMER:**

This compliance guide provides general features for Australian gambling regulations. **It is NOT a substitute for legal advice.** You MUST work with a qualified legal expert specializing in Australian gambling law before deploying this application publicly.

Compliance requirements vary by state, territory, and licensing status.

---

## Table of Contents

1. [Regulatory Framework](#regulatory-framework)
2. [Implemented Compliance Features](#implemented-compliance-features)
3. [Legal Requirements Checklist](#legal-requirements-checklist)
4. [Setup Instructions](#setup-instructions)
5. [Admin Compliance Dashboard](#admin-compliance-dashboard)
6. [User Compliance Settings](#user-compliance-settings)

---

## Regulatory Framework

### Federal Level

**Interactive Gambling Act 2001 (IGA)**
- Prohibits conduct of online gambling services without exemption
- Defines "interactive gambling" as gambling on Internet
- Exempts certain activities (sports betting, lotteries)

**Anti-Money Laundering/Counter-Terrorism Financing Act 2006 (AML/CTF)**
- Requires Know Your Customer (KYC) verification
- Suspicious Activity Reporting (SAR)
- Ongoing due diligence

**Telecommunications Act 1997**
- Internet content standards
- Privacy requirements

### State/Territory Level

Each state has its own gambling regulations:
- **NSW:** Liquor & Gaming NSW licensing
- **VIC:** Victorian Gambling and Casino Control Commission
- **QLD:** Office of Liquor and Gaming Regulation
- **WA:** Department of Local Government, Sport and Cultural Industries
- **SA:** Gambling Supervision Branch
- **TAS:** Tasmanian Gambling Commission
- **ACT:** ACT Gambling and Racing Commission
- **NT:** NT Racing Commission

---

## Implemented Compliance Features

### 1. Age Verification (18+)

**Required by:** All Australian states

**Implementation:**
```python
# User verifies age during initial signup
verify_age(email, date_of_birth)

# Check if user is age-verified before allowing betting
is_age_verified(email)
```

**Database:**
- `kyc_data.verified_age` - Boolean flag
- `kyc_data.date_of_birth` - Stored securely
- `kyc_data.verification_date` - Audit trail

**Admin Panel:**
- View age verification status
- Manually verify identities if needed

### 2. Responsible Gambling Features

**Daily/Weekly/Monthly Betting Limits**
```python
# Set betting limits for user
set_betting_limits(
    email,
    daily_limit=500.00,      # AUD
    weekly_limit=2000.00,    # AUD
    monthly_limit=5000.00,   # AUD
    session_minutes=120      # Max session duration
)

# Retrieve user's limits
limits = get_betting_limits(email)
```

**Self-Exclusion (6-12 months)**
```python
# User can request self-exclusion
request_self_exclusion(
    email,
    duration_days=180,  # Default 6 months
    reason="Personal reasons"
)

# Check if user is currently self-excluded
is_self_excluded(email)  # Returns True/False
```

**Database:**
- `responsible_gambling` table - Stores all limits and settings
- `self_exclusion_requests` table - Tracks exclusion periods
- Automatic expiry checking

### 3. Audit Trail & Compliance Logging

**Betting Activity Log**
```python
# Log all betting activity
log_betting_activity(
    email="user@example.com",
    action="bet_placed",
    amount=50.00,
    bet_details={"race_id": "123", "horse": "Black Beauty"},
    ip_address="192.168.1.1"
)
```

**Database:**
- `betting_activity_log` table - Immutable audit trail
- Timestamp on every action
- IP address tracking for fraud detection

**Compliance Alerts**
```python
# Create alerts for suspicious activity
create_compliance_alert(
    email="user@example.com",
    alert_type="high_bet_amount",
    description="User placed bet exceeding daily limit",
    severity="warning"
)
```

### 4. KYC/AML Framework

**Know Your Customer (KYC)**
- Age verification (18+)
- Identity verification option
- Contact information
- Source of funds declaration (if required by state)

**Database:**
- `kyc_data` table - Stores verification status
- `verified_age` - Age verification flag
- `verified_identity` - Identity verification flag
- Audit trail of all verifications

### 5. Compliance Reporting

**Admin Report:**
```python
# Generate compliance report for user
report = get_compliance_report(email)
# Returns: {
#   "email": "user@example.com",
#   "age_verified": true,
#   "identity_verified": false,
#   "betting_limits": {...},
#   "self_excluded": false
# }
```

---

## Legal Requirements Checklist

### Before Deployment

- [ ] **Licensing**: Confirm you have appropriate gambling license for your target state
- [ ] **Terms & Conditions**: Draft legal T&Cs with state-specific requirements
- [ ] **Privacy Policy**: Comply with Privacy Act 1988 (Cth)
- [ ] **AML/CTF Compliance**: Implement full KYC/SAR procedures
- [ ] **Problem Gambling**: Include links to support services
- [ ] **Responsible Gambling**: Display warnings on betting pages
- [ ] **Geolocation**: Implement state-based access controls
- [ ] **Financial Controls**: Set up segregated accounts for user funds
- [ ] **Audit Trail**: Ensure immutable logging of all bets
- [ ] **Dispute Resolution**: Establish user complaint handling process

### Ongoing Requirements

- [ ] **Compliance Monitoring**: Regular audits of betting activity
- [ ] **Suspicious Activity Reporting**: Report suspicious patterns to AUSTRAC
- [ ] **User Communication**: Annual compliance statements to users
- [ ] **Training**: Staff training on responsible gambling
- [ ] **Updates**: Track changes to state regulations

---

## Setup Instructions

### 1. Initialize Compliance Tables

The compliance tables are automatically created on app startup:
```python
# In main.py startup event
init_compliance_tables()
```

Tables created:
- `kyc_data` - Know Your Customer info
- `responsible_gambling` - User limits & settings
- `betting_activity_log` - Audit trail
- `self_exclusion_requests` - Self-exclusion tracking
- `compliance_alerts` - Alert tracking

### 2. Enable Age Verification on Signup

**In login.html:**
```javascript
// Add age verification form
function verifyAge(email, dateOfBirth) {
    fetch('/compliance/verify-age', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, date_of_birth: dateOfBirth})
    })
}
```

### 3. Display Responsible Gambling Message

**Required Text:**
```
Gambling can be addictive. If you need help, contact:
- National Problem Gambling Helpline: 1300 554 427
- Gamblers Anonymous: www.gamblersanonymous.org.au
- Lifeline: 13 11 14
```

### 4. Implement Betting Limits

**After each bet placement:**
```python
# Check if user has exceeded limits
limits = get_betting_limits(email)
if amount > limits['daily_limit']:
    # Block bet, show message
    return {"error": "Daily betting limit exceeded"}
```

### 5. Set Up Admin Compliance Dashboard

**Admin view includes:**
- Age verification status per user
- Active betting limits
- Self-exclusion list
- Compliance alerts
- Audit trail export

---

## Admin Compliance Dashboard

### Access Compliance Reports

**Admin can:**
1. View all users' compliance status
2. Manually verify identities
3. Set/modify betting limits
4. View self-exclusion list
5. Export audit trails
6. Create compliance alerts
7. Generate compliance reports

### Key Admin Endpoints

```
GET /admin/compliance/users
  - List all users with compliance status

GET /admin/compliance/report?email=user@example.com
  - Get detailed compliance report for user

POST /admin/compliance/alerts
  - Create compliance alert

GET /admin/compliance/audit-trail?email=user@example.com
  - Export betting activity log
```

---

## User Compliance Settings

### Age Verification

**When:** During first login or signup
**How:** User provides date of birth
**Storage:** Encrypted in `kyc_data` table
**Audit:** Verification timestamp recorded

### Betting Limits

**User can set:**
- Daily limit (e.g., $500)
- Weekly limit (e.g., $2,000)
- Monthly limit (e.g., $5,000)
- Session time limit (e.g., 2 hours)

**System enforces:**
- Blocks bets exceeding limits
- Shows warning at 80% of limit
- Notifies user when limit reached

### Self-Exclusion

**User can:**
- Request exclusion for 6, 12, or 24 months
- View exclusion end date
- Cannot modify account during exclusion
- Cannot place bets during exclusion

**Admin can:**
- Cancel exclusion early (with user consent)
- View all active exclusions
- Extend exclusion periods

---

## State-Specific Compliance

### NSW (Liquor & Gaming NSW)

- Must hold license from Liquor & Gaming NSW
- Responsible Gambling Code of Conduct
- Player Protection Standards
- Limits on free bets and inducements

### Victoria (VGCCC)

- Victorian Gambling and Casino Control Commission license required
- Harm Prevention Standards
- Advertising restrictions
- Interaction requirements

### Queensland (OLGR)

- Office of Liquor and Gaming Regulation license
- Wagering Code of Practice
- Bet limit and player protection requirements
- Community consultation

### Western Australia

- Department of Local Government, Sport and Cultural Industries license
- Racing and Wagering Regulations
- Responsible gambling standards
- Geolocation restrictions

### South Australia

- Gambling Supervision Branch license
- Horse Racing and Sports Betting Regulations
- Player protection obligations
- Audit and reporting requirements

### Tasmania

- Tasmanian Gambling Commission license
- Gambling (Sports Betting and Lotteries) Regulations
- Responsible gambling framework

### Australian Capital Territory

- ACT Gambling and Racing Commission license
- Gambling and Racing Regulations
- Community benefit obligations

### Northern Territory

- NT Racing Commission license
- Betting Control Board approval
- NT-specific player protection standards

---

## Responsible Gambling Resources

**Link on every betting page:**

- **National Problem Gambling Helpline**: 1300 554 427 (Free, confidential, 24/7)
- **Gamblers Anonymous**: www.gamblersanonymous.org.au
- **Lifeline**: 13 11 14
- **Beyond Blue**: 1300 224 636
- **Black Dog Institute**: www.blackdoginstitute.org.au
- **Problem Gambling Support Service**: www.problemgambling.gov.au

---

## Audit Trail Access

**All betting activity is logged:**
```
Email | Action | Amount | Timestamp | IP Address | Bet Details
user@... | bet_placed | 50.00 | 2024-09-07... | 192.168... | {race_id:...}
```

**Admin can:**
- Export audit trail (CSV/JSON)
- Filter by date range
- Filter by user email
- Search by action type
- Track suspicious patterns

---

## Compliance Checklist for Launch

### Before Public Launch

- [ ] Legal review completed by Australian gambling law specialist
- [ ] Appropriate state license obtained
- [ ] Age verification deployed and tested
- [ ] Responsible gambling features active
- [ ] All compliance databases created
- [ ] Admin dashboard operational
- [ ] Terms & Conditions published
- [ ] Privacy Policy compliant
- [ ] Problem gambling links displayed
- [ ] Audit logging tested
- [ ] AML/CTF procedures documented
- [ ] Staff training completed

### Ongoing (Monthly)

- [ ] Review compliance alerts
- [ ] Check self-exclusion list
- [ ] Export and review audit trails
- [ ] Monitor betting limits
- [ ] Verify age verification rate
- [ ] Check for suspicious patterns

### Ongoing (Quarterly)

- [ ] Generate compliance report
- [ ] Review state regulation updates
- [ ] Update responsible gambling resources
- [ ] Staff refresher training
- [ ] Audit trail archive

### Ongoing (Annually)

- [ ] Full compliance audit
- [ ] License renewal (if applicable)
- [ ] Regulatory updates review
- [ ] Independent review (if required)

---

## Support & Legal Consultation

**BEFORE DEPLOYING:** Contact a legal expert specializing in Australian gambling law.

**Recommended Consultation Topics:**
- Your specific state's licensing requirements
- AML/CTF compliance procedures
- Player protection obligations
- Advertising and inducement restrictions
- Dispute resolution procedures
- Compliance reporting requirements

---

**Last Updated:** September 2024
**Status:** General Framework (NOT LEGAL ADVICE)

⚠️ **This guide is for reference only. Consult qualified legal counsel before deployment.**
