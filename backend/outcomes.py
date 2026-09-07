"""Prediction Outcomes Tracking for PunterEdge

Tracks prediction performance and enables learning from historical data.
"""

import psycopg2
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
import os
import json

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")

def get_db_connection():
    """Get PostgreSQL connection"""
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable not set - outcomes unavailable")
        return None
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None

def init_outcomes_tables():
    """Initialize prediction outcomes tracking tables"""
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not set - outcomes tracking disabled (use Render for PostgreSQL)")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Prediction outcomes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_outcomes (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255),
                race_id VARCHAR(255) NOT NULL,
                track VARCHAR(255),
                race_num VARCHAR(50),
                horse_name VARCHAR(255) NOT NULL,
                predicted_score DECIMAL(5, 2),
                predicted_odds DECIMAL(10, 2),
                prediction_date TIMESTAMP NOT NULL,
                race_date TIMESTAMP,
                actual_result VARCHAR(50),
                actual_odds DECIMAL(10, 2),
                payoff DECIMAL(10, 2),
                roi DECIMAL(10, 2),
                notes TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE SET NULL
            )
        """)

        # Performance summary by horse
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS horse_performance (
                horse_name VARCHAR(255) PRIMARY KEY,
                total_predictions INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                places INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_rate DECIMAL(5, 2) DEFAULT 0,
                avg_roi DECIMAL(10, 2) DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Performance summary by user
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_performance (
                email VARCHAR(255) PRIMARY KEY,
                total_predictions INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                places INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_rate DECIMAL(5, 2) DEFAULT 0,
                avg_roi DECIMAL(10, 2) DEFAULT 0,
                total_profit DECIMAL(15, 2) DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_race ON prediction_outcomes(race_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_horse ON prediction_outcomes(horse_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_email ON prediction_outcomes(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_result ON prediction_outcomes(actual_result)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_date ON prediction_outcomes(prediction_date)")

        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Prediction outcomes tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing outcomes tables: {e}")
        raise

def record_prediction_outcome(
    race_id: str,
    horse_name: str,
    predicted_score: float,
    predicted_odds: float,
    prediction_date: datetime,
    race_date: datetime,
    actual_result: str,
    actual_odds: float = None,
    payoff: float = None,
    email: str = None,
    track: str = None,
    race_num: str = None
) -> bool:
    """Record prediction outcome after race is complete"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - outcome not recorded")
            return False
        cursor = conn.cursor()

        # Calculate ROI
        roi = None
        if payoff is not None and predicted_odds is not None:
            stake = 100.0  # Assume $100 stake for calculation
            roi = ((payoff - stake) / stake * 100) if stake > 0 else 0

        cursor.execute("""
            INSERT INTO prediction_outcomes
            (race_id, horse_name, predicted_score, predicted_odds, prediction_date,
             race_date, actual_result, actual_odds, payoff, roi, email, track, race_num)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (race_id, horse_name, predicted_score, predicted_odds, prediction_date,
              race_date, actual_result, actual_odds, payoff, roi, email, track, race_num))

        conn.commit()
        cursor.close()
        conn.close()

        # Update summary tables
        update_performance_summary(horse_name, email, actual_result, roi)
        return True
    except Exception as e:
        logger.error(f"Error recording prediction outcome: {e}")
        return False

def update_performance_summary(horse_name: str, email: str = None, result: str = None, roi: float = None):
    """Update horse and user performance summaries"""
    try:
        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor()

        # Update horse performance
        if horse_name:
            cursor.execute("""
                INSERT INTO horse_performance (horse_name, total_predictions)
                VALUES (%s, 1)
                ON CONFLICT (horse_name) DO UPDATE SET
                total_predictions = total_predictions + 1
            """, (horse_name,))

            if result == 'win':
                cursor.execute("UPDATE horse_performance SET wins = wins + 1 WHERE horse_name = %s", (horse_name,))
            elif result == 'place':
                cursor.execute("UPDATE horse_performance SET places = places + 1 WHERE horse_name = %s", (horse_name,))
            elif result == 'loss':
                cursor.execute("UPDATE horse_performance SET losses = losses + 1 WHERE horse_name = %s", (horse_name,))

            # Update win rate and ROI
            cursor.execute("""
                UPDATE horse_performance
                SET win_rate = ROUND((wins::DECIMAL / total_predictions) * 100, 2),
                    avg_roi = (SELECT ROUND(AVG(roi), 2) FROM prediction_outcomes WHERE horse_name = %s),
                    last_updated = CURRENT_TIMESTAMP
                WHERE horse_name = %s
            """, (horse_name, horse_name))

        # Update user performance
        if email:
            cursor.execute("""
                INSERT INTO user_performance (email, total_predictions)
                VALUES (%s, 1)
                ON CONFLICT (email) DO UPDATE SET
                total_predictions = total_predictions + 1
            """, (email,))

            if result == 'win':
                cursor.execute("UPDATE user_performance SET wins = wins + 1 WHERE email = %s", (email,))
            elif result == 'place':
                cursor.execute("UPDATE user_performance SET places = places + 1 WHERE email = %s", (email,))
            elif result == 'loss':
                cursor.execute("UPDATE user_performance SET losses = losses + 1 WHERE email = %s", (email,))

            # Update win rate, ROI, and total profit
            cursor.execute("""
                UPDATE user_performance
                SET win_rate = ROUND((wins::DECIMAL / total_predictions) * 100, 2),
                    avg_roi = (SELECT ROUND(AVG(roi), 2) FROM prediction_outcomes WHERE email = %s),
                    total_profit = (SELECT ROUND(SUM(COALESCE(payoff, 0) - 100), 2) FROM prediction_outcomes WHERE email = %s),
                    last_updated = CURRENT_TIMESTAMP
                WHERE email = %s
            """, (email, email, email))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error updating performance summary: {e}")

def get_outcomes_by_horse(horse_name: str, limit: int = 50) -> List[Dict]:
    """Get all prediction outcomes for a specific horse"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT race_id, horse_name, predicted_score, predicted_odds,
                   prediction_date, race_date, actual_result, actual_odds,
                   payoff, roi, email, track, race_num
            FROM prediction_outcomes
            WHERE horse_name = %s
            ORDER BY prediction_date DESC
            LIMIT %s
        """, (horse_name, limit))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        return [
            {
                "race_id": row[0],
                "horse_name": row[1],
                "predicted_score": float(row[2]) if row[2] else None,
                "predicted_odds": float(row[3]) if row[3] else None,
                "prediction_date": row[4].isoformat() if row[4] else None,
                "race_date": row[5].isoformat() if row[5] else None,
                "actual_result": row[6],
                "actual_odds": float(row[7]) if row[7] else None,
                "payoff": float(row[8]) if row[8] else None,
                "roi": float(row[9]) if row[9] else None,
                "email": row[10],
                "track": row[11],
                "race_num": row[12]
            }
            for row in results
        ]
    except Exception as e:
        logger.error(f"Error getting horse outcomes: {e}")
        return []

def get_horse_performance(horse_name: str = None) -> Dict:
    """Get performance summary for horse(s)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if horse_name:
            cursor.execute("""
                SELECT horse_name, total_predictions, wins, places, losses,
                       win_rate, avg_roi
                FROM horse_performance
                WHERE horse_name = %s
            """, (horse_name,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                return {
                    "horse_name": result[0],
                    "total_predictions": result[1],
                    "wins": result[2],
                    "places": result[3],
                    "losses": result[4],
                    "win_rate": float(result[5]) if result[5] else 0,
                    "avg_roi": float(result[6]) if result[6] else 0
                }
        else:
            cursor.execute("""
                SELECT horse_name, total_predictions, wins, places, losses,
                       win_rate, avg_roi
                FROM horse_performance
                ORDER BY total_predictions DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return [
                {
                    "horse_name": row[0],
                    "total_predictions": row[1],
                    "wins": row[2],
                    "places": row[3],
                    "losses": row[4],
                    "win_rate": float(row[5]) if row[5] else 0,
                    "avg_roi": float(row[6]) if row[6] else 0
                }
                for row in results
            ]

        return {}
    except Exception as e:
        logger.error(f"Error getting horse performance: {e}")
        return {}

def get_user_performance(email: str = None) -> Dict:
    """Get performance summary for user(s)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if email:
            cursor.execute("""
                SELECT email, total_predictions, wins, places, losses,
                       win_rate, avg_roi, total_profit
                FROM user_performance
                WHERE email = %s
            """, (email,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                return {
                    "email": result[0],
                    "total_predictions": result[1],
                    "wins": result[2],
                    "places": result[3],
                    "losses": result[4],
                    "win_rate": float(result[5]) if result[5] else 0,
                    "avg_roi": float(result[6]) if result[6] else 0,
                    "total_profit": float(result[7]) if result[7] else 0
                }
        else:
            cursor.execute("""
                SELECT email, total_predictions, wins, places, losses,
                       win_rate, avg_roi, total_profit
                FROM user_performance
                ORDER BY total_profit DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            return [
                {
                    "email": row[0],
                    "total_predictions": row[1],
                    "wins": row[2],
                    "places": row[3],
                    "losses": row[4],
                    "win_rate": float(row[5]) if row[5] else 0,
                    "avg_roi": float(row[6]) if row[6] else 0,
                    "total_profit": float(row[7]) if row[7] else 0
                }
                for row in results
            ]

        return {}
    except Exception as e:
        logger.error(f"Error getting user performance: {e}")
        return {}

def get_outcomes_report(start_date: datetime = None, end_date: datetime = None,
                       min_score: float = None) -> Dict:
    """Generate outcomes report for date range and minimum score"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM prediction_outcomes WHERE 1=1"
        params = []

        if start_date:
            query += " AND prediction_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND prediction_date <= %s"
            params.append(end_date)

        if min_score:
            query += " AND predicted_score >= %s"
            params.append(min_score)

        query += " ORDER BY prediction_date DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()

        # Calculate summary stats
        total = len(results)
        wins = sum(1 for row in results if row[7] == 'win')
        places = sum(1 for row in results if row[7] == 'place')
        losses = sum(1 for row in results if row[7] == 'loss')

        win_rate = (wins / total * 100) if total > 0 else 0
        avg_roi = sum(float(row[9]) if row[9] else 0 for row in results) / total if total > 0 else 0

        cursor.close()
        conn.close()

        return {
            "total_predictions": total,
            "wins": wins,
            "places": places,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "avg_roi": round(avg_roi, 2),
            "outcomes": [
                {
                    "race_id": row[2],
                    "track": row[14] if len(row) > 14 else None,
                    "race_num": row[15] if len(row) > 15 else None,
                    "horse_name": row[3],
                    "predicted_score": float(row[4]) if row[4] else None,
                    "predicted_odds": float(row[5]) if row[5] else None,
                    "prediction_date": row[6].isoformat() if row[6] else None,
                    "actual_result": row[8],
                    "roi": float(row[10]) if row[10] else None
                }
                for row in results
            ]
        }
    except Exception as e:
        logger.error(f"Error generating outcomes report: {e}")
        return {}
