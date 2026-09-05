import httpx
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PuntersEdgeClient:
    """PuntersEdge Australian Odds API client"""

    BASE_URL = "https://api.puntersedge.online/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}
        self.timeout = 15

    async def get_racing_next_to_go(self) -> list:
        """Get upcoming races with live odds - returns list of races"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/racing/next-to-go",
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                # API returns list directly
                return data if isinstance(data, list) else data.get('races', [])
            except httpx.HTTPError as e:
                logger.error(f"PuntersEdge API error: {e}")
                raise

    async def get_best_odds(self, sport: str = "racing") -> dict:
        """Get best odds across all bookmakers by sport"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/best-odds/{sport}",
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"PuntersEdge API error: {e}")
                raise

    async def get_arb_best_prices(self) -> dict:
        """Get arbitrage data with overlay metrics"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/arb/best-prices",
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"PuntersEdge API error: {e}")
                raise

    async def get_odds_by_bookmaker(self, bookmaker: str) -> dict:
        """Get odds from specific bookmaker"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/odds-by-bookmaker/{bookmaker}",
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"PuntersEdge API error: {e}")
                raise
