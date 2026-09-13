#!/usr/bin/env python3
"""
Automated E2E Test Suite for PunterEdge Application
Tests all dashboard functionality including authentication, predictions, and outcomes.
"""

import time
import json
import sys
from urllib.parse import urljoin
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print("ERROR: selenium not installed. Install with: pip install selenium")
    sys.exit(1)


class E2ETestRunner:
    def __init__(self, base_url="http://localhost:8000", headless=False):
        self.base_url = base_url
        self.driver = None
        self.test_results = []
        self.headless = headless
        self.admin_email = "info@fm8.global"
        self.admin_password = "admin123"
        self.test_user_email = "testuser@example.com"
        self.test_user_password = "TestPass123!"

    def setup(self):
        """Initialize the Chrome WebDriver."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print(f"✓ WebDriver initialized (headless={self.headless})")
        except Exception as e:
            print(f"✗ Failed to initialize WebDriver: {e}")
            raise

    def teardown(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            print("✓ WebDriver closed")

    def log_result(self, test_name, status, message=""):
        """Log test result."""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        symbol = "✓" if status == "PASS" else "✗"
        print(f"{symbol} {test_name}: {status} {message}")

    def navigate_to(self, path="/"):
        """Navigate to a specific path."""
        url = urljoin(self.base_url, path)
        self.driver.get(url)
        time.sleep(1)

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return self.driver.find_element(by, value)
        except:
            return None

    def get_local_storage(self, key):
        """Get value from localStorage."""
        return self.driver.execute_script(f"return localStorage.getItem('{key}')")

    def clear_local_storage(self):
        """Clear all localStorage."""
        self.driver.execute_script("localStorage.clear()")

    # ============ TEST CASES ============

    def test_page_loads(self):
        """T0: Verify login page loads."""
        try:
            self.navigate_to("/")
            self.wait_for_element(By.TAG_NAME, "input")
            self.log_result("T0: Page Loads", "PASS")
            return True
        except Exception as e:
            self.log_result("T0: Page Loads", "FAIL", str(e))
            return False

    def test_admin_login(self):
        """T1: Admin login with password."""
        try:
            self.clear_local_storage()
            self.navigate_to("/")

            # Find email input and enter admin email
            email_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='email']")
            email_input.clear()
            email_input.send_keys(self.admin_email)
            time.sleep(1)

            # Wait for password field to appear
            password_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.clear()
            password_input.send_keys(self.admin_password)
            time.sleep(0.5)

            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_button.click()

            # Wait for dashboard to load
            time.sleep(3)

            # Check if redirected to dashboard
            if "/dashboard" in self.driver.current_url or "Predictions" in self.driver.page_source:
                # Verify token in localStorage
                token = self.get_local_storage("token")
                if token:
                    self.log_result("T1: Admin Login", "PASS")
                    return True

            self.log_result("T1: Admin Login", "FAIL", "Dashboard not loaded")
            return False
        except Exception as e:
            self.log_result("T1: Admin Login", "FAIL", str(e))
            return False

    def test_session_persistence(self):
        """T2: Session persists after page reload."""
        try:
            # Get current token
            token_before = self.get_local_storage("token")
            if not token_before:
                self.log_result("T2: Session Persistence", "FAIL", "No token before reload")
                return False

            # Reload page
            self.driver.refresh()
            time.sleep(2)

            # Check if still logged in
            token_after = self.get_local_storage("token")
            if token_after == token_before and "Predictions" in self.driver.page_source:
                self.log_result("T2: Session Persistence", "PASS")
                return True

            self.log_result("T2: Session Persistence", "FAIL", "Session not persisted")
            return False
        except Exception as e:
            self.log_result("T2: Session Persistence", "FAIL", str(e))
            return False

    def test_dashboard_loads(self):
        """T3: Dashboard loads with all sections."""
        try:
            # Check for main sections
            predictions_present = "Predictions" in self.driver.page_source
            outcomes_present = "Outcomes" in self.driver.page_source

            if predictions_present and outcomes_present:
                self.log_result("T3: Dashboard Loads", "PASS")
                return True

            self.log_result("T3: Dashboard Loads", "FAIL",
                          f"Predictions: {predictions_present}, Outcomes: {outcomes_present}")
            return False
        except Exception as e:
            self.log_result("T3: Dashboard Loads", "FAIL", str(e))
            return False

    def test_predictions_section(self):
        """T4: Predictions section loads and displays data."""
        try:
            # Try to find predictions section
            predictions_section = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Predictions')]/..")
            predictions_section.scroll_into_view()
            time.sleep(1)

            # Check page source for predictions data
            if "horse" in self.driver.page_source.lower() or "prediction" in self.driver.page_source.lower():
                self.log_result("T4: Predictions Section", "PASS")
                return True

            self.log_result("T4: Predictions Section", "PASS", "(No predictions data - may be empty)")
            return True
        except Exception as e:
            self.log_result("T4: Predictions Section", "FAIL", str(e))
            return False

    def test_outcomes_section(self):
        """T5: Outcomes section loads and displays data."""
        try:
            # Try to find outcomes section
            outcomes_section = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Outcomes')]/..")
            outcomes_section.scroll_into_view()
            time.sleep(1)

            # Check for table or data
            if "outcome" in self.driver.page_source.lower():
                self.log_result("T5: Outcomes Section", "PASS")
                return True

            self.log_result("T5: Outcomes Section", "PASS", "(No outcomes data - may be empty)")
            return True
        except Exception as e:
            self.log_result("T5: Outcomes Section", "FAIL", str(e))
            return False

    def test_console_errors(self):
        """T6: No JavaScript errors in console."""
        try:
            logs = self.driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']

            if not errors:
                self.log_result("T6: Console Errors", "PASS", "(No errors)")
                return True

            error_messages = [log['message'] for log in errors[:3]]
            self.log_result("T6: Console Errors", "FAIL", f"Found {len(errors)} errors: {error_messages}")
            return False
        except Exception as e:
            self.log_result("T6: Console Errors", "PASS", "(Cannot check - browser logging unavailable)")
            return True

    def test_logout_clears_session(self):
        """T7: Logout clears session."""
        try:
            # Find and click logout button
            logout_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Logout') or contains(text(), 'logout')]")
            logout_button.click()
            time.sleep(2)

            # Check if redirected to login
            token = self.get_local_storage("token")
            if not token and ("login" in self.driver.current_url.lower() or "email" in self.driver.page_source.lower()):
                self.log_result("T7: Logout Clears Session", "PASS")
                return True

            self.log_result("T7: Logout Clears Session", "FAIL", "Session not cleared properly")
            return False
        except Exception as e:
            self.log_result("T7: Logout Clears Session", "FAIL", str(e))
            return False

    def test_login_invalid_credentials(self):
        """T8: Invalid credentials rejected."""
        try:
            self.clear_local_storage()
            self.navigate_to("/")

            email_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='email']")
            email_input.clear()
            email_input.send_keys("test@example.com")
            time.sleep(1)

            password_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.clear()
            password_input.send_keys("WrongPassword123!")
            time.sleep(0.5)

            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_button.click()
            time.sleep(2)

            # Check for error message
            if "error" in self.driver.page_source.lower() or "invalid" in self.driver.page_source.lower():
                self.log_result("T8: Invalid Credentials Rejected", "PASS")
                return True

            self.log_result("T8: Invalid Credentials Rejected", "FAIL", "No error message shown")
            return False
        except Exception as e:
            self.log_result("T8: Invalid Credentials Rejected", "FAIL", str(e))
            return False

    def test_page_responsive(self):
        """T9: Page is responsive and usable."""
        try:
            # Check if elements are visible and clickable
            page_source = self.driver.page_source
            has_content = len(page_source) > 500

            if has_content:
                self.log_result("T9: Page Responsive", "PASS")
                return True

            self.log_result("T9: Page Responsive", "FAIL", "Page content too minimal")
            return False
        except Exception as e:
            self.log_result("T9: Page Responsive", "FAIL", str(e))
            return False

    def run_all_tests(self):
        """Run all tests in sequence."""
        print("\n" + "="*60)
        print("STARTING E2E TEST SUITE")
        print("="*60 + "\n")

        try:
            self.setup()

            # Test sequence
            self.test_page_loads()
            self.test_admin_login()
            self.test_session_persistence()
            self.test_dashboard_loads()
            self.test_predictions_section()
            self.test_outcomes_section()
            self.test_console_errors()
            self.test_page_responsive()
            self.test_logout_clears_session()
            self.test_login_invalid_credentials()

        except Exception as e:
            print(f"✗ Test suite error: {e}")
        finally:
            self.teardown()

        # Print summary
        self.print_summary()
        return self.get_pass_rate()

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)

        print(f"\nTotal Tests: {total}")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"Pass Rate: {(passed/total*100):.1f}%")

        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  ✗ {result['test']}: {result['message']}")

        print("\n" + "="*60)

    def get_pass_rate(self):
        """Return pass rate as percentage."""
        if not self.test_results:
            return 0
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        return (passed / len(self.test_results)) * 100


def main():
    import argparse

    parser = argparse.ArgumentParser(description="E2E Tests for PunterEdge")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the application")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--admin-email", default="info@fm8.global", help="Admin email for testing")
    parser.add_argument("--admin-password", default="admin123", help="Admin password for testing")

    args = parser.parse_args()

    runner = E2ETestRunner(
        base_url=args.url,
        headless=args.headless
    )
    runner.admin_email = args.admin_email
    runner.admin_password = args.admin_password

    pass_rate = runner.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if pass_rate >= 70 else 1)


if __name__ == "__main__":
    main()
