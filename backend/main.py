from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
import logging
import os
from api_client import PuntersEdgeClient
from models import Race, BetPrediction, RaceResponse
from scoring import BetScorer
from typing import List, Optional
from dotenv import load_dotenv
from auth import (
    validate_session, create_session, logout_session,
    is_user_approved, add_approved_user, remove_approved_user,
    get_approved_users, is_admin, is_email_valid
)
from pydantic import BaseModel

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
api_key = os.getenv("API_KEY", "test_key")
debug = os.getenv("DEBUG", "False") == "True"
app = FastAPI(title="PunterEdge API", version="0.1.0")
scorer = BetScorer()
client = PuntersEdgeClient(api_key)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LoginRequest(BaseModel):
    email: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: str

class UserManagement(BaseModel):
    email: str

# Helper: Get authenticated email from header
def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """Extract and validate auth token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token")

    # Token format: "Bearer <token>"
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    email = validate_session(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return email


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


# AUTH ENDPOINTS

@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with email"""
    email = request.email.lower().strip()

    if not is_email_valid(email):
        return LoginResponse(success=False, message="Invalid email format")

    if not is_user_approved(email):
        return LoginResponse(success=False, message="Email not approved. Contact info@fm8.global")

    token = create_session(email)
    return LoginResponse(
        success=True,
        token=token,
        message=f"Welcome {email}!"
    )


@app.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Logout user"""
    if authorization:
        try:
            token = authorization.split(" ")[1]
            logout_session(token)
        except:
            pass
    return {"message": "Logged out"}


@app.get("/me")
async def get_current_user_info(email: str = Header(None, alias="X-User-Email")):
    """Get current user info"""
    # This will be called after auth check
    return {"email": email, "is_admin": is_admin(email)}


# ADMIN ENDPOINTS

@app.get("/admin/users")
async def list_users(authorization: Optional[str] = Header(None)):
    """List approved users (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    return {"approved_users": get_approved_users()}


@app.post("/admin/users/add")
async def add_user(request: UserManagement, authorization: Optional[str] = Header(None)):
    """Add approved user (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    new_email = request.email.lower().strip()
    if add_approved_user(new_email):
        return {"message": f"User {new_email} approved"}
    return {"message": "Failed to add user", "error": "Invalid email"}


@app.post("/admin/users/remove")
async def remove_user(request: UserManagement, authorization: Optional[str] = Header(None)):
    """Remove approved user (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    remove_email = request.email.lower().strip()
    if remove_user(remove_email):
        return {"message": f"User {remove_email} removed"}
    return {"message": "Failed to remove user"}


# PROTECTED API ENDPOINTS

@app.get("/races", response_model=list)
async def get_races(authorization: Optional[str] = Header(None)):
    """Get upcoming races with live odds (authenticated)"""
    email = get_current_user(authorization)

    try:
        races_data = await client.get_racing_next_to_go()
        return [Race(**race) for race in races_data]
    except Exception as e:
        logger.error(f"Error fetching races: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch races")


@app.get("/bets", response_model=List[BetPrediction])
async def get_bets(min_score: float = 50.0, authorization: Optional[str] = Header(None)):
    """
    Get all bet predictions filtered by score (authenticated).
    Default minimum score: 50/100
    """
    email = get_current_user(authorization)

    try:
        races_data = await client.get_racing_next_to_go()
        races = [Race(**race) for race in races_data]

        all_predictions = []
        for race in races:
            predictions = scorer.score_race(race)
            all_predictions.extend(predictions)

        filtered = [p for p in all_predictions if p.score >= min_score]
        return sorted(filtered, key=lambda x: x.score, reverse=True)

    except Exception as e:
        logger.error(f"Error scoring races: {e}")
        raise HTTPException(status_code=500, detail="Failed to score races")


@app.get("/bets/race/{race_id}", response_model=List[BetPrediction])
async def get_bets_for_race(race_id: str, min_score: float = 50.0, authorization: Optional[str] = Header(None)):
    """Get predictions for a specific race (authenticated)"""
    email = get_current_user(authorization)

    try:
        races_data = await client.get_racing_next_to_go()
        races = [Race(**race) for race in races_data]

        target_race = next((r for r in races if r.race_id == race_id), None)
        if not target_race:
            raise HTTPException(status_code=404, detail="Race not found")

        predictions = scorer.score_race(target_race)
        filtered = [p for p in predictions if p.score >= min_score]
        return sorted(filtered, key=lambda x: x.score, reverse=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch race")


@app.post("/score/adjust-threshold")
async def adjust_score_threshold(min_overlay: float = 5.0, min_odds: float = 1.5, authorization: Optional[str] = Header(None)):
    """Adjust betting heuristics (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    scorer.min_overlay_pct = min_overlay
    scorer.min_odds = min_odds
    return {
        "min_overlay_pct": scorer.min_overlay_pct,
        "min_odds": scorer.min_odds
    }


# Serve static files
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

try:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


# Root/Login page
@app.get("/", response_class=HTMLResponse)
async def login_page():
    """Serve login page"""
    login_file = STATIC_DIR / "login.html"
    if login_file.exists():
        with open(login_file, 'r') as f:
            return f.read()
    return "<h1>PunterEdge</h1><p>Login page not found. Visit /docs for API docs.</p>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
