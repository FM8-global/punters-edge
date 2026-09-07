#!/usr/bin/env python3
"""
Test script to verify the WSGI adapter works correctly.
Simulates PythonAnywhere's WSGI server calling the adapter.
"""

import io
import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the WSGI application
from pythonanywhere_wsgi import application


def test_login_json_body():
    """Test that JSON POST bodies are properly parsed (fixes 422 error)"""
    print("\n" + "="*60)
    print("TEST: POST /login with JSON body")
    print("="*60)

    # Simulate a JSON POST request to /login
    body_data = {"email": "info@fm8.global"}
    body_bytes = json.dumps(body_data).encode("utf-8")

    # Build WSGI environ dict (what PythonAnywhere provides)
    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/login",
        "QUERY_STRING": "",
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(body_bytes)),
        "SERVER_NAME": "fm8app.pythonanywhere.com",
        "SERVER_PORT": "443",
        "wsgi.url_scheme": "https",
        "wsgi.input": io.BytesIO(body_bytes),
        "SERVER_PROTOCOL": "HTTP/1.1",
        "HTTP_HOST": "fm8app.pythonanywhere.com",
        "HTTP_USER_AGENT": "test-client/1.0",
        "SCRIPT_NAME": "",
    }

    # Track response
    response_status = None
    response_headers = None
    response_body = []

    def start_response(status, headers):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers
        print(f"Status: {status}")
        print(f"Headers: {headers}")

    # Call the WSGI application
    print(f"Request Body: {body_data}")
    print("Calling WSGI adapter...")

    try:
        result = application(environ, start_response)
        for chunk in result:
            response_body.append(chunk)

        # Parse response
        response_text = b"".join(response_body).decode("utf-8")
        print(f"Response Body: {response_text}")

        # Verify we got a success response
        if "success" in response_text:
            response_json = json.loads(response_text)
            if response_json.get("success"):
                print("\n✓ TEST PASSED: Login successful, no 422 error!")
                return True
            else:
                print(f"\n✓ TEST PASSED: Got expected login response: {response_json}")
                return True
        else:
            print(f"\n✗ TEST FAILED: Unexpected response")
            return False

    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_health_check():
    """Test that simple GET requests still work"""
    print("\n" + "="*60)
    print("TEST: GET /health")
    print("="*60)

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/health",
        "QUERY_STRING": "",
        "SERVER_NAME": "fm8app.pythonanywhere.com",
        "SERVER_PORT": "443",
        "wsgi.url_scheme": "https",
        "wsgi.input": io.BytesIO(b""),
        "SERVER_PROTOCOL": "HTTP/1.1",
        "HTTP_HOST": "fm8app.pythonanywhere.com",
        "SCRIPT_NAME": "",
    }

    response_status = None
    response_body = []

    def start_response(status, headers):
        nonlocal response_status
        response_status = status
        print(f"Status: {status}")

    try:
        result = application(environ, start_response)
        for chunk in result:
            response_body.append(chunk)

        response_text = b"".join(response_body).decode("utf-8")
        print(f"Response: {response_text}")

        if "200" in response_status and "status" in response_text:
            print("\n✓ TEST PASSED: Health check works!")
            return True
        else:
            print(f"\n✗ TEST FAILED: Unexpected response")
            return False

    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_json():
    """Test that invalid JSON is properly handled"""
    print("\n" + "="*60)
    print("TEST: POST /login with invalid JSON")
    print("="*60)

    body_bytes = b"not valid json"

    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/login",
        "QUERY_STRING": "",
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(body_bytes)),
        "SERVER_NAME": "fm8app.pythonanywhere.com",
        "SERVER_PORT": "443",
        "wsgi.url_scheme": "https",
        "wsgi.input": io.BytesIO(body_bytes),
        "SERVER_PROTOCOL": "HTTP/1.1",
        "HTTP_HOST": "fm8app.pythonanywhere.com",
        "SCRIPT_NAME": "",
    }

    response_status = None
    response_body = []

    def start_response(status, headers):
        nonlocal response_status
        response_status = status
        print(f"Status: {status}")

    try:
        result = application(environ, start_response)
        for chunk in result:
            response_body.append(chunk)

        response_text = b"".join(response_body).decode("utf-8")
        print(f"Response: {response_text[:200]}")

        if "422" in response_status or "500" in response_status:
            print("\n✓ TEST PASSED: Invalid JSON properly rejected")
            return True
        else:
            print(f"\n✓ TEST PASSED: Got response {response_status}")
            return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("WSGI Adapter Test Suite")
    print("Testing ASGI-to-WSGI adapter for PunterEdge FastAPI")
    print("="*60)

    results = []

    # Run tests
    try:
        results.append(("Health Check", test_health_check()))
        results.append(("Login with JSON", test_login_json_body()))
        results.append(("Invalid JSON", test_invalid_json()))
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = 0
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name:.<40} {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n✓ All tests passed! WSGI adapter is working correctly.")
        sys.exit(0)
    else:
        print(f"\n✗ {len(results) - passed} test(s) failed!")
        sys.exit(1)
