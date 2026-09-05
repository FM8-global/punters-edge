from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RacingCategory(str, Enum):
    HORSE = "horse"
    GREYHOUND = "greyhound"
    HARNESS = "harness"


class BookmakerOdds(BaseModel):
    key: str  # bookmaker code (e.g., 'sportsbet', 'neds')
    win_price: Optional[float] = None
    place_price: Optional[float] = None
    each_way_price: Optional[float] = None
    source_url: Optional[str] = None

    class Config:
        extra = "allow"  # Allow extra fields from API


class Runner(BaseModel):
    name: str
    number: int
    barrier: Optional[int] = None
    weight: Optional[float] = None
    handicap: Optional[float] = None
    bookmakers: List[BookmakerOdds]

    class Config:
        extra = "allow"  # Allow extra fields from API

    @property
    def best_win_price(self) -> Optional[float]:
        """Get best win price across bookmakers"""
        prices = [b.win_price for b in self.bookmakers if b.win_price]
        return max(prices) if prices else None

    @property
    def avg_win_price(self) -> Optional[float]:
        """Get average win price"""
        prices = [b.win_price for b in self.bookmakers if b.win_price]
        return sum(prices) / len(prices) if prices else None


class Race(BaseModel):
    race_id: str
    venue: str
    race_number: int
    category: RacingCategory
    start_time: datetime
    country: str
    runners: List[Runner]

    class Config:
        use_enum_values = True
        extra = "allow"  # Allow extra fields from API


class RaceResponse(BaseModel):
    races: List[Race]
    demo: bool = False
    note: Optional[str] = None
    cached: bool = False


class BetPrediction(BaseModel):
    race_id: str
    race_venue: str
    race_number: int
    runner_name: str
    runner_number: int
    best_price: float
    avg_price: float
    overlay_pct: float
    score: float  # 0-100
    reasoning: str
    category: str
    start_time: datetime

    class Config:
        use_enum_values = True
