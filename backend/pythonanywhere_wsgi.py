"""
ASGI-to-WSGI adapter for PythonAnywhere deployment.

This wrapper converts WSGI requests (from PythonAnywhere) to ASGI format
so FastAPI can properly handle them. The key fix for the 422 validation error
is properly buffering and streaming the request body through the ASGI
receive() callable.

Issue solved:
- PythonAnywhere is WSGI-only
- FastAPI is ASGI
- We need a reliable ASGI-to-WSGI adapter that properly handles JSON bodies
"""

import asyncio
import io
import sys
import os
from pathlib import Path

# Add your project directory to the sys.path
project_path = Path(__file__).parent.absolute()
if str(project_path) not in sys.path:
    sys.path.insert(0, str(project_path))

# Set environment variables before importing the app
os.environ.setdefault('API_KEY', 'c9edb4f8-4c7f-4a20-b0a5-edbac822e0ec')

# Import the FastAPI app
from main import app


def build_environ(environ, body):
    """
    Build an ASGI scope from WSGI environ.
    This converts the WSGI environment to the ASGI format FastAPI expects.

    Key fix: Properly convert headers, especially Content-Type which is critical
    for JSON parsing.
    """
    # Build headers list - convert from WSGI to ASGI format
    headers = []
    for key, value in environ.items():
        if key.startswith("HTTP_"):
            # Convert HTTP_HEADER_NAME to header-name
            header_name = key[5:].lower().replace("_", "-")
            headers.append((header_name.encode("latin1"), value.encode("latin1")))
        elif key == "CONTENT_TYPE":
            # Content-Type is a special case - no HTTP_ prefix in WSGI
            headers.append((b"content-type", value.encode("latin1")))
        elif key == "CONTENT_LENGTH":
            # Content-Length is also special
            headers.append((b"content-length", value.encode("latin1")))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": environ.get("SERVER_PROTOCOL", "HTTP/1.0").split("/")[1],
        "method": environ["REQUEST_METHOD"],
        "scheme": environ.get("wsgi.url_scheme", "http"),
        "path": environ.get("PATH_INFO", "/"),
        "query_string": environ.get("QUERY_STRING", "").encode("latin1"),
        "root_path": environ.get("SCRIPT_NAME", ""),
        "headers": headers,
        "server": (
            environ.get("SERVER_NAME", "localhost"),
            int(environ.get("SERVER_PORT", "80")),
        ),
        "client": None,
    }

    # Add client info if available
    if environ.get("REMOTE_ADDR"):
        scope["client"] = (environ["REMOTE_ADDR"], 0)

    return scope, body


class ASGItoWSGI:
    """
    ASGI-to-WSGI adapter that properly handles request bodies.

    This is the core fix: we buffer the entire request body upfront,
    then provide it through the ASGI receive() interface so FastAPI
    can properly parse JSON POST requests.
    """

    def __init__(self, asgi_app, executor=None):
        self.asgi_app = asgi_app
        self.executor = executor

    def __call__(self, environ, start_response):
        """
        WSGI application entry point.
        Receives WSGI environ and start_response, adapts to ASGI format.
        """
        # Read the entire request body upfront (this fixes the 422 error)
        body = b""
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        # Read body from wsgi.input
        if content_length > 0:
            wsgi_input = environ.get("wsgi.input")
            if wsgi_input is not None:
                body = wsgi_input.read(content_length)
                if not body and content_length > 0:
                    # If read returned empty but content_length > 0, wsgi.input may be at EOF
                    # Try to seek to beginning and read again
                    try:
                        wsgi_input.seek(0)
                        body = wsgi_input.read(content_length)
                    except (AttributeError, IOError):
                        # seek not supported or I/O error, use what we have
                        pass

        # Build ASGI scope
        scope, body_bytes = build_environ(environ, body)

        # Run the ASGI app
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response_started = False
            status = "500 Internal Server Error"
            response_headers = []
            response_body = []
            body_sent = False

            async def receive():
                """
                ASGI receive callable that provides the request body.
                This is critical for JSON POST requests - it provides the body data.
                Called by FastAPI to read the request body.
                """
                nonlocal body_sent

                if not body_sent:
                    body_sent = True
                    # Return the complete request body with more_body=False
                    # This tells FastAPI/Pydantic that all data is available
                    return {
                        "type": "http.request",
                        "body": body_bytes,
                        "more_body": False,
                    }
                else:
                    # Subsequent calls return empty body
                    return {
                        "type": "http.request",
                        "body": b"",
                        "more_body": False,
                    }

            async def send(message):
                """
                ASGI send callable that collects response data.
                """
                nonlocal response_started, status, response_headers, response_body

                if message["type"] == "http.response.start":
                    response_started = True
                    status = f"{message['status']} {_get_status_text(message['status'])}"
                    response_headers = [
                        (name.decode() if isinstance(name, bytes) else name,
                         value.decode() if isinstance(value, bytes) else value)
                        for name, value in message.get("headers", [])
                    ]

                elif message["type"] == "http.response.body":
                    body_part = message.get("body", b"")
                    if body_part:
                        response_body.append(body_part)

            # Run the ASGI app
            loop.run_until_complete(self.asgi_app(scope, receive, send))

            # Start the WSGI response
            start_response(status, response_headers)

            # Return the response body
            return response_body if response_body else [b""]

        except Exception as e:
            # Error handling - log the error for debugging
            import traceback
            error_message = f"Internal Server Error: {str(e)}\n{traceback.format_exc()}"
            status = "500 Internal Server Error"
            start_response(status, [("Content-Type", "text/plain")])
            return [error_message.encode()]

        finally:
            loop.close()


def _get_status_text(status_code):
    """Get HTTP status text from status code."""
    status_codes = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
    }
    return status_codes.get(status_code, "Unknown")


# Create the WSGI application
application = ASGItoWSGI(app)
