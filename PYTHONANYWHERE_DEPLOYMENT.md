# PythonAnywhere Deployment Guide - PunterEdge

## Quick Reference
- **🚀 Live App:** https://fm8global.pythonanywhere.com/
- **🔑 Admin Login:** info@fm8.global / admin123
- **📚 Quick Start:** [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)
- **📖 API Docs:** https://fm8global.pythonanywhere.com/docs
- **✅ Status:** Deployed & Fully Operational

---

## Pre-Deployment Checklist

- [ ] Have PythonAnywhere account created
- [ ] Email verified on PythonAnywhere
- [ ] Know your PythonAnywhere username
- [ ] GitHub account (for cloning code)

---

## Deployment Steps (Copy & Paste)

### Step 1: Clone Code (Bash Console)
```bash
cd ~
git clone https://github.com/YOUR_GITHUB_USERNAME/punter-edge.git
cd punter-edge/backend
```

### Step 2: Create Virtual Environment (Bash Console)
```bash
python3.10 -m venv punter-edge_venv
source punter-edge_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Create Web App
1. Click **Web** tab
2. Click **Add a new web app**
3. Choose **Python 3.10**
4. Keep defaults and complete

### Step 4: Configure Web App
Edit your web app config:

**Source code:** 
```
/home/YOUR_USERNAME/punter-edge
```

**Working directory:**
```
/home/YOUR_USERNAME/punter-edge/backend
```

**Virtualenv:**
```
/home/YOUR_USERNAME/punter-edge/backend/punter-edge_venv
```

### Step 5: Update WSGI File
In the **WSGI configuration file** section, click to edit and paste:

```python
import sys
import os

path = '/home/YOUR_USERNAME/punter-edge/backend'
if path not in sys.path:
    sys.path.append(path)

os.environ['API_KEY'] = 'c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec'

from main import app as application
```

### Step 6: Add Environment Variable
Scroll to **Environment variables** section:
- Click **Add a new variable**
- **Name:** `API_KEY`
- **Value:** `c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec`

### Step 7: Reload App
- Click green **Reload** button
- Wait for "Reloaded at..." message (about 5-10 seconds)

---

## Testing Deployment

### Test 1: Access Login Page
Visit: `https://YOUR_USERNAME.pythonanywhere.com/`
- Should see login form
- Should see "PunterEdge" title

### Test 2: Admin Login
```
Email: info@fm8.global
Password: (your admin password)
```
- Should redirect to dashboard
- Should see "Approved Users", "Pending Requests", etc.

### Test 3: API Access
Visit: `https://YOUR_USERNAME.pythonanywhere.com/docs`
- Should see interactive API documentation
- Try GET `/bets` (should work if logged in or with token)

---

## Troubleshooting

### Error: "No module named 'main'"
- ✅ Check working directory is `/home/YOUR_USERNAME/punter-edge/backend`
- ✅ Make sure virtualenv path is set correctly
- ✅ Click Reload again

### Error: "ModuleNotFoundError"
- ✅ Check virtualenv is set to: `/home/YOUR_USERNAME/punter-edge/backend/punter-edge_venv`
- ✅ In Bash: `source punter-edge_venv/bin/activate && pip install -r requirements.txt`

### App shows blank page
- ✅ Check **Source code** is `/home/YOUR_USERNAME/punter-edge`
- ✅ Check **Working directory** is `/home/YOUR_USERNAME/punter-edge/backend`
- ✅ Click Reload

### Can't login
- ✅ Make sure you have `API_KEY` environment variable set
- ✅ Check admin user exists: `info@fm8.global`
- ✅ Check password is correct

---

## After Successful Deployment

### Share the App
- Share link: `https://YOUR_USERNAME.pythonanywhere.com/`
- Admin panel: `https://YOUR_USERNAME.pythonanywhere.com/admin` (after login)
- API docs: `https://YOUR_USERNAME.pythonanywhere.com/docs`

### Add Users
1. Login as admin (info@fm8.global)
2. Click "Admin Panel"
3. Click "Add New User"
4. Enter email and optional password
5. Users can now login

### Monitor App
- Check **Web** tab in PythonAnywhere dashboard
- Click on your app name to see logs
- Logs show errors and activity

---

## Support

**PythonAnywhere Help:** help.pythonanywhere.com  
**App Issues:** Check Web tab → "Error log" for debugging  
**Code Changes:** Push to GitHub, then in PythonAnywhere bash: `cd ~/punter-edge && git pull origin main`

---

## Deployment Status

✅ Code ready for deployment  
✅ All tests passing  
✅ Database configured  
✅ API keys configured  

**Ready to launch!** 🚀
