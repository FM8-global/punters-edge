"""Mock racing data for development and testing"""

from datetime import datetime, timedelta
from models import Race, Runner, Bookmaker, BetPrediction
import random

def get_mock_races():
    """Generate mock racing data for testing"""
    races = []

    base_time = datetime.utcnow()

    for i in range(5):
        race_time = base_time + timedelta(hours=i)

        runners = []
        for j in range(1, 9):
            runner = Runner(
                name=f"Horse {j} {chr(65+i)}",
                number=j,
                bookmakers=[
                    Bookmaker(
                        key="neds",
                        win_price=round(random.uniform(1.5, 8.0), 2),
                        place_price=round(random.uniform(1.1, 3.0), 2)
                    ),
                    Bookmaker(
                        key="sportsbet",
                        win_price=round(random.uniform(1.5, 8.0), 2),
                        place_price=round(random.uniform(1.1, 3.0), 2)
                    ),
                    Bookmaker(
                        key="betfair",
                        win_price=round(random.uniform(1.5, 8.0), 2),
                        place_price=round(random.uniform(1.1, 3.0), 2)
                    )
                ]
            )
            runners.append(runner)

        race = Race(
            race_id=f"mock-race-{i}",
            venue=["MOONEE VALLEY", "FLEMINGTON", "RANDWICK", "EAGLE FARM"][i % 4],
            venue_id=["moonee-valley", "flemington", "randwick", "eagle-farm"][i % 4],
            race_number=i + 1,
            category="horse",
            start_time=race_time.isoformat() + "Z",
            country="AU",
            race_name=f"Mock Race {i+1} - Test Event",
            distance_m=2000,
            track_condition="Good",
            weather="Fine",
            runners=runners,
            places_paid=3,
            scratchings=[]
        )
        races.append(race)

    return races


def get_mock_predictions():
    """Generate mock predictions for testing"""
    predictions = []

    races = get_mock_races()

    for race in races:
        for runner in race.runners:
            if random.random() > 0.3:  # 70% of runners get predictions
                prediction = BetPrediction(
                    race_id=race.race_id,
                    runner_name=runner.name,
                    runner_number=runner.number,
                    venue=race.venue,
                    start_time=race.start_time,
                    score=round(random.uniform(50, 95), 1),
                    predicted_odds=round(random.uniform(1.5, 6.0), 2),
                    best_available_odds=round(random.uniform(1.5, 6.0), 2),
                    recommended_bookmaker="neds",
                    confidence_level=random.choice(["High", "Medium", "Low"]),
                    reasoning=f"Mock prediction for {runner.name} in {race.race_name}"
                )
                predictions.append(prediction)

    return sorted(predictions, key=lambda x: x.score, reverse=True)


def get_mock_horse_performance():
    """Generate mock horse performance data"""
    return {
        "total_races": 245,
        "wins": 62,
        "places": 98,
        "win_rate": 25.3,
        "place_rate": 58.4,
        "average_odds": 4.2,
        "roi": 12.5,
        "top_performers": [
            {
                "horse": "Black Thunder",
                "wins": 12,
                "places": 24,
                "roi": 18.5
            },
            {
                "horse": "Silver Flash",
                "wins": 10,
                "places": 22,
                "roi": 15.2
            },
            {
                "horse": "Golden Dawn",
                "wins": 9,
                "places": 19,
                "roi": 14.1
            }
        ]
    }


def get_mock_user_performance():
    """Generate mock user performance data"""
    return {
        "total_bets": 156,
        "winning_bets": 47,
        "win_rate": 30.1,
        "total_staked": 4650.00,
        "total_returns": 5234.50,
        "profit": 584.50,
        "roi": 12.6,
        "average_odds": 3.8,
        "best_day": {
            "date": "2026-09-05",
            "profit": 245.00,
            "bets": 8
        },
        "monthly_trend": [
            {"month": "July", "profit": 125.50, "bets": 42},
            {"month": "August", "profit": 234.25, "bets": 58},
            {"month": "September", "profit": 225.00, "bets": 56}
        ]
    }


def get_mock_outcomes_report():
    """Generate mock outcomes report data"""
    return {
        "period": "Last 30 days",
        "total_predictions": 342,
        "winning_predictions": 124,
        "accuracy": 36.3,
        "roi": 11.8,
        "total_staked": 8234.50,
        "total_returns": 9206.75,
        "profit": 972.25,
        "by_confidence": {
            "high": {"predictions": 156, "wins": 62, "accuracy": 39.7, "roi": 14.2},
            "medium": {"predictions": 128, "wins": 42, "accuracy": 32.8, "roi": 9.5},
            "low": {"predictions": 58, "wins": 20, "accuracy": 34.5, "roi": 8.1}
        }
    }
