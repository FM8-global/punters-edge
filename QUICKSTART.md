# PunterEdge Quick Start Guide

Get the MVP running in 5 minutes.

## Step 1: Get API Key (1 min)

Go to **https://puntersedge.online/api** and sign up for free tier:
- 1,500 credits/month
- No credit card needed
- Full access to Australian racing odds

Copy your API key.

## Step 2: Install Dependencies (2 min)

```bash
# Run setup script (creates venv, installs packages)
./setup.sh

# Or manually:
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..
```

## Step 3: Configure API Key (1 min)

```bash
# Edit backend/.env
nano backend/.env

# Add your key:
API_KEY=your_api_key_here
DEBUG=False
```

## Step 4: Run (1 min)

**Option A: Run all services**
```bash
./run.sh
```

**Option B: Run individually**

Backend:
```bash
cd backend
python main.py
# http://localhost:8000
```

CLI:
```bash
cd cli
python main.py today-bets --api-key YOUR_KEY
```

Frontend:
```bash
cd frontend
npm start
# http://localhost:3000
```

## What You'll See

### CLI Output
```
PunterEdge - Today's Best Bets

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓
┃ Race               ┃ Runner    ┃ Best Price┃ Overlay┃Score┃ Time  ┃ Notes      ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━╇━━━━━━━━╇━━━━━━━━━━━━┛
│ Temora R1         │ Chilling Edge │ $1.95   │ 8.2%  │ 62  │ 09:15 │ Good overlay
│ Leeton R2         │ Western Style │ $4.80   │ 12.5% │ 75  │ 09:45 │ Excellent overlay
└───────────────────┴───────────────┴─────────┴───────┴─────┴───────┴────────────┘

Total selections: 2
Average score: 68.5
```

### Web Dashboard
Visit **http://localhost:3000**:
- Live odds table
- Bet predictions with scores
- Filter by minimum score
- Overlay % highlighting
- Real-time refresh

### API Endpoints
Visit **http://localhost:8000/docs** for interactive API explorer:
- `GET /health` — Check if running
- `GET /races` — All upcoming races
- `GET /bets?min_score=50` — Today's predictions
- `POST /score/adjust-threshold` — Tune heuristics

## First Validation (Next 2 Weeks)

1. **Run daily:** `python cli/main.py today-bets --api-key YOUR_KEY`
2. **Log predictions:** Screenshot or export the bets
3. **Compare results:** Did the predicted winners actually win?
4. **Calculate edge:** ROI = (Wins × Avg Price) - Total Bets
5. **Adjust scoring:** Edit `backend/scoring.py` based on results

Example tracking sheet:
```
Date | Venue | Race | Runner    | Predicted Score | Best Price | Result | Actual Price
2024-01-15 | Temora | 1 | Chilling Edge | 62 | $1.95 | LOSS | -
```

## Troubleshooting

**API Error: Invalid API Key**
- Check `.env` has your key
- Verify key at https://puntersedge.online/login

**No races available**
- Races only show during racing hours
- Try mid-morning on a race day

**Port already in use**
- Backend (8000): `lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9`
- Frontend (3000): `lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9`

**Module not found errors**
- Activate venv: `source backend/venv/bin/activate` (Linux/Mac) or `backend\venv\Scripts\activate` (Windows)
- Reinstall: `pip install -r requirements.txt`

## Next: Validate Your Edge

See [README.md](README.md) for:
- How scoring works
- Customizing heuristics
- Adding new signals
- Building ML models

---

**Support:**
- PuntersEdge docs: https://puntersedge.online/developers
- Responsible gambling: 1800 858 858 (Australia)
