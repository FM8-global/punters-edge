# E2E Testing Guide for PunterEdge

This guide explains how to run comprehensive End-to-End tests for the PunterEdge application.

## Overview

The E2E test suite validates:
- ✅ Admin and user authentication
- ✅ Dashboard functionality
- ✅ Predictions section
- ✅ Outcomes section
- ✅ Session persistence
- ✅ Error handling
- ✅ Console for JavaScript errors

## Prerequisites

1. **Python 3.7+** installed
2. **Chrome/Chromium browser** installed (for Selenium WebDriver)
3. **Application running** at the test URL (default: http://localhost:8000)

## Quick Start

### Method 1: Using the Test Runner Script (Recommended)

```bash
# Navigate to project directory
cd punter-edge

# Make script executable
chmod +x run_e2e_tests.sh

# Run tests against local server
./run_e2e_tests.sh

# Run tests against remote server
./run_e2e_tests.sh --url https://your-app.railway.app

# Run tests in headless mode (no browser window)
./run_e2e_tests.sh --url https://your-app.railway.app --headless

# Run with custom credentials
./run_e2e_tests.sh --url http://localhost:8000 \
    --admin-email your-email@example.com \
    --admin-password your-password
```

### Method 2: Direct Python Execution

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
python3 e2e_test_automated.py --url http://localhost:8000

# Run with headless browser
python3 e2e_test_automated.py --url http://localhost:8000 --headless

# Run against production
python3 e2e_test_automated.py --url https://your-app.railway.app --headless
```

## Test Cases

The test suite includes the following test cases:

### T0: Page Loads
- Verifies the login page loads successfully
- Checks that input elements are present

### T1: Admin Login
- Tests admin authentication with email and password
- Verifies redirect to dashboard
- Checks session token storage

### T2: Session Persistence
- Tests that session persists after page reload
- Verifies token is retained in localStorage
- Ensures user remains logged in

### T3: Dashboard Loads
- Verifies dashboard renders
- Checks for Predictions and Outcomes sections
- Confirms page structure

### T4: Predictions Section
- Tests predictions data loads
- Verifies section is visible and accessible
- Checks for data or empty state

### T5: Outcomes Section
- Tests outcomes data loads
- Verifies section is visible and accessible
- Checks for data or empty state

### T6: Console Errors
- Scans browser console for JavaScript errors
- Reports any SEVERE level errors

### T7: Logout Clears Session
- Tests logout functionality
- Verifies session token is cleared
- Checks redirect to login page

### T8: Invalid Credentials Rejected
- Tests login with wrong password
- Verifies error message is shown
- Confirms user is not authenticated

### T9: Page Responsive
- Tests page has content and is usable
- Verifies elements are present and visible

## Test Users

By default, the test suite uses:
- **Admin Email:** `info@fm8.global`
- **Admin Password:** `admin123`

You can override these with command-line arguments:
```bash
./run_e2e_tests.sh --admin-email your@email.com --admin-password yourpass
```

## Understanding Test Output

### Successful Test
```
✓ T1: Admin Login: PASS
```

### Failed Test
```
✗ T1: Admin Login: FAIL Dashboard not loaded
```

### Test Summary
```
============================================================
TEST SUMMARY
============================================================

Total Tests: 10
✓ Passed: 10
✗ Failed: 0
Pass Rate: 100.0%

============================================================
```

## CI/CD Integration

To integrate E2E tests into your CI/CD pipeline:

### GitHub Actions Example
```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r punter-edge/requirements.txt
          pip install -r punter-edge/requirements-test.txt
      
      - name: Start app
        run: |
          cd punter-edge
          python backend/main.py &
          sleep 5
      
      - name: Run E2E tests
        run: cd punter-edge && ./run_e2e_tests.sh --headless
```

## Troubleshooting

### "Chrome driver not found"
Install webdriver-manager or download ChromeDriver manually.

### "Connection refused"
Ensure the application is running at the specified URL. Check:
```bash
curl -I http://localhost:8000
```

### "Invalid credentials"
Verify the admin email and password are correct. Check if test user exists in the database.

### "Element not found"
Wait times may be too short. Increase timeout in the test script (currently 10 seconds).

### "JavaScript console errors"
Check the test output for specific error messages. These may indicate issues in the frontend code that need fixing before deployment.

## Running Against Different Environments

### Local Development
```bash
./run_e2e_tests.sh --url http://localhost:8000
```

### Staging
```bash
./run_e2e_tests.sh --url https://staging.your-app.com --headless
```

### Production
```bash
./run_e2e_tests.sh --url https://your-app.railway.app --headless
```

## Best Practices

1. **Always run before deployment** - Catch issues before production
2. **Use headless mode in CI/CD** - Faster execution without GUI
3. **Test with real data** - Use actual test accounts, not mocks
4. **Check console errors** - JavaScript errors often indicate problems
5. **Monitor response times** - Note if tests slow down unexpectedly
6. **Keep test data clean** - Reset test users between test runs if needed

## Advanced Usage

### Custom Test Timeout
Edit `e2e_test_automated.py` and change the timeout values:
```python
WebDriverWait(self.driver, 20)  # 20 second timeout
```

### Extend Tests
Add new test methods to the `E2ETestRunner` class:
```python
def test_custom_feature(self):
    """T10: Custom feature test."""
    try:
        # Your test code here
        self.log_result("T10: Custom Feature", "PASS")
        return True
    except Exception as e:
        self.log_result("T10: Custom Feature", "FAIL", str(e))
        return False
```

### Screenshot on Failure
Add to tests that fail:
```python
self.driver.save_screenshot(f"failure_{int(time.time())}.png")
```

## Production Readiness Checklist

Before deploying to production, ensure:
- [ ] All E2E tests passing (100% pass rate)
- [ ] No JavaScript errors in console
- [ ] Admin login works
- [ ] Dashboard loads all sections
- [ ] Predictions display correctly
- [ ] Outcomes display correctly
- [ ] Session persists across reloads
- [ ] Logout clears session properly
- [ ] Invalid credentials are rejected
- [ ] Response times are acceptable

## Getting Help

If tests fail:
1. Check the error message output
2. Run in non-headless mode to see browser behavior: `python3 e2e_test_automated.py --url http://localhost:8000`
3. Check browser console for errors: Press F12 in the browser
4. Review application logs
5. Check network requests in DevTools (F12 → Network tab)

## Next Steps

Once E2E tests pass:
1. Deploy to production
2. Monitor application logs
3. Run tests weekly to catch regressions
4. Add new tests for new features
5. Update test data as needed
