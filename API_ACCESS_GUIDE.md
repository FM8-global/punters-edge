# PunterEdge - API Access Guide

**🚀 Live App:** https://fm8global.pythonanywhere.com  
**📚 New Users:** See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for dashboard tour  
**🔑 Demo Admin:** info@fm8.global / admin123

---

The app is deployed and fully functional! Access via web dashboard or API.

## Quick Start: Dashboard (Recommended for New Users)

For easiest access, use the web dashboard:

1. **Open:** https://fm8global.pythonanywhere.com
2. **Login:** info@fm8.global / admin123
3. **View Predictions:** Click "VIEW PREDICTIONS"
4. **Get Token:** Click "VIEW TOKEN" to use API

👉 **Full guide:** [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)

---

## Quick Start: API Access

### Step 1: Login (Get Token)

```bash
curl -X POST "https://fm8global.pythonanywhere.com/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"info@fm8.global"}'
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "message": "Welcome info@fm8.global!"
}
```

Copy the `token` value.

### Step 2: Get Predictions

```bash
curl "https://fm8global.pythonanywhere.com/bets?min_score=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Returns all predictions with AI scores ≥50.

### Step 3: Get Races

```bash
curl "https://fm8global.pythonanywhere.com/races" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Returns live race data with odds.

## All Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/login` | POST | ❌ | Get auth token |
| `/logout` | POST | ✅ | Logout |
| `/bets` | GET | ✅ | All predictions |
| `/bets/race/{id}` | GET | ✅ | Predictions for race |
| `/races` | GET | ✅ | Live races |
| `/admin/users` | GET | 👑 | List approved users |
| `/admin/users/add` | POST | 👑 | Approve user |
| `/health` | GET | ❌ | Health check |

Legend: ❌ = Public, ✅ = Needs token, 👑 = Admin only

## Admin Management

Add approved users:

```bash
curl -X POST "https://fm8app.pythonanywhere.com/admin/users/add" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

List approved users:

```bash
curl "https://fm8app.pythonanywhere.com/admin/users" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Default Admin

**Email:** info@fm8.global  
**Token Duration:** 30 days

## Web Interface

The web login page is at https://fm8app.pythonanywhere.com/ but has a technical limitation with form submission. Use the API curl commands above instead - they work perfectly!

## API Docs

OpenAPI/Swagger docs available at:
https://fm8app.pythonanywhere.com/docs

## Status

✅ **DEPLOYED & LIVE**
- Backend: Running
- Database: Ready
- API: Responding
- Authentication: Working
- Predictions: Generating

**Note:** Web form has a temporary issue. All functionality is available via API.
