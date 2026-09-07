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
    get_approved_users, is_admin, is_email_valid, make_admin,
    remove_admin, get_all_users, request_access, get_pending_requests,
    approve_request, reject_request, verify_admin_password, ADMIN_EMAIL, init_db
)
from compliance import (
    init_compliance_tables, verify_age, is_age_verified, is_self_excluded,
    set_betting_limits, get_betting_limits, request_self_exclusion,
    log_betting_activity, get_compliance_report, create_compliance_alert
)
from outcomes import (
    init_outcomes_tables, record_prediction_outcome, get_horse_performance,
    get_user_performance, get_outcomes_report, get_outcomes_by_horse
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

# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database schema on startup"""
    try:
        init_db()
        init_compliance_tables()
        init_outcomes_tables()
        logger.info("Database, compliance, and outcomes tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Models
class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    message: str

class UserManagement(BaseModel):
    email: str

class AgeVerificationRequest(BaseModel):
    email: str
    date_of_birth: str

class BettingLimitsRequest(BaseModel):
    daily_limit: Optional[float] = None
    weekly_limit: Optional[float] = None
    monthly_limit: Optional[float] = None
    session_minutes: Optional[int] = None

class SelfExclusionRequest(BaseModel):
    email: str
    duration_days: int = 180
    reason: Optional[str] = None

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
    """Login with email (and password for admin)"""
    email = request.email.lower().strip()

    if not is_email_valid(email):
        return LoginResponse(success=False, message="Invalid email format")

    # Admin requires password
    if email == ADMIN_EMAIL:
        if not request.password:
            return LoginResponse(success=False, message="Password required for admin account")
        if not verify_admin_password(request.password):
            return LoginResponse(success=False, message="Invalid admin password")
    elif not is_user_approved(email):
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


@app.post("/signup", response_model=LoginResponse)
async def signup(request: LoginRequest):
    """Request access to PunterEdge"""
    email = request.email.lower().strip()

    if not is_email_valid(email):
        return LoginResponse(success=False, message="Invalid email format")

    if request_access(email):
        return LoginResponse(
            success=True,
            message=f"Access request submitted for {email}. An admin will review your request shortly."
        )
    return LoginResponse(
        success=False,
        message="Email is already approved or pending. Try logging in or contact info@fm8.global"
    )


@app.post("/compliance/verify-age")
async def verify_age_endpoint(request: AgeVerificationRequest):
    """Verify user is 18+ years old (Australian gambling requirement)"""
    email = request.email.lower().strip()

    if not is_email_valid(email):
        return {"success": False, "message": "Invalid email format"}

    if verify_age(email, request.date_of_birth):
        return {
            "success": True,
            "message": "Age verified. You can now complete your account setup."
        }
    return {
        "success": False,
        "message": "You must be 18 years or older to use PunterEdge. If you believe this is an error, please contact support."
    }


@app.post("/compliance/check-age-verified")
async def check_age_verified(request: LoginRequest):
    """Check if user has completed age verification"""
    email = request.email.lower().strip()
    verified = is_age_verified(email)
    return {
        "email": email,
        "age_verified": verified
    }


# OUTCOMES ENDPOINTS (admin only)

@app.get("/admin/outcomes/horse-performance")
async def get_horse_perf(authorization: Optional[str] = Header(None)):
    """Get horse performance summary (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    return {"horses": get_horse_performance()}


@app.get("/admin/outcomes/user-performance")
async def get_user_perf(authorization: Optional[str] = Header(None)):
    """Get user performance summary (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    return {"users": get_user_performance()}


@app.get("/admin/outcomes/report")
async def get_outcomes_report_endpoint(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_score: Optional[float] = 50.0,
    authorization: Optional[str] = Header(None)
):
    """Get outcomes report for date range (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    from datetime import datetime
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None

    return get_outcomes_report(start_date=start, end_date=end, min_score=min_score)


@app.get("/admin/outcomes/horse/{horse_name}")
async def get_horse_outcomes(horse_name: str, authorization: Optional[str] = Header(None)):
    """Get all outcomes for specific horse (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    return {"outcomes": get_outcomes_by_horse(horse_name)}


@app.post("/admin/outcomes/record")
async def record_outcome(
    race_id: str,
    horse_name: str,
    predicted_score: float,
    predicted_odds: float,
    actual_result: str,
    actual_odds: Optional[float] = None,
    payoff: Optional[float] = None,
    track: Optional[str] = None,
    race_num: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """Record prediction outcome (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    from datetime import datetime
    if record_prediction_outcome(
        race_id=race_id,
        horse_name=horse_name,
        predicted_score=predicted_score,
        predicted_odds=predicted_odds,
        prediction_date=datetime.now(),
        race_date=datetime.now(),
        actual_result=actual_result,
        actual_odds=actual_odds,
        payoff=payoff,
        track=track,
        race_num=race_num
    ):
        return {"success": True, "message": f"Outcome recorded for {horse_name} in race {race_id}"}
    return {"success": False, "message": "Failed to record outcome"}


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
    if remove_approved_user(remove_email):
        return {"message": f"User {remove_email} removed"}
    return {"message": "Failed to remove user"}


@app.get("/admin/users/all")
async def list_all_users(authorization: Optional[str] = Header(None)):
    """Get all users with their status (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    users = get_all_users()
    return {
        "users": [
            {
                "email": user_email,
                "approved": user_data.get("approved", False),
                "is_admin": user_data.get("is_admin", False) or user_email == "info@fm8.global",
                "created": user_data.get("created", "")
            }
            for user_email, user_data in users.items()
        ]
    }


@app.post("/admin/users/make-admin")
async def make_user_admin(request: UserManagement, authorization: Optional[str] = Header(None)):
    """Make user an admin (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    user_email = request.email.lower().strip()
    if make_admin(user_email):
        return {"message": f"User {user_email} is now an admin"}
    return {"message": "Failed to promote user", "error": "User not found"}


@app.post("/admin/users/remove-admin")
async def remove_user_admin(request: UserManagement, authorization: Optional[str] = Header(None)):
    """Remove admin privileges from user (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    user_email = request.email.lower().strip()
    if remove_admin(user_email):
        return {"message": f"Admin privileges removed from {user_email}"}
    return {"message": "Failed to remove admin privileges"}


@app.get("/admin/pending")
async def list_pending_requests(authorization: Optional[str] = Header(None)):
    """Get all pending access requests (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    return {"pending_requests": get_pending_requests()}


@app.post("/admin/pending/approve")
async def approve_pending_request(request: UserManagement, authorization: Optional[str] = Header(None)):
    """Approve a pending access request (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    user_email = request.email.lower().strip()
    if approve_request(user_email):
        return {"message": f"Access approved for {user_email}"}
    return {"message": "Failed to approve request", "error": "Request not found"}


@app.post("/admin/pending/reject")
async def reject_pending_request(request: UserManagement, authorization: Optional[str] = Header(None)):
    """Reject a pending access request (admin only)"""
    email = get_current_user(authorization)
    if not is_admin(email):
        raise HTTPException(status_code=403, detail="Admin access required")

    user_email = request.email.lower().strip()
    if reject_request(user_email):
        return {"message": f"Request rejected for {user_email}"}
    return {"message": "Failed to reject request"}


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
        with open(login_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>PunterEdge</h1><p>Login page not found. Visit /docs for API docs.</p>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
