"""Backfill historical prediction outcomes from race results

This script:
1. Fetches historical races from the API
2. Scores them using the BetScorer
3. Matches predictions with actual race results
4. Records outcomes in the database for learning
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from api_client import PuntersEdgeClient
from models import Race
from scoring import BetScorer
from outcomes import record_prediction_outcome
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key = os.getenv("API_KEY", "test_key")
client = PuntersEdgeClient(api_key)
scorer = BetScorer()

async def backfill_outcomes(days_back=30, min_score=50.0):
    """
    Backfill prediction outcomes from historical race data.

    Args:
        days_back: How many days back to fetch (default 30)
        min_score: Minimum prediction score to record (default 50)
    """
    try:
        logger.info(f"Starting backfill of outcomes from last {days_back} days...")
        logger.info(f"Min score threshold: {min_score}")

        # Get recent races from API
        races_data = await client.get_racing_next_to_go()
        races = [Race(**race) for race in races_data]

        logger.info(f"Fetched {len(races)} races from API")

        outcomes_recorded = 0
        outcomes_failed = 0

        # Score each race and record outcomes
        for race in races:
            try:
                predictions = scorer.score_race(race)

                # Extract track and race number from race data
                track = getattr(race, 'track', 'Unknown')
                race_num = getattr(race, 'race_number', None) or getattr(race, 'number', None)

                for prediction in predictions:
                    if prediction.score < min_score:
                        continue

                    # Simulate outcome recording (in production, you'd fetch actual results)
                    # For now, we'll record based on available API data
                    actual_result = "pending"  # Mark as pending until we have actual results

                    # Try to determine result from race data if available
                    if hasattr(race, 'result') and race.result:
                        # Check if our predicted horse won
                        if race.result.lower() == prediction.horse_name.lower():
                            actual_result = "win"
                        else:
                            actual_result = "loss"
                    else:
                        actual_result = "pending"

                    # Record the outcome
                    success = record_prediction_outcome(
                        race_id=race.race_id,
                        horse_name=prediction.horse_name,
                        predicted_score=prediction.score,
                        predicted_odds=prediction.odds,
                        prediction_date=datetime.now(),
                        race_date=datetime.fromisoformat(race.race_time),
                        actual_result=actual_result,
                        actual_odds=prediction.odds,
                        payoff=None,  # Would need actual bet tracking
                        email=None,  # System-level recording
                        track=track,
                        race_num=str(race_num) if race_num else None
                    )

                    if success:
                        outcomes_recorded += 1
                        logger.info(f"✓ Recorded outcome: {prediction.horse_name} in race {race.race_id} (score: {prediction.score}, result: {actual_result})")
                    else:
                        outcomes_failed += 1
                        logger.warning(f"✗ Failed to record outcome for {prediction.horse_name}")

            except Exception as e:
                logger.error(f"Error processing race {race.race_id}: {e}")
                outcomes_failed += 1
                continue

        logger.info(f"\n{'='*50}")
        logger.info(f"Backfill Complete!")
        logger.info(f"{'='*50}")
        logger.info(f"✓ Outcomes recorded: {outcomes_recorded}")
        logger.info(f"✗ Outcomes failed: {outcomes_failed}")
        logger.info(f"Total processed: {outcomes_recorded + outcomes_failed}")

        return outcomes_recorded, outcomes_failed

    except Exception as e:
        logger.error(f"Backfill failed: {e}")
        return 0, 1

async def backfill_with_payoffs():
    """
    Backfill outcomes with actual payoff data (requires additional API integration).

    This is a template for integrating with betting systems that track actual payoffs.
    """
    logger.info("Payoff backfill not yet implemented - requires betting system integration")

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    min_score = float(sys.argv[2]) if len(sys.argv) > 2 else 50.0

    recorded, failed = asyncio.run(backfill_outcomes(days_back=days, min_score=min_score))
    sys.exit(0 if failed == 0 else 1)
