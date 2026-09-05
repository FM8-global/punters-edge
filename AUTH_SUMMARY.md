# Authentication System - What's Built

Complete email-based auth system with admin management. Ready to deploy live!

---

## Files Created

### 1. Backend Authentication Module
**File:** `backend/auth.py`

Handles:
- User approval tracking
- Session management (30-day tokens)
- Admin verification
- Email validation
- File-based storage (can upgrade to DB)

---

### 2. Updated API Server
**File:** `backend/main.py` (updated)

**New Auth Endpoints:**

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/` | GET | No | Login page (HTML) |
| `/login` | POST | No | Email login, get token |
| `/logout` | POST | Yes | Logout, invalidate token |
| `/admin/users` | GET | Admin | List approved users |
| `/admin/users/add` | POST | Admin | Approve new user |
| `/admin/users/remove` | POST | Admin | Remove user |

**Protected Endpoints (now require token):**

| Endpoint | Auth Header |
|----------|-------------|
| `/races` | `Authorization: Bearer [token]` |
| `/bets` | `Authorization: Bearer [token]` |
| `/bets/race/{id}` | `Authorization: Bearer [token]` |
| `/score/adjust-threshold` | Admin only |

---

### 3. Login Page
**File:** `backend/static/login.html`

Features:
- Beautiful gradient UI
- Email-only login (no password)
- Real-time validation
- Token display & copy button
- Usage instructions
- Responsive design

---

## How It Works

### User Flow

```
1. User visits https://app.com/
2. Sees login page
3. Enters email
4. Backend checks if approved
5. If approved: Session created, token returned
6. User copies token
7. User includes token in API requests:
   Authorization: Bearer [token]
8. API validates token, returns data
```

### Admin Flow

```
1. Admin (info@fm8.global) logs in
2. Gets token
3. Uses /admin/users endpoints to manage approvals
4. Can add/remove users
5. New users can then log in
```

---

## Default Setup

**Admin Email (by default):**
- `info@fm8.global`

**Session Duration:**
- 30 days

**Storage:**
- File-based (auto-created in `backend/data/`)
- `backend/data/users.json` — Approved user list
- `backend/data/sessions.json` — Active sessions

---

## Quick Start (Local Testing)

### 1. Start Backend
```bash
cd punter-edge/backend
python main.py
```

### 2. Open Login Page
Visit: http://localhost:8000/

### 3. Login as Admin
Email: `info@fm8.global`

### 4. Copy Token, Test API
```bash
# Get token from login page, then:
curl "http://localhost:8000/bets" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Deployment Steps (Summary)

1. **Choose hosting:**
   - Heroku (easiest, $7/month)
   - Railway (modern, $5/month)
   - Your own server

2. **Deploy code:**
   - Push to hosting platform
   - Set `API_KEY` environment variable

3. **Get live URL:**
   - From deployment platform
   - Example: `https://punter-edge-app.herokuapp.com`

4. **Test live:**
   - Visit URL
   - Login with `info@fm8.global`
   - Test API with token

5. **Add to Squarespace:**
   - Create card on fm8-apps page
   - Link to `https://your-url.com/`

---

## API Usage Examples

### Login
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# Response:
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "message": "Welcome user@example.com!"
}
```

### Get Predictions (with token)
```bash
curl "http://localhost:8000/bets?min_score=50" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# Response: [list of predictions with scores]
```

### Add Approved User (admin only)
```bash
curl -X POST "http://localhost:8000/admin/users/add" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com"}'

# Response:
{
  "message": "User newuser@example.com approved"
}
```

### List All Approved Users
```bash
curl "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Response:
{
  "approved_users": ["info@fm8.global", "user@example.com"]
}
```

---

## Security Features

✅ Token-based authentication (not cookie-based)
✅ 30-day expiring tokens
✅ Email validation
✅ Admin-only endpoints (protected)
✅ All API endpoints require auth (except login)
✅ Logout removes sessions

---

## Next: Deploy to Live

See `DEPLOYMENT.md` for:
- Heroku deployment (recommended)
- Railway alternative
- Your own server setup
- Squarespace integration

---

## Customization

### Change Admin Email

In `backend/auth.py` line 16:
```python
ADMIN_EMAIL = "your@email.com"
```

### Change Session Duration

In `backend/auth.py` line 97:
```python
"expires": (datetime.now() + timedelta(days=7)).isoformat()  # 7 days instead of 30
```

### Upgrade to Database

Replace file operations with PostgreSQL/MongoDB - document includes TODO notes.

---

## Testing Checklist

- [ ] Local login works
- [ ] Token generated correctly
- [ ] API requires Authorization header
- [ ] Admin endpoints restricted
- [ ] User management working
- [ ] Session expires after 30 days
- [ ] Deploy to Heroku/Railway
- [ ] Live login works
- [ ] Live API works with token
- [ ] Add to Squarespace
- [ ] Share link with approved users

---

**Status:** ✅ Authentication system complete and ready to deploy!

**Next:** Read DEPLOYMENT.md to deploy live with Squarespace integration.
