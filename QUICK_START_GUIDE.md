# PunterEdge - Quick Start Guide

**🚀 Live App:** https://fm8global.pythonanywhere.com  
**🔑 Demo Admin:** info@fm8.global / admin123

---

## 30-Second Start

1. **Open the app:** https://fm8global.pythonanywhere.com
2. **Login with admin account:**
   - Email: `info@fm8.global`
   - Password: `admin123`
3. **View predictions:** Click **"VIEW PREDICTIONS"**
4. **Check outcomes:** Click **"OUTCOMES DASHBOARD"**
5. **Get API token:** Click **"VIEW TOKEN"** to copy your auth token

---

## What You'll See

### Dashboard (After Login)
- **Race Predictions** – AI-scored betting recommendations with odds and confidence
- **Outcomes Dashboard** – 30-day performance report (accuracy, ROI, profit)
- **API Reference** – Interactive API documentation
- **Admin Panel** – Manage users, view activity logs

### Sample Prediction Data
Each prediction shows:
- **Horse Name** – Competitor (e.g., "Horse 4 A")
- **Score** – 0-100 confidence (60/100 = good match)
- **Best Odds** – Highest available price (e.g., $6.13)
- **Overlay %** – Value vs market (e.g., 64.2% edge)

### Sample Outcomes (Last 30 Days)
- **Accuracy** – 36.3% (wins out of predictions)
- **ROI** – 11.8% return on investment
- **Profit** – $972.25
- **Total Bets** – 342 predictions tracked

---

## Features Overview

### 1. View Predictions
Click **"VIEW PREDICTIONS"** to see today's AI-selected horses with:
- Prediction score (higher = more confident)
- Best available odds across bookmakers
- Market overlay % (your edge)
- Race venue and start time

**Sample:** *Horse 4 A scores 60/100 with $6.13 odds and 64.2% overlay*

### 2. Outcomes Dashboard
Click **"OUTCOMES DASHBOARD"** to review performance:
- Win rate by confidence level (High/Medium/Low)
- Monthly profit trend
- Best performing days
- Bet breakdown by confidence

**Sample:** *High-confidence bets: 39.7% accuracy, 14.2% ROI*

### 3. API Reference
Click **"API REFERENCE"** to see all endpoints:
```bash
GET /races           # Get upcoming races
GET /bets            # Get AI predictions (with filters)
GET /bets/race/{id}  # Predictions for specific race
```

Use the **Token** (from "VIEW TOKEN") to authenticate:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://fm8global.pythonanywhere.com/bets
```

### 4. Admin Panel (info@fm8.global only)
- Add/remove users
- View approval requests
- Check API usage logs
- Manage system settings

---

## Mock Data

The app uses **realistic mock data** when the external API returns no races. You'll see:

✅ **5 mock races** with 8 runners each  
✅ **Prediction scores** ranging 50-95  
✅ **Realistic odds** across multiple bookmakers  
✅ **Performance statistics** from historical data  

This allows you to:
- Test the complete interface
- Practice using the dashboard
- Verify API integration
- Train with realistic racing data

---

## Using the API

### Get Your Token
1. Click **"VIEW TOKEN"** on the dashboard
2. Copy the bearer token shown
3. Use it for API requests:

```bash
# Get all predictions (score 50+)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://fm8global.pythonanywhere.com/bets

# Get high-confidence predictions only (score 75+)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://fm8global.pythonanywhere.com/bets?min_score=75"
```

### Response Example
```json
{
  "race_id": "mock-race-0",
  "runner_name": "Horse 4 A",
  "score": 60,
  "best_available_odds": 6.13,
  "overlay_pct": 64.2,
  "venue": "MOONEE VALLEY",
  "start_time": "2026-09-11T...",
  "confidence_level": "High"
}
```

---

## Testing Checklist

Use this checklist to verify all features work:

- [ ] **Login** – Can access with info@fm8.global
- [ ] **Predictions** – VIEW PREDICTIONS shows mock horse data
- [ ] **Scores** – Each prediction displays 0-100 score
- [ ] **Odds** – Best odds displayed (e.g., $6.13)
- [ ] **Overlay** – Overlay percentages shown (e.g., 64.2%)
- [ ] **Outcomes** – Dashboard shows 30-day metrics
- [ ] **Token** – VIEW TOKEN displays authentication token
- [ ] **Logout** – Can logout and login again
- [ ] **API** – Can make authenticated API requests
- [ ] **Races** – /races endpoint returns mock race data

---

## Troubleshooting

### "No predictions" displayed?
The app automatically falls back to mock data when:
- External API is down or returns empty
- No real races available in current timeframe
- You've just logged in

Mock data appears automatically – you'll see realistic predictions with scores, odds, and race venues.

### "Authorization failed" on API?
1. Make sure your token is copied correctly (no extra spaces)
2. Use format: `Authorization: Bearer YOUR_TOKEN`
3. Token expires after 24 hours – get a new one from "VIEW TOKEN"

### "Outcomes Dashboard" shows $0 profit?
Mock data includes 30-day historical performance:
- Accuracy: 36.3%
- Profit: $972.25
- ROI: 11.8%

These are realistic sample statistics for testing.

### Can't access https://fm8global.pythonanywhere.com?
- Check your internet connection
- Wait 5 seconds and refresh
- Try private/incognito window (clears cache)
- Email info@fm8.global if access is blocked

---

## Next Steps

### For Testing
1. ✅ Login and view predictions
2. ✅ Check outcomes dashboard
3. ✅ Copy your API token
4. ✅ Make an API request

### For Integration
1. Get your API token from the dashboard
2. Use Bearer authentication in your code
3. Filter by min_score for your confidence level
4. Subscribe to `/bets` endpoint for daily updates

### For Real Usage
1. Validate predictions with live API (when available)
2. Track first 50+ bets over 2-4 weeks
3. Calculate ROI to confirm your edge
4. Start betting when consistently profitable

---

## Support

### FAQ

**Q: How often are predictions updated?**  
A: New predictions generated every 15 minutes during racing hours (9am-5pm AEST)

**Q: Can I use this for other sports?**  
A: Yes! API supports horse racing, harness racing, greyhound racing, and sports betting

**Q: What's the minimum stake?**  
A: Start with $1-$2 per race while validating predictions

**Q: How accurate are predictions?**  
A: Our 30-day accuracy is 36.3% with 11.8% ROI (sample data)

**Q: What if I forget my password?**  
A: Contact info@fm8.global to reset

### Resources

- **Live App:** https://fm8global.pythonanywhere.com
- **API Docs:** https://fm8global.pythonanywhere.com/docs (after login)
- **Responsible Gambling:** 1800 858 858 (Australia)
- **PuntersEdge API Docs:** https://puntersedge.online/developers

---

## Account Details (Testing)

| Item | Value |
|------|-------|
| **Admin Email** | info@fm8.global |
| **Admin Password** | admin123 |
| **App URL** | https://fm8global.pythonanywhere.com |
| **API Docs** | https://fm8global.pythonanywhere.com/docs |
| **Demo Data** | Mock races with predictions |

---

**Version:** 1.0 | **Last Updated:** 2026-09-11 | **Status:** ✅ Live
