#!/usr/bin/env python3
"""Quick test of PuntersEdge API integration"""

import asyncio
import sys
sys.path.insert(0, 'backend')

from api_client import PuntersEdgeClient
from models import Race
from scoring import BetScorer


async def test_api_connection(api_key: str):
    """Test API connection and data flow"""
    print("🧪 Testing PunterEdge API Integration\n")

    client = PuntersEdgeClient(api_key)
    scorer = BetScorer()

    try:
        # Test 1: Fetch races
        print("1️⃣  Fetching upcoming races...")
        races_data = await client.get_racing_next_to_go()

        if 'races' not in races_data:
            print("   ❌ No races data in response")
            return False

        races = [Race(**race) for race in races_data.get('races', [])]
        print(f"   ✅ Fetched {len(races)} races")

        if len(races) == 0:
            print("   ⚠️  No races currently available (normal outside racing hours)")
            return True

        # Test 2: Show first race
        race = races[0]
        print(f"\n2️⃣  Sample race: {race.venue} Race {race.race_number}")
        print(f"   Category: {race.category}")
        print(f"   Start time: {race.start_time}")
        print(f"   Runners: {len(race.runners)}")

        # Test 3: Score the race
        print(f"\n3️⃣  Scoring runners...")
        predictions = scorer.score_race(race)
        print(f"   ✅ Scored {len(race.runners)} runners")

        if predictions:
            top_pred = predictions[0]
            print(f"\n   Top selection:")
            print(f"   - Runner: #{top_pred.runner_number} {top_pred.runner_name}")
            print(f"   - Best Price: ${top_pred.best_price:.2f}")
            print(f"   - Overlay: {top_pred.overlay_pct:.1f}%")
            print(f"   - Score: {top_pred.score:.0f}/100")
            print(f"   - Reason: {top_pred.reasoning}")
        else:
            print(f"   ⚠️  No high-scoring selections (threshold: 40/100)")

        print(f"\n✅ API integration working!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    api_key = input("Enter your PuntersEdge API key: ").strip()

    if not api_key:
        print("❌ API key required")
        sys.exit(1)

    success = asyncio.run(test_api_connection(api_key))
    sys.exit(0 if success else 1)
