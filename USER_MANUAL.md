# PunterEdge User Manual

Complete guide to using the AI horse racing betting app.

---

## Quick Links (When Backend is Running)

| Feature | Link |
|---------|------|
| **Interactive API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |
| **Get Bets** | http://localhost:8000/bets?min_score=50 |
| **Get Races** | http://localhost:8000/races |

**👉 Start here:** http://localhost:8000/docs

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Using the CLI Tool](#using-the-cli-tool)
3. [Using the Web API](#using-the-web-api)
4. [Understanding Scores](#understanding-scores)
5. [Validating Your Edge](#validating-your-edge)
6. [Customizing Scores](#customizing-scores)
7. [FAQ](#faq)

---

## Getting Started

### Prerequisites
- Backend running: `python main.py` (in `punter-edge/backend/`)
- API key configured in `.env`
- Python activated: `source venv/bin/activate`

### Architecture

```
You (User)
    ↓
CLI Tool OR Web Browser
    ↓
FastAPI Backend (http://localhost:8000)
    ↓
PuntersEdge API (14 Australian bookmakers)
    ↓
Live Race Data & Odds
```

---

## Using the CLI Tool

### 1. Show Today's Best Bets

```bash
cd punter-edge/cli
python main.py today-bets --api-key your_api_key_here
```

**Output:**
```
PunterEdge - Today's Best Bets
Minimum score threshold: 50

Race          Runner              Best Price  Overlay %  Score  Start Time  Notes
Leeton R5     #7 Bettorbythesea  $41.00      14.3%      65     09:45       Good overlay | Sweet spot odds range
Leeton R5     #3 Lamna Nasus     $31.00      28.4%      65     09:45       Excellent overlay | Sweet spot odds range
Gosford R3    #1 She's All Heart $4.60       5.5%       50     10:15       Moderate overlay | Favourite...

Total selections: 3
Average score: 60.0
```

### 2. Adjust Minimum Score

```bash
# Only show bets scoring 60+
python main.py today-bets --api-key your_key --min-score 60

# Only show high-confidence bets (75+)
python main.py today-bets --api-key your_key --min-score 75
```

Higher threshold = fewer bets, but higher quality

### 3. List All Upcoming Races (No Scoring)

```bash
python main.py list-races --api-key your_api_key_here
```

**Output:**
```
Upcoming Races

Venue               Race #  Category   Start Time  Runners
Leeton              5       harness    09:45       8
Gosford             3       greyhound  10:15       9
Kanazawa            9       horse      11:00       8
```

---

## Using the Web API

### 1. Access Interactive API Docs

Visit: **http://localhost:8000/docs**

You'll see:
- List of all endpoints
- Click "Try it out" to test each one
- See response data formatted nicely

### 2. Endpoints Overview

#### GET /health
Check if backend is running
```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

#### GET /races
Get all upcoming races
```bash
curl http://localhost:8000/races
# Returns: [list of races]
```

#### GET /bets
Get AI predictions filtered by score
```bash
# Default (min_score=50)
curl "http://localhost:8000/bets"

# Only show 60+ scores
curl "http://localhost:8000/bets?min_score=60"

# Only show 75+ scores
curl "http://localhost:8000/bets?min_score=75"
```

**Response example:**
```json
[
  {
    "race_id": "9c8a82a8-81f0-43d1-9fc1-2270b70ddccb",
    "race_venue": "Leeton",
    "race_number": 5,
    "runner_name": "Bettorbythesea",
    "runner_number": 7,
    "best_price": 41.0,
    "avg_price": 35.87,
    "overlay_pct": 14.3,
    "score": 65.0,
    "reasoning": "Good overlay: 14.3% | Sweet spot odds range",
    "category": "harness",
    "start_time": "2026-09-01T09:45:00Z"
  }
]
```

#### GET /bets/race/{race_id}
Get predictions for specific race
```bash
curl "http://localhost:8000/bets/race/9c8a82a8-81f0-43d1-9fc1-2270b70ddccb?min_score=40"
```

#### POST /score/adjust-threshold
Adjust scoring parameters (temporary)
```bash
curl -X POST "http://localhost:8000/score/adjust-threshold" \
  -H "Content-Type: application/json" \
  -d '{"min_overlay": 7.0, "min_odds": 2.0}'
```

---

## Understanding Scores

### Score Calculation (0-100)

Your predictions are scored based on **4 factors**:

#### 1. Overlay % (20-40 points)
**What it is:** How much better the best price vs market average
- 20%+ overlay → 40 points ✅ Excellent
- 10-20% overlay → 30 points ✅ Good
- 5-10% overlay → 20 points ✅ Moderate
- <5% overlay → 0 points ❌ No edge

**Example:**
- Best price: $5.00
- Market average: $4.35
- Overlay: ($5.00 - $4.35) / $4.35 × 100 = 14.9%
- Points: 30

#### 2. Odds Range (10-20 points)
**Sweet spot:** $2.00 - $8.00
- $2.00-$8.00 → 20 points ✅ Sweet spot
- $1.50-$2.00 → 10 points (Favourites)
- $8.00-$15.00 → 15 points
- $15.00+ → 5 points (Long shots)

**Why?** Betting sweet spot has historically better ROI

#### 3. Bookmaker Liquidity (10-20 points)
**More bookmakers = more reliable odds**
- 10+ bookmakers → 20 points ✅ Excellent liquidity
- 8-9 bookmakers → 15 points
- 5-7 bookmakers → 10 points
- <5 bookmakers → 0 points

**Why?** Widely available prices are less likely to be mispriced

#### 4. Race Conditions (0-10 points)
- Barrier 1-2 (horse racing) → +10 points
- Light weight ≤53kg (horse racing) → +5 points

**Why?** Position/weight advantages matter in racing

### Total Score

```
Score = Overlay (0-40) + Odds (0-20) + Liquidity (0-20) + Conditions (0-10)
Range: 0-100
```

### What Score Means

| Score | Confidence | Action |
|-------|-----------|--------|
| 75+ | Very High | **Bet with confidence** |
| 60-74 | High | Bet, but smaller stake |
| 50-59 | Moderate | Consider betting |
| 40-49 | Low | Risky - skip or small bet |
| <40 | Very Low | **Don't bet** |

---

## Validating Your Edge

### Phase 1: Prove Your Edge (2-4 weeks)

This is CRITICAL before betting real money.

#### Step 1: Set Up Tracking Spreadsheet

Create a file (Excel/Google Sheets) with columns:

| Date | Venue | Race | Runner | Score | Best Price | Odds @ Bet | Result | Actual Price | ROI |
|------|-------|------|--------|-------|------------|-----------|--------|--------------|-----|
| 2026-09-01 | Leeton | 5 | Bettorbythesea | 65 | $41 | $41 | LOSS | - | -$41 |
| 2026-09-01 | Leeton | 5 | Lamna Nasus | 65 | $31 | $31 | WIN | $31 | +$31 |

#### Step 2: Run Daily Predictions

Each morning during racing season:
```bash
python main.py today-bets --api-key your_key > bets_$(date +%Y%m%d).txt
```

Copy/paste predictions into spreadsheet

#### Step 3: Record Results

After each race, log:
- **Result:** WIN / PLACE / LOSE
- **Actual Price:** What price when you would have placed bet
- **Payout:** Win price × $1

#### Step 4: Calculate Key Metrics

**After 2-4 weeks of data:**

1. **Win Rate by Score Range**
   ```
   65+ score races: 10 wins / 20 bets = 50% win rate
   50-64 score races: 4 wins / 12 bets = 33% win rate
   ```

2. **ROI (Return on Investment)**
   ```
   Total Wagered: $320 (20 bets @ $16 each)
   Total Won: $420
   Net Profit: $100
   ROI: $100 / $320 = 31% 
   ```

3. **Expected Value per Score Threshold**
   ```
   75+ score: ROI 35% - EXCELLENT
   60-74 score: ROI 15% - GOOD
   50-59 score: ROI -5% - SKIP THESE
   ```

#### Step 5: Decide to Bet or Adjust

If 60+ scores are profitable → **Start betting**
If 50+ scores losing money → **Adjust heuristics**
If all scores losing money → **Different edge needed**

---

## Customizing Scores

### Adjusting Thresholds (Quick)

Edit `punter-edge/backend/scoring.py`, class `BetScorer.__init__()`:

```python
def __init__(self):
    self.min_overlay_pct = 5.0    # Minimum overlay % to consider
    self.min_odds = 1.5           # Minimum odds
    self.max_odds = 50.0          # Maximum odds
```

**Example: Only high-value bets**
```python
self.min_overlay_pct = 10.0  # Require 10%+ overlay (was 5%)
self.min_odds = 2.0          # No short odds (was 1.5)
```

### Adding Custom Signals

Edit `_calculate_score()` method to add your own signals:

```python
# Example: Prefer recent winners
def _calculate_score(...):
    score = 0.0
    
    # Existing code...
    # ... overlay, odds, liquidity ...
    
    # NEW: Add points if runner won in last 14 days
    # (you would need to add this data from form guide)
    if runner.days_since_last_win and runner.days_since_last_win < 14:
        score += 10
    
    return min(score, 100)
```

**Common custom signals:**
- Trainer win rate: `if trainer_wins_last_10 > 30: score += 15`
- Jockey form: `if jockey_wins_recent > 25: score += 10`
- Track bias: `if runner.track == "favourite_track": score += 5`
- Weight drop: `if weight_drop > 2kg: score += 8`

### Testing Changes

After editing scoring.py:

```bash
# Restart backend
python main.py

# Test in new terminal
python cli/main.py today-bets --api-key your_key

# Compare old vs new scores
```

---

## FAQ

### Q: How often should I run predictions?
**A:** Daily during racing season (typically Tue-Sat in Australia). Run in morning to catch day's races.

### Q: Can I bet on old race predictions?
**A:** Yes, but odds change. Use the "Odds @ Bet" column in your spreadsheet to track actual bet price vs predicted price.

### Q: Why does my score change between runs?
**A:** Odds update constantly. Re-run predictions 5-10 minutes before race to get latest odds.

### Q: Should I follow high-score bets blindly?
**A:** No. High scores mean good *odds value*, not guaranteed winner. Horses lose despite good odds. Only bet what you can afford to lose.

### Q: How do I know if my edge is real?
**A:** Track 50+ bets over 2-4 weeks. If ROI is positive, edge is real. If negative, adjust scoring or abandon approach.

### Q: Can I use this for other sports (AFL, NRL)?
**A:** Yes, API supports sports odds too. Update `cli/main.py` line 40 from `"racing"` to other sport codes.

### Q: What's the minimum stake?
**A:** Typically $1-$2 per race. Start small while validating edge.

### Q: Can I automate betting?
**A:** API supports it, but most Australian bookmakers require manual bet placement for compliance. Check your bookmaker's terms.

### Q: What if API is down?
**A:** Backend will fail with error. Check https://puntersedge.online/status for PuntersEdge outages.

### Q: Why am I getting "No races available"?
**A:** Races only available during racing hours (typically 9am-5pm AEST). Try again during race day.

### Q: How long until I can profit?
**A:** Typically 3-6 months of consistent tracking to:
1. Validate edge (2-4 weeks)
2. Confirm consistency (4-8 weeks)
3. Build confidence to bet confidently (ongoing)

---

## Support & Resources

**PuntersEdge Documentation:** https://puntersedge.online/developers

**Responsible Gambling:**
- Gamble only what you can afford to lose
- Set betting limits (e.g., max $10/day)
- Track all bets and ROI
- Take breaks when losing

**Gambling Help:** 1800 858 858 (Australia)

---

**Questions?** Check INSTALL.md for installation help or README.md for architecture details.
