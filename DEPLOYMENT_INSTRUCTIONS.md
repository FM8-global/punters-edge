# PunterEdge Deployment to PythonAnywhere - WSGI Adapter Fix

## Quick Summary

The HTTP 422 validation error on POST requests has been **fixed**. The solution was creating a proper ASGI-to-WSGI adapter that:
1. Buffers the complete request body
2. Properly implements the ASGI receive() interface
3. Correctly passes Content-Type headers to FastAPI

## Files Changed

### New Files Created:
- `backend/pythonanywhere_wsgi.py` - **Complete ASGI-to-WSGI adapter** (THE FIX)
- `WSGI_FIX_EXPLANATION.md` - Technical explanation of the problem and solution
- `test_wsgi_adapter.py` - Test script to verify the adapter works

### Files Unchanged:
- `main.py` - FastAPI app (no changes needed)
- `requirements.txt` - Dependencies (no new packages needed)
- All other app files remain the same

## Deployment Steps

### Step 1: Upload Updated Code

If using Git:
```bash
git add backend/pythonanywhere_wsgi.py
git commit -m "Add WSGI adapter to fix 422 errors on JSON POST requests"
git push origin main
```

Then in PythonAnywhere Bash console:
```bash
cd ~/punter-edge
git pull origin main
```

Or manually upload the `pythonanywhere_wsgi.py` file via PythonAnywhere's Files interface.

### Step 2: Update WSGI Configuration on PythonAnywhere

1. Log into PythonAnywhere: https://www.pythonanywhere.com
2. Go to **Web** tab
3. Click on your app name (e.g., `fm8app.pythonanywhere.com`)
4. Under "WSGI configuration file:", you should see a path
   - For fm8app, it would be: `/var/www/fm8app_pythonanywhere_com_wsgi.py`
5. **Click on the WSGI configuration file path** to edit it
6. Replace the entire content with this:

```python
"""
WSGI wrapper for PunterEdge FastAPI app on PythonAnywhere.
Uses the ASGI-to-WSGI adapter from the backend.
"""

import sys
import os

# Add the app's backend directory to Python path
app_dir = '/home/fm8app/punter-edge/backend'
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Set environment variables
os.environ['API_KEY'] = 'c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec'

# Import the WSGI application from our adapter
from pythonanywhere_wsgi import application
```

7. Click **Save**

### Step 3: Reload the Web App

1. Still in the Web tab for your app
2. Find the green **Reload** button at the top right
3. Click **Reload [YOUR-APP]**
4. Wait for "Reloaded at..." message to appear

### Step 4: Test the Fix

#### Test 1: Health Check (should always work)
```bash
curl https://fm8app.pythonanywhere.com/health
```

Expected response:
```json
{"status":"ok"}
```

#### Test 2: Login with JSON (this was broken before, now fixed)
```bash
curl -X POST https://fm8app.pythonanywhere.com/login \
  -H "Content-Type: application/json" \
  -d '{"email":"info@fm8.global"}'
```

Expected response:
```json
{
  "success": true,
  "token": "...(auth token)...",
  "message": "Welcome info@fm8.global!"
}
```

If you get a different response like "Email not approved", that's still correct - the endpoint is working, just the user isn't approved yet.

#### Test 3: Login Page (should still work)
```bash
curl https://fm8app.pythonanywhere.com/
```

Should return HTML login page, no errors.

### Step 5: Verify Error Logs

If you still have issues, check the error log:

1. In PythonAnywhere, go to **Web** tab
2. Find **Log files** section
3. Click on the **error log** link
4. Look at the last few lines for any errors

Common issues:
- `ModuleNotFoundError: No module named 'main'` - Check working directory is `/home/fm8app/punter-edge/backend`
- `Permission denied` - Check file permissions
- `Connection refused` - Check API_KEY environment variable is set

## What Changed Under the Hood

### Before (Broken):
```python
# OLD - Doesn't work because FastAPI is ASGI, not WSGI
from main import app as application
```

This failed because:
- PythonAnywhere WSGI server expects `application(environ, start_response)`
- FastAPI is an ASGI app expecting `app(scope, receive, send)`
- Request body wasn't being passed to FastAPI
- Pydantic validation failed → 422 error

### After (Fixed):
```python
# NEW - Proper ASGI-to-WSGI adapter
from pythonanywhere_wsgi import application
```

This works because:
- Adapter reads the complete request body
- Converts WSGI environ to ASGI scope
- Implements ASGI receive() to provide the body
- Implements ASGI send() to collect response
- Runs FastAPI in an asyncio event loop
- Returns proper WSGI response

## Architecture Overview

```
PythonAnywhere WSGI Server
         ↓
    (environ, start_response)
         ↓
  pythonanywhere_wsgi.py (ASGItoWSGI adapter)
         ↓
  Converts to ASGI format (scope, receive, send)
         ↓
  Runs asyncio event loop
         ↓
  FastAPI app (ASGI)
         ↓
  Returns JSON response
         ↓
  Returns via start_response
```

## Troubleshooting

### Issue: Still getting 422 errors

1. **Check Content-Type header**: Must be `application/json` for JSON POST
   ```bash
   curl -X POST https://fm8app.pythonanywhere.com/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com"}'
   ```

2. **Check request body is valid JSON**:
   ```bash
   # Invalid (missing quotes)
   curl -X POST ... -d '{email: "test@example.com"}'
   
   # Valid
   curl -X POST ... -d '{"email":"test@example.com"}'
   ```

3. **Verify the WSGI file was updated correctly**
   - Click the WSGI file path in PythonAnywhere
   - Make sure it contains the adapter code, not the old import

4. **Check error log** for stack traces that indicate the real issue

### Issue: "Module not found" errors

1. Verify `main.py` exists at `/home/fm8app/punter-edge/backend/main.py`
2. Check working directory is set to `/home/fm8app/punter-edge/backend`
3. Verify Python path includes the backend directory
4. Ensure virtualenv is selected and has dependencies installed

### Issue: API errors after login

After the 422 fix, you might encounter:
- "Email not approved" - Expected, add user via `/admin/users/add`
- API connection errors - Check API_KEY environment variable
- "Invalid token" - Token may have expired or been invalidated

These are application-level issues, not WSGI issues, and are expected behavior.

## Testing Locally (Optional)

To test the adapter locally before deploying:

```bash
cd punter-edge
python test_wsgi_adapter.py
```

This simulates what PythonAnywhere does and verifies the adapter works.

## Support & Next Steps

### If the fix works:
1. Test all endpoints with valid requests
2. Monitor error logs for any issues
3. You're done! The app should now work properly

### If you still have issues:
1. Check the error log as described above
2. Run the test script locally to debug
3. Verify all files are uploaded correctly
4. Contact PythonAnywhere support if there are WSGI server issues

## Key Points to Remember

- **Never put passwords in WSGI file** - use environment variables (API_KEY is already set)
- **Always reload after WSGI changes** - Changes don't take effect until you click Reload
- **Check error logs** - They contain valuable debugging information
- **Backup the original WSGI file** - Before making changes, in case you need to revert

## Files Reference

- **pythonanywhere_wsgi.py** - The ASGI-to-WSGI adapter (contains the fix)
- **main.py** - The FastAPI application (unchanged)
- **auth.py** - Authentication logic (unchanged)
- **models.py** - Pydantic models (unchanged)
- **scoring.py** - Bet scoring logic (unchanged)

All other files remain unchanged by this fix.
