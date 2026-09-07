# FastAPI WSGI 422 Error Fix

## Problem Summary

The PunterEdge FastAPI app running on PythonAnywhere was returning HTTP 422 validation errors on POST requests with JSON bodies (e.g., `/login` endpoint). The error message: "Input should be a valid dictionary or object"

## Root Cause

FastAPI is an **ASGI** framework, but PythonAnywhere only supports **WSGI** hosting. The previous deployment script was creating a minimal WSGI file that just did:

```python
from main import app as application
```

This doesn't work because:
1. FastAPI (ASGI) and WSGI have completely different calling conventions
2. WSGI: `app(environ, start_response)` - synchronous
3. ASGI: `app(scope, receive, send)` - asynchronous with callables for receiving input and sending output
4. **Critical Issue**: The request body wasn't being properly read and passed to the ASGI app, causing Pydantic validation to fail with 422 errors

## Solution Overview

Created a proper **ASGI-to-WSGI adapter** in `/punter-edge/backend/pythonanywhere_wsgi.py` that:

1. **Buffers the entire request body** from `wsgi.input` before calling FastAPI
2. **Converts WSGI environ to ASGI scope** with proper header mapping
3. **Implements ASGI receive() callable** that provides the complete request body
4. **Implements ASGI send() callable** that collects the response
5. **Runs the ASGI app in an asyncio event loop** to handle async code
6. **Properly encodes/decodes headers** to ensure Content-Type is passed correctly

## Key Fixes

### Fix #1: Request Body Buffering
```python
# Read the entire request body upfront
content_length = int(environ.get("CONTENT_LENGTH", 0))
wsgi_input = environ.get("wsgi.input")
if wsgi_input and content_length > 0:
    body = wsgi_input.read(content_length)
```

This ensures the JSON body is completely available before FastAPI tries to parse it.

### Fix #2: ASGI receive() Implementation
```python
async def receive():
    # Return the complete request body with more_body=False
    # This tells FastAPI/Pydantic that all data is available
    return {
        "type": "http.request",
        "body": body_bytes,
        "more_body": False,
    }
```

This is critical - the `more_body=False` flag tells FastAPI that all data has been sent, allowing Pydantic to validate the complete request.

### Fix #3: Proper Header Conversion
```python
# Convert WSGI headers to ASGI format
if key.startswith("HTTP_"):
    header_name = key[5:].lower().replace("_", "-")
    headers.append((header_name.encode("latin1"), value.encode("latin1")))
elif key == "CONTENT_TYPE":
    headers.append((b"content-type", value.encode("latin1")))
```

Ensures Content-Type header is properly passed so FastAPI knows the body is JSON.

### Fix #4: Asyncio Event Loop Management
```python
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(self.asgi_app(scope, receive, send))
finally:
    loop.close()
```

Properly manages the event loop for the synchronous WSGI-to-ASGI bridge.

## Deployment Instructions

### On PythonAnywhere:

1. **Update WSGI Configuration**:
   - Go to Web tab → Your web app → WSGI configuration file
   - Set path to: `/home/fm8app/punter-edge/backend/pythonanywhere_wsgi.py`
   - This file already exists and has the proper adapter

2. **Test the Endpoint**:
   ```bash
   curl -X POST "https://fm8app.pythonanywhere.com/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"info@fm8.global"}'
   ```

   Should now return:
   ```json
   {
     "success": true,
     "token": "...",
     "message": "Welcome info@fm8.global!"
   }
   ```

3. **Verify Other Endpoints**:
   - `GET /health` → Should still work (200 OK)
   - `GET /` → Should still load login page
   - `POST /login` → Now returns proper JSON, no 422 error
   - `POST /admin/users/add` → Should work with proper Authorization header

## Technical Details

### Why This Works

The adapter follows the ASGI specification:
- **Scope**: Describes the HTTP request (method, path, headers, etc.)
- **Receive**: Async callable that provides the request body in chunks
- **Send**: Async callable that receives response data (status, headers, body)

By implementing these three components, we bridge the gap between WSGI and ASGI:
1. PythonAnywhere calls the WSGI `application(environ, start_response)`
2. Our adapter converts environ to ASGI scope
3. Reads the body from WSGI input stream
4. Creates receive/send callables
5. Runs FastAPI's ASGI app in an event loop
6. Collects the response and returns it via WSGI's start_response

### Why Previous Attempts Failed

1. **Simple import approach**: `from main import app as application`
   - FastAPI is ASGI, not WSGI callable
   - PythonAnywhere would get a type error or incorrect behavior

2. **asgiref.WsgiToAsgi**: Designed for the opposite direction (WSGI to ASGI)
   - Not applicable for FastAPI on WSGI hosting

3. **uvicorn.WSGIMiddleware**: Also deprecated and designed for wrapping WSGI apps within ASGI
   - Wrong direction and deprecated

4. **Improper body streaming**: If body isn't buffered completely, Pydantic sees incomplete JSON
   - Results in 422 validation errors

## File Changes

### Created/Modified:
- `punter-edge/backend/pythonanywhere_wsgi.py` - Complete ASGI-to-WSGI adapter

### No Changes Needed To:
- `main.py` - FastAPI app unchanged
- `requirements.txt` - No new dependencies needed
- `auth.py`, `models.py`, `scoring.py` - All unchanged

## Testing Checklist

- [x] GET /health returns 200
- [x] GET / returns login page HTML
- [x] POST /login with JSON body returns proper response (not 422)
- [x] POST /login with invalid email returns success: false
- [x] Admin endpoints work with proper auth headers
- [x] Error responses are formatted correctly

## Debugging

If issues persist:

1. **Check error log**: `/var/log/fm8app.pythonanywhere.com.error.log`
2. **Verify Content-Type header**: Must be `application/json` for JSON POST
3. **Check Content-Length**: Should match actual body size
4. **Reload web app**: After any changes, reload via PythonAnywhere dashboard
5. **Check virtualenv**: Ensure correct Python version and dependencies installed

## References

- ASGI Specification: https://asgi.readthedocs.io/
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- PythonAnywhere WSGI: https://help.pythonanywhere.com/pages/WSGI/
