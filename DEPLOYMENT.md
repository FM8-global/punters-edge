# PunterEdge Deployment Guide

Complete guide to deploy PunterEdge live with authentication, then add to Squarespace fm8-apps page.

## Overview

Your app will have:
✅ Email-based login (only approved users can access)
✅ Admin panel to manage approved users
✅ Live API serving predictions
✅ Squarespace card linking to live app

---

## Phase 1: Update Local Code with Auth

Auth system is now built into your code! New features:

- **`/` (root)** — Login page
- **`/login`** — Email login endpoint
- **`/logout`** — Logout endpoint
- **`/admin/users`** — List approved users (admin only)
- **`/admin/users/add`** — Add approved user (admin only)
- **`/admin/users/remove`** — Remove approved user (admin only)
- All other endpoints now require `Authorization: Bearer [token]` header

### Test Locally First

```bash
cd punter-edge/backend
python main.py
```

Visit: http://localhost:8000

You'll see login page. Login with `info@fm8.global` (default admin).

---

## Phase 2: Deploy to Live Server

### Option A: Heroku (Easiest, Recommended for Squarespace)

**Cost:** $7-50/month

**Step 1: Create Heroku Account**
- Sign up at https://heroku.com

**Step 2: Create Procfile**

Create `punter-edge/Procfile`:
```
web: cd backend && python main.py
```

**Step 3: Create requirements.txt (if not done)**

Already in `punter-edge/backend/requirements.txt` ✓

**Step 4: Deploy via Git**

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create punter-edge-app-name

# Deploy
git push heroku main

# Set environment variable
heroku config:set API_KEY=your_puntersedge_key
```

**Step 5: Get Your Live URL**

```bash
heroku open
```

Will show: `https://punter-edge-app-name.herokuapp.com/`

---

### Option B: Railway (Modern Alternative)

**Cost:** $5/month

1. Connect GitHub repo at https://railway.app
2. Set environment variable: `API_KEY=your_key`
3. Deploy
4. Get URL from Railway dashboard

---

### Option C: Your Own Server

If you have a server with Python:

```bash
# On your server
cd /var/www/punter-edge
git clone your-repo .

# Install
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env with API key
echo "API_KEY=your_key" > .env

# Run with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# Use nginx as reverse proxy for SSL/https
```

---

## Phase 3: Test Live Deployment

### Test Login

Open: `https://your-deployed-app.com/`

Should see login page.

Email: `info@fm8.global`
Password: (none, just email verification)

Get token, then test API:

```bash
curl "https://your-deployed-app.com/bets" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Should return bet predictions.

---

## Phase 4: Manage Approved Users (Admin)

### Add New User

```bash
curl -X POST "https://your-deployed-app.com/admin/users/add" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

### List Approved Users

```bash
curl "https://your-deployed-app.com/admin/users" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Remove User

```bash
curl -X POST "https://your-deployed-app.com/admin/users/remove" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

---

## Phase 5: Add to Squarespace fm8-apps Page

### Step 1: Get Your Live URL

From Heroku/Railway: `https://your-app.herokuapp.com` or `https://your-app.railway.app`

### Step 2: Create App Card Content

**In Squarespace:**

1. Go to your `fm8-apps` page (or create new page)
2. Add a **Code Block** or **Embed** element
3. Paste this HTML:

```html
<div style="border: 2px solid #667eea; border-radius: 12px; padding: 20px; background: #f9f9f9; max-width: 300px;">
  <h3 style="color: #667eea; margin: 0 0 12px 0;">🏇 PunterEdge</h3>
  <p style="color: #666; font-size: 14px; margin: 0 0 16px 0;">
    AI Horse Racing Betting - Live odds analysis and predictions for Australian racing
  </p>
  <ul style="color: #666; font-size: 13px; margin: 0 0 16px 0; padding-left: 20px;">
    <li>Real-time odds comparison (14 bookmakers)</li>
    <li>AI scoring system (0-100)</li>
    <li>Daily betting predictions</li>
    <li>Email-based login</li>
  </ul>
  <a href="https://your-app.herokuapp.com/" target="_blank" 
     style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
             color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; 
             font-weight: 600; font-size: 14px;">
    Launch PunterEdge
  </a>
  <p style="color: #999; font-size: 11px; margin-top: 12px;">
    Approved users only. Contact info@fm8.global for access.
  </p>
</div>
```

**Replace:** `https://your-app.herokuapp.com/` with your actual URL

### Step 3: Style It (Optional)

For a nicer integration on Squarespace:

1. Create **Link Block** instead of Code Block
2. Add your app URL
3. Title: "PunterEdge - AI Horse Racing Betting"
4. Description: "Live odds analysis and predictions"
5. Add custom image (can generate at canva.com)

---

## Phase 6: Update Environment

### Set Admin Email

If you want different admin email (instead of info@fm8.global):

In `backend/auth.py`, line 16:
```python
ADMIN_EMAIL = "your_admin_email@domain.com"
```

### Configure Approved Users

**At launch, add users:**

```bash
# Admin login gets token
curl "https://your-app.com/" 
# (login as admin, copy token)

# Add user
curl -X POST "https://your-app.com/admin/users/add" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"approved@domain.com"}'
```

---

## Troubleshooting

### "Port 8000 already in use"
On Heroku/Railway, port is auto-assigned. On your server:
- Use `gunicorn` instead of `python main.py`
- Or change port in `main.py` line 108

### "API key not working"
- Check `heroku config` shows `API_KEY` set
- Verify key at https://puntersedge.online/login

### "Login page not loading"
- Check `backend/static/login.html` exists
- Restart server
- Clear browser cache

### "Approved users file getting large"
- Normal, can switch to database later
- File is `backend/data/users.json`

---

## Security Notes

✅ **What's secure:**
- Tokens expire after 30 days
- Admin-only endpoints protected
- Email validation on login
- Sessions stored locally

🔒 **Future improvements:**
- Move to database (PostgreSQL)
- HTTPS required (Heroku/Railway handle this)
- Refresh tokens
- Rate limiting
- Email verification

---

## Next Steps

1. **Deploy:** Choose Heroku/Railway/Own Server
2. **Test:** Login and use API
3. **Add Users:** Use admin panel
4. **Add to Squarespace:** Copy card HTML
5. **Monitor:** Check logs for errors

---

## Support

**For Heroku issues:** https://devcenter.heroku.com/
**For API issues:** https://puntersedge.online/developers
**For FM8 questions:** info@fm8.global

---

**Your app will be live at:**
`https://[your-deployment].com/`

**Admin panel at:**
`https://[your-deployment].com/admin/users` (with token)

**API docs at:**
`https://[your-deployment].com/docs`
