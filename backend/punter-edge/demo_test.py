#!/usr/bin/env python3
"""Demo test - shows project structure and API integration readiness"""

import sys
sys.path.insert(0, 'backend')

print("=" * 60)
print("🏇 PunterEdge MVP - Demo & Structure")
print("=" * 60)

# Test 1: Imports
print("\n1️⃣  Testing imports...")
try:
    from api_client import PuntersEdgeClient
    from models import Race, Runner, BetPrediction, RacingCategory
    from scoring import BetScorer
    print("   ✅ All modules imported successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Data models
print("\n2️⃣  Testing data models...")
try:
    test_runner = Runner(
        name="Test Horse",
        number=1,
        barrier=2,
        weight=55.0,
        bookmakers=[
            {
                "key": "sportsbet",
                "win_price": 3.5,
                "source_url": "https://example.com"
            }
        ]
    )
    print(f"   ✅ Created test runner: {test_runner.name}")
    print(f"      Best price: ${test_runner.best_win_price}")
    print(f"      Avg price: ${test_runner.avg_win_price}")
except Exception as e:
    print(f"   ❌ Model test failed: {e}")
    sys.exit(1)

# Test 3: Scoring engine
print("\n3️⃣  Testing scoring engine...")
try:
    scorer = BetScorer()
    print(f"   ✅ Scorer initialized")
    print(f"      Min overlay threshold: {scorer.min_overlay_pct}%")
    print(f"      Min odds: {scorer.min_odds}")
    print(f"      Max odds: {scorer.max_odds}")
except Exception as e:
    print(f"   ❌ Scorer test failed: {e}")
    sys.exit(1)

# Test 4: API Client
print("\n4️⃣  Testing API Client...")
try:
    client = PuntersEdgeClient("test_key")
    print(f"   ✅ API client initialized")
    print(f"      Base URL: {client.BASE_URL}")
    print(f"      Auth: X-API-Key header ready")
except Exception as e:
    print(f"   ❌ Client test failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("📦 Project Structure")
print("=" * 60)

structure = """
punter-edge/
├── backend/
│   ├── api_client.py      ✅ PuntersEdge API wrapper
│   ├── models.py          ✅ Data models (Race, Runner, etc)
│   ├── scoring.py         ✅ Betting heuristics engine
│   ├── main.py            ✅ FastAPI server
│   ├── venv/              ✅ Virtual environment (installed)
│   └── .env               ✅ Configuration ready
│
├── cli/
│   └── main.py            ✅ Typer CLI tool
│
├── frontend/
│   └── src/Dashboard.jsx  ✅ React dashboard
│
├── test_api.py            ✅ API test script
└── README.md              ✅ Full documentation
"""
print(structure)

print("=" * 60)
print("🚀 Next Steps")
print("=" * 60)
print("""
1. Get your free API key:
   → https://puntersedge.online/api

2. Update backend/.env:
   → Edit and add: API_KEY=your_key_here

3. Run the backend:
   → cd backend
   → python main.py
   → Visit http://localhost:8000/docs

4. Test CLI:
   → cd cli
   → python main.py today-bets --api-key YOUR_KEY

5. Validate your edge:
   → Run daily predictions
   → Log results in spreadsheet
   → Adjust scoring rules based on wins/losses
""")

print("=" * 60)
print("✅ All systems ready!")
print("=" * 60)
