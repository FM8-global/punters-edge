# PunterEdge Installation Guide

Complete step-by-step installation for Windows, Mac, and Linux.

## Prerequisites

- **Python 3.10+** - Download from https://www.python.org/
- **Git** (optional) - For version control
- **PuntersEdge API Key** (free) - https://puntersedge.online/api

## Step 1: Get Your Free API Key

1. Visit https://puntersedge.online/api
2. Click "Get a free API key"
3. Sign up with your email (no credit card needed)
4. Copy your API key - you'll need it in Step 3

Free tier includes:
- 1,500 credits/month
- Full access to 14 Australian bookmakers
- All racing categories (horse, greyhound, harness)

---

## Step 2: Download & Extract PunterEdge

### Option A: Clone from GitHub (if using git)
```bash
git clone https://github.com/yourusername/punter-edge.git
cd punter-edge
```

### Option B: Manual Download
1. Download the punter-edge folder
2. Open terminal/PowerShell in that folder
3. Continue to Step 3

---

## Step 3: Install Python Dependencies

### Windows (PowerShell)
```powershell
cd punter-edge/backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

### Mac/Linux (Terminal)
```bash
cd punter-edge/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

**What this does:**
- Creates isolated Python environment (venv)
- Installs FastAPI, Pydantic, httpx, etc.
- Takes 2-3 minutes

---

## Step 4: Configure API Key

### Windows
```powershell
cd punter-edge/backend
notepad .env
```

### Mac/Linux
```bash
cd punter-edge/backend
nano .env
```

**Add this line:**
```
API_KEY=your_api_key_here
DEBUG=False
```

Replace `your_api_key_here` with the key from Step 1.

**Save and close** (Ctrl+S in nano, Ctrl+X to exit)

---

## Step 5: Verify Installation

### Test API Connection
```bash
# Windows
cd punter-edge
python test_api_key.py

# Mac/Linux
cd punter-edge
python3 test_api_key.py
```

**Expected output:**
```
Testing PuntersEdge API Key

API Key: c9edb4f8...e0ec
[OK] API Connection Successful!

Found 3 races:
  Venue: Gosford
  Race: #3
  ...

[SUCCESS] Your API key is valid and working!
```

If you see `[SUCCESS]`, you're ready! If not, check:
- API key is copied correctly
- `.env` file is in `punter-edge/backend/`
- You have internet connection

---

## Step 6: Start the Backend

### Windows (PowerShell)
```powershell
cd punter-edge/backend
.\venv\Scripts\Activate.ps1
python main.py
```

### Mac/Linux (Terminal)
```bash
cd punter-edge/backend
source venv/bin/activate
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Leave this running - it's your API server.

---

## Step 7: Test the Backend (New Terminal)

### Windows (PowerShell - New Window)
```powershell
# Test health check
Invoke-WebRequest http://localhost:8000/health
```

### Mac/Linux (New Terminal)
```bash
# Test health check
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"ok"}
```

---

## Step 8: Run CLI Tool (Optional - New Terminal)

### Windows (PowerShell - New Window)
```powershell
cd punter-edge/cli
python main.py today-bets --api-key your_api_key_here
```

### Mac/Linux (New Terminal)
```bash
cd punter-edge/cli
python3 main.py today-bets --api-key your_api_key_here
```

**Expected output:**
```
PunterEdge - Today's Best Bets

┏━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━┓
┃ Race      ┃ Runner  ┃ Price  ┃ Overlay┃Score┃
┡━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━┩
│ Leeton R5 │ #7 Bet  │ $41.00 │ 14.3%  │ 65  │
│ Leeton R5 │ #3 Lam  │ $31.00 │ 28.4%  │ 65  │
└───────────┴─────────┴────────┴────────┴─────┘

Total selections: 2
Average score: 65
```

---

## Step 9: Access Web API (Optional)

Visit: http://localhost:8000/docs

You'll see interactive API documentation where you can:
- View all endpoints
- Test endpoints with a "Try It Out" button
- See response formats
- Adjust parameters

---

## Installation Complete! ✅

### What's Running:

| Service | URL | Access |
|---------|-----|--------|
| **Backend API** | http://localhost:8000 | JSON endpoints |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **Health Check** | http://localhost:8000/health | {status: ok} |
| **CLI Tool** | Terminal | `python main.py today-bets` |

**Copy these links to your browser:**
- **Swagger API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

### Next Steps:
1. Read [USER_MANUAL.md](USER_MANUAL.md) to start using the app
2. Run daily predictions with CLI
3. Log results and validate your edge
4. Adjust scoring rules based on wins/losses

---

## Troubleshooting

### "Python not found"
- Make sure Python 3.10+ is installed
- Check: `python --version` or `python3 --version`
- On Mac, may need to use `python3` instead of `python`

### "Module not found" errors
- Activate venv first: `source venv/bin/activate` (Mac/Linux) or `.\venv\Scripts\Activate.ps1` (Windows)
- Reinstall requirements: `pip install -r requirements.txt`

### "Port 8000 already in use"
- Another app is using port 8000
- Find and close it, or edit `main.py` line 95 to use different port

### "API key invalid"
- Double-check key in `.env` (no extra spaces)
- Run `python test_api_key.py` to verify
- Get new key at https://puntersedge.online/api

### "No races available"
- Check if it's racing hours in Australia (9am-5pm AEST on race days)
- Try again during race hours

### Still stuck?
See the FAQ section in [USER_MANUAL.md](USER_MANUAL.md)

---

**Questions?** See USER_MANUAL.md for detailed usage guide.
