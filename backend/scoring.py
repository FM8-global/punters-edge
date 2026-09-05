from typing import Optional, List
from models import Race, Runner, BetPrediction
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BetScorer:
    """Score betting selections based on manual heuristics"""

    def __init__(self):
        self.min_overlay_pct = 5.0  # Only consider bets with 5%+ overlay
        self.min_odds = 1.5  # Minimum odds to consider
        self.max_odds = 50.0  # Maximum odds

    def score_race(self, race: Race) -> List[BetPrediction]:
        """Score all runners in a race, return high-value bets"""
        predictions = []

        for runner in race.runners:
            score = self._score_runner(runner, race)
            if score and score.score >= 40:  # Threshold for inclusion
                predictions.append(score)

        return sorted(predictions, key=lambda x: x.score, reverse=True)

    def _score_runner(self, runner: Runner, race: Race) -> Optional[BetPrediction]:
        """Score individual runner"""
        best_price = runner.best_win_price
        avg_price = runner.avg_win_price

        if not best_price or not avg_price:
            return None

        # Filter by odds range
        if best_price < self.min_odds or best_price > self.max_odds:
            return None

        # Calculate overlay
        overlay_pct = ((best_price - avg_price) / avg_price * 100) if avg_price > 0 else 0

        # Minimum overlay threshold
        if overlay_pct < self.min_overlay_pct:
            return None

        # Score calculation (0-100 scale)
        score = self._calculate_score(
            best_price=best_price,
            overlay_pct=overlay_pct,
            runner=runner,
            race=race
        )

        reasoning = self._generate_reasoning(
            best_price=best_price,
            overlay_pct=overlay_pct,
            score=score
        )

        return BetPrediction(
            race_id=race.race_id,
            race_venue=race.venue,
            race_number=race.race_number,
            runner_name=runner.name,
            runner_number=runner.number,
            best_price=best_price,
            avg_price=avg_price,
            overlay_pct=overlay_pct,
            score=score,
            reasoning=reasoning,
            category=race.category,
            start_time=race.start_time
        )

    def _calculate_score(
        self,
        best_price: float,
        overlay_pct: float,
        runner: Runner,
        race: Race
    ) -> float:
        """
        Calculate bet score (0-100).
        Heuristics to tune based on your edge validation.
        """
        score = 0.0

        # Base score from overlay percentage
        # Higher overlay = better value
        if overlay_pct >= 20:
            score += 40
        elif overlay_pct >= 10:
            score += 30
        elif overlay_pct >= 5:
            score += 20

        # Price range preference
        # Often sweet spot is 2.0-8.0 odds in racing
        if 2.0 <= best_price <= 8.0:
            score += 20
        elif 1.5 <= best_price < 2.0:
            score += 10
        elif 8.0 < best_price <= 15.0:
            score += 15
        elif best_price > 15.0:
            score += 5

        # Number of bookmakers offering price
        # Higher liquidity = more reliable odds
        num_books = len([b for b in runner.bookmakers if b.win_price])
        if num_books >= 10:
            score += 20
        elif num_books >= 8:
            score += 15
        elif num_books >= 5:
            score += 10

        # Barrier/weight data (when available)
        if runner.barrier and runner.barrier <= 2:
            score += 10
        if runner.weight and race.category == "horse":
            if runner.weight <= 53:  # Light weight
                score += 5

        return min(score, 100)

    def _generate_reasoning(
        self,
        best_price: float,
        overlay_pct: float,
        score: float
    ) -> str:
        """Generate human-readable explanation for the bet score"""
        reasons = []

        if overlay_pct >= 20:
            reasons.append(f"Excellent overlay: {overlay_pct:.1f}%")
        elif overlay_pct >= 10:
            reasons.append(f"Good overlay: {overlay_pct:.1f}%")
        else:
            reasons.append(f"Moderate overlay: {overlay_pct:.1f}%")

        if 2.0 <= best_price <= 8.0:
            reasons.append("Sweet spot odds range")
        elif best_price < 2.0:
            reasons.append("Favourite—low odds but good value")

        return " | ".join(reasons)
