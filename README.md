# PunterEdge: AI Horse Racing Betting App

Australian racing punter app with AI scoring powered by PuntersEdge odds API.

**Status:** MVP Phase 1 - Manual Heuristics + Live Odds Integration

---

## 🚀 Quick Access (After Starting Backend)

**Backend running? Access the app here:**

| Interface | URL | Use For |
|-----------|-----|---------|
| **Interactive Docs** | http://localhost:8000/docs | Test API endpoints |
| **Get Today's Bets** | http://localhost:8000/bets?min_score=50 | View predictions |
| **CLI Tool** | Terminal: `python cli/main.py today-bets --api-key YOUR_KEY` | Daily reports |
| **Health Check** | http://localhost:8000/health | Verify server running |

👉 **Start here:** http://localhost:8000/docs

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- PuntersEdge free API key (https://puntersedge.online/api)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env and add your API key
```

**Run API server:**
```bash
python main.py
# Or: uvicorn main:app --reload
```

Server runs on `http://localhost:8000`

**API Endpoints:**
- `GET /health` — Health check
- `GET /races` — All upcoming races
- `GET /bets?min_score=50` — Bet predictions filtered by score
- `GET /bets/race/{race_id}` — Predictions for specific race
- `POST /score/adjust-threshold` — Tweak scoring parameters

### 2. CLI Tool

```bash
cd cli
python main.py today-bets --api-key YOUR_KEY

# Or with minimum score filter
python main.py today-bets --api-key YOUR_KEY --min-score 60

# List all races
python main.py list-races --api-key YOUR_KEY
```

### 3. Dashboard (Frontend)

```bash
cd frontend
npm install
npm start
```

Runs on `http://localhost:3000`

## Architecture

```
punter-edge/
├── backend/
│   ├── api_client.py      — PuntersEdge API wrapper
│   ├── models.py          — Pydantic data models
│   ├── scoring.py         — Betting heuristics engine
│   ├── main.py            — FastAPI server
│   └── requirements.txt
├── cli/
│   └── main.py            — Typer CLI tool
├── frontend/
│   ├── src/
│   │   └── Dashboard.jsx  — React dashboard
│   └── package.json
└── data/                  — (for future: bet logs, training data)
```

## How It Works

### Phase 1: Manual Heuristics (Current)

Scoring engine evaluates each runner based on:

1. **Overlay %** — How far best price sits above market average
   - 20%+ overlay → 40 points
   - 10-20% → 30 points
   - 5-10% → 20 points

2. **Odds Range** — "Sweet spot" odds typically 2.0-8.0
   - 2.0-8.0 → 20 points
   - 1.5-2.0 → 10 points (favourites)
   - 8.0-15.0 → 15 points

3. **Bookmaker Liquidity** — More books = more reliable
   - 10+ bookmakers → 20 points
   - 8-9 → 15 points
   - 5-7 → 10 points

4. **Race Conditions** (when data available)
   - Horse racing: light weight (+5 pts)
   - Any category: barrier 1-2 (+10 pts)

**Final Score:** 0-100 scale (default min bet: 50 score)

### Phase 2: Machine Learning (Next)

Once you validate manual edge:
- Collect historical data (races, predictions, results)
- Train model (XGBoost) on proven signals
- Deploy as optional scoring layer
- A/B test manual vs ML predictions

## Customization

### Adjust Scoring Thresholds

Edit `backend/scoring.py`:

```python
self.min_overlay_pct = 5.0    # Minimum overlay %
self.min_odds = 1.5           # Minimum odds to consider
self.max_odds = 50.0          # Maximum odds
```

Or via API:
```bash
curl -X POST http://localhost:8000/score/adjust-threshold \
  -H "Content-Type: application/json" \
  -d '{"min_overlay": 7.0, "min_odds": 2.0}'
```

### Add New Scoring Rules

In `BetScorer._calculate_score()`, add logic for:
- Trainer form
- Jockey statistics
- Track conditions
- Weight trends
- Form curves

Example:
```python
if runner.trainer_wins_recent > 50:  # High win rate last 10 races
    score += 15
```

## Data Collection (For Future Training)

To build ML model, log your bets:

```python
# Save to CSV/database
{
    "race_id": "...",
    "runner_id": "...",
    "predicted_score": 75,
    "best_price": 4.2,
    "overlay_pct": 12.5,
    "result": "WIN",  # WIN/PLACE/LOSE
    "actual_price": 4.2,
    "odds_when_placed": 4.2,
}
```

Use this data to:
- Validate scoring accuracy
- Backtest against historical races
- Train ML models
- Calculate ROI by score threshold

## Next Steps

1. **Get API Key** → Free tier at https://puntersedge.online/api
2. **Run Backend** → `python backend/main.py`
3. **Test CLI** → `python cli/main.py today-bets --api-key YOUR_KEY`
4. **Validate Edge** → Check predictions vs actual results for 2-4 weeks
5. **Tune Heuristics** → Adjust scoring based on validation
6. **Add ML** → Once confident in manual edge

## Responsible Gambling

This tool is for **analysis only**. Always:
- Bet only what you can afford to lose
- Track ROI and expected value
- Never chase losses
- Use betting limits

Help: 1800 858 858 (Australia)

---

**Built with:** FastAPI · React · PuntersEdge API  
**License:** MIT
