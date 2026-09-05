# PythonAnywhere Setup for PunterEdge

Complete automated setup guide for deploying to PythonAnywhere with username: **fm8**

---

## Your Live URLs (After Setup)

| URL | Purpose |
|-----|---------|
| **https://fm8.pythonanywhere.com/** | Login page |
| **https://fm8.pythonanywhere.com/docs** | API documentation |
| **https://fm8.pythonanywhere.com/bets** | Get predictions |
| **https://fm8.pythonanywhere.com/admin/users** | Manage users (admin) |

---

## Step 1: Sign Up (2 minutes)

1. Go to https://www.pythonanywhere.com
2. Click "Start running Python online"
3. Sign up with:
   - Username: **fm8**
   - Email: your@email.com
   - Password: (secure)
4. Verify email
5. Login

---

## Step 2: Upload Code (2 minutes)

### Option A: Git (Recommended)

In PythonAnywhere **Bash Console**:
```bash
cd ~
git clone https://github.com/YOUR_GITHUB_USERNAME/punter-edge.git
cd punter-edge
```

### Option B: Manual Upload

1. Zip the `punter-edge` folder
2. In PythonAnywhere Files tab, upload ZIP
3. Extract it

---

## Step 3: Create Virtual Environment (2 minutes)

In PythonAnywhere **Bash Console**:

```bash
cd ~/punter-edge/backend
python3.10 -m venv punter-edge_venv
source punter-edge_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Wait for it to complete (2-3 minutes).

---

## Step 4: Create WSGI Configuration File (1 minute)

In PythonAnywhere, go to **Files** tab:

Create file: `/home/fm8/punter-edge/backend/wsgi.py`

Content:
```python
import sys
import os

path = '/home/fm8/punter-edge/backend'
if path not in sys.path:
    sys.path.append(path)

os.environ['API_KEY'] = 'c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec'

from main import app as application
```

Save it.

---

## Step 5: Create Web App (1 minute)

1. Click **Web** tab
2. Click **"Add a new web app"**
3. Select **Python 3.10** (or latest)
4. Click through to finish

---

## Step 6: Configure Web App (2 minutes)

1. In **Web** tab, click your app name
2. Scroll to **Code** section:
   - **Source code:** `/home/fm8/punter-edge`
   - **Working directory:** `/home/fm8/punter-edge/backend`

3. Scroll to **WSGI configuration file:**
   - Path: `/home/fm8/punter-edge/backend/wsgi.py`

4. Scroll to **Virtualenv:**
   - Path: `/home/fm8/punter-edge/backend/punter-edge_venv`

---

## Step 7: Add Environment Variables (1 minute)

1. In **Web** tab, scroll down to **Environment variables**
2. Add:
   - Key: `API_KEY`
   - Value: `c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec`
3. Click "Add"

---

## Step 8: Reload & Go Live (30 seconds)

1. Click green **Reload** button at top
2. Wait for "Reloaded at..." message
3. Done!

Your app is now live at: **https://fm8.pythonanywhere.com/**

---

## Step 9: Test It (1 minute)

1. Visit: https://fm8.pythonanywhere.com/
2. Should see login page
3. Login with: `info@fm8.global`
4. Should get auth token
5. Copy token and test API:
   ```
   https://fm8.pythonanywhere.com/bets
   (with Authorization: Bearer [token] header)
   ```

---

## Step 10: Add to Squarespace (2 minutes)

In your **fm8-apps** page, add this card:

```html
<div style="border: 2px solid #667eea; border-radius: 12px; padding: 24px; background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); margin: 20px 0;">
  <h3 style="color: #667eea; margin: 0 0 12px 0; font-size: 22px;">PunterEdge</h3>
  <p style="color: #555; font-size: 16px; margin: 0 0 16px 0; line-height: 1.6;">
    <strong>AI Horse Racing Betting Intelligence</strong><br>
    Real-time odds analysis across 14 Australian bookmakers with AI-powered predictions
  </p>
  
  <ul style="color: #666; font-size: 15px; margin: 0 0 20px 16px; padding-left: 20px;">
    <li>Live odds comparison</li>
    <li>AI scoring system (0-100)</li>
    <li>Daily predictions</li>
    <li>Email-based login</li>
  </ul>
  
  <a href="https://fm8.pythonanywhere.com/" 
     style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600;">
    Launch PunterEdge
  </a>
  
  <p style="color: #999; font-size: 13px; margin-top: 12px;">Approved users only. Contact info@fm8.global</p>
</div>
```

---

## Manage Users (Admin)

To add approved users:

```bash
# Get your admin token from the login page first, then:

curl -X POST "https://fm8.pythonanywhere.com/admin/users/add" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

---

## Troubleshooting

### "Module not found" error
- Ensure virtualenv path is correct in Web tab
- Run pip install again in bash console

### "Connection error"
- Check API_KEY environment variable is set
- Verify PuntersEdge API key is valid

### "403 Forbidden"
- Clear browser cache
- Try incognito/private window

### Still having issues?
- PythonAnywhere Support: help.pythonanywhere.com
- PuntersEdge API: puntersedge.online/developers

---

## Done!

Your live app is ready at: **https://fm8.pythonanywhere.com/**

**Total setup time: ~15 minutes**

Next: Share the link with approved users!
