"""Mock racing data for development and testing"""

from datetime import datetime, timedelta
from models import Race, Runner, BookmakerOdds, BetPrediction
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
                    BookmakerOdds(
                        key="neds",
                        win_price=round(random.uniform(1.5, 8.0), 2),
                        place_price=round(random.uniform(1.1, 3.0), 2)
                    ),
                    BookmakerOdds(
                        key="sportsbet",
                        win_price=round(random.uniform(1.5, 8.0), 2),
                        place_price=round(random.uniform(1.1, 3.0), 2)
                    ),
                    BookmakerOdds(
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
    return [
        {
            "horse": "Black Thunder",
            "predictions": 44,
            "wins": 12,
            "places": 24,
            "losses": 8,
            "win_rate": 27.3,
            "avg_roi": 18.5
        },
        {
            "horse": "Silver Flash",
            "predictions": 42,
            "wins": 10,
            "places": 22,
            "losses": 10,
            "win_rate": 23.8,
            "avg_roi": 15.2
        },
        {
            "horse": "Golden Dawn",
            "predictions": 40,
            "wins": 9,
            "places": 19,
            "losses": 12,
            "win_rate": 22.5,
            "avg_roi": 14.1
        }
    ]


def get_mock_user_performance():
    """Generate mock user performance data"""
    return [
        {
            "email": "john.smith@example.com",
            "predictions": 78,
            "wins": 24,
            "places": 31,
            "losses": 23,
            "win_rate": 30.8,
            "avg_roi": 12.6,
            "total_profit": 584.50
        },
        {
            "email": "sarah.jones@example.com",
            "total_predictions": 65,
            "wins": 18,
            "places": 28,
            "losses": 19,
            "win_rate": 27.7,
            "avg_roi": 10.2,
            "total_profit": 425.75
        },
        {
            "email": "mike.wilson@example.com",
            "total_predictions": 52,
            "wins": 15,
            "places": 22,
            "losses": 15,
            "win_rate": 28.8,
            "avg_roi": 14.1,
            "total_profit": 625.00
        }
    ]


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
