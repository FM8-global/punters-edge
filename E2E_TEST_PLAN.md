# E2E Testing Plan - PunterEdge Deployment

## Test Scope
This E2E test validates:
- ✅ Approved user login flow
- ✅ New user signup flow
- ✅ Admin panel functionality
- ✅ Password validation system
- ✅ Session management
- ✅ Age verification (18+)
- ✅ Outcomes accuracy
- ✅ Predictions loading
- ✅ User data persistence

---

## Pre-Test Setup

### Test Users
```
Admin User:
  Email: info@fm8.global
  Password: (generate from admin panel or set manually)

Test Approved User:
  Email: testuser@example.com
  Password: (generate or set in admin panel)

Test New User:
  Email: newuser@example.com
  Password: (will create during signup flow)
```

### Test Environment
- Live PythonAnywhere deployment
- Browser: Chrome/Firefox/Safari
- Network: Normal internet connection

---

## Test Cases

### T1: Admin Login Flow
**Objective:** Verify admin can login with password

**Steps:**
1. Navigate to `https://YOUR_USERNAME.pythonanywhere.com/`
2. Enter: `info@fm8.global`
3. See password field appear
4. Enter admin password
5. Click "Login"

**Expected Result:**
- ✅ Redirects to dashboard
- ✅ Shows "Admin Panel" option
- ✅ Shows approved users, pending requests sections
- ✅ Session token stored in localStorage

**Status:** [ ] PASS [ ] FAIL

---

### T2: Approved User Login Flow
**Objective:** Verify approved users can login

**Steps:**
1. Navigate to login page
2. Enter approved user email: `testuser@example.com`
3. See password field appear
4. Enter correct password
5. Click "Login"

**Expected Result:**
- ✅ Redirects to dashboard
- ✅ Shows "Approved User" label
- ✅ Can access predictions
- ✅ Can access outcomes
- ✅ Session persists on page reload

**Status:** [ ] PASS [ ] FAIL

---

### T3: Password Validation
**Objective:** Verify password authentication works correctly

**Substeps:**

**T3a: Correct Password**
1. Login with correct password
2. Should succeed

**T3b: Wrong Password**
1. Enter approved user email
2. Enter incorrect password
3. Click "Login"
4. Should see error: "Invalid email or password"

**T3c: Approved User Without Password Attempt**
1. Enter non-existent email: `fake@example.com`
2. Should still show password field
3. Enter any password
4. Click "Login"
5. Should see error: "Invalid email or password"

**Expected Result:**
- ✅ Correct password: login succeeds
- ✅ Wrong password: login fails with generic error
- ✅ Non-existent user: login fails with generic error
- ✅ No information leakage about which users exist

**Status:** [ ] PASS [ ] FAIL

---

### T4: New User Signup Flow
**Objective:** Verify new users can create accounts

**Steps:**
1. Click "Sign Up" on login page
2. Enter email: `newuser@example.com`
3. Enter password: `TestPass123!`
4. Confirm password: `TestPass123!`
5. Select age: 18 or older
6. Accept terms
7. Click "Sign Up"

**Expected Result:**
- ✅ Redirects to dashboard after signup
- ✅ Shows "Pending Approval" message
- ✅ Email is stored in pending_requests
- ✅ User cannot access full features until approved
- ✅ Can logout and see account was created

**Status:** [ ] PASS [ ] FAIL

---

### T5: Age Verification
**Objective:** Verify 18+ age requirement

**T5a: Under 18 Signup**
1. On signup page
2. Select age: "Under 18"
3. Attempt to signup

**Expected Result:**
- ✅ Shows error: "Must be 18 or older to use PunterEdge"
- ✅ Signup blocked

**T5b: 18 or Older Signup**
1. Select age: "18 or older"
2. Complete signup

**Expected Result:**
- ✅ Signup succeeds
- ✅ Account created

**Status:** [ ] PASS [ ] FAIL

---

### T6: Admin Panel - Add User
**Objective:** Verify admin can add approved users

**Steps:**
1. Login as admin
2. Go to Admin Panel
3. Click "Add New User"
4. Enter email: `admintest@example.com`
5. Generate password (or enter custom password)
6. Click "Add User"

**Expected Result:**
- ✅ User added to approved users
- ✅ Success message shown
- ✅ New user can login with generated password
- ✅ Newly added user stays logged in after logout/login

**Status:** [ ] PASS [ ] FAIL

---

### T7: Session Persistence
**Objective:** Verify user sessions remain valid

**Steps:**
1. Login as approved user
2. Note token in localStorage
3. Reload page (F5)
4. Check if still logged in

**Expected Result:**
- ✅ User remains logged in
- ✅ Token still valid
- ✅ Can access dashboard immediately
- ✅ No need to re-login

**Substeps - Logout Persistence:**
1. While logged in, click "Logout"
2. Refresh page
3. Should see login form

**Expected Result:**
- ✅ Logout clears session
- ✅ Redirects to login after refresh
- ✅ Token removed from localStorage

**Status:** [ ] PASS [ ] FAIL

---

### T8: Dashboard Access
**Objective:** Verify dashboard loads with all sections

**Steps:**
1. Login as approved user
2. Verify page loads
3. Check all sections visible

**Expected Result:**
- ✅ "Predictions" section loads
- ✅ "Outcomes" section loads
- ✅ "User Profile" section visible
- ✅ Navigation works
- ✅ No console errors

**Status:** [ ] PASS [ ] FAIL

---

### T9: Predictions Loading
**Objective:** Verify predictions API works

**Steps:**
1. Login as approved user
2. Navigate to "Predictions" section
3. Verify predictions load

**Expected Result:**
- ✅ Predictions display (or empty state if no data)
- ✅ No errors in console
- ✅ Network request succeeds (check Network tab)
- ✅ API returns valid JSON

**Status:** [ ] PASS [ ] FAIL

---

### T10: Outcomes Accuracy
**Objective:** Verify outcomes data is correct

**Steps:**
1. Login as approved user
2. Navigate to "Outcomes" section
3. Verify outcomes display correctly

**Expected Result:**
- ✅ Outcomes load without errors
- ✅ Data format is correct (arrays, not empty objects)
- ✅ Performance data shows correctly
- ✅ No console errors

**Status:** [ ] PASS [ ] FAIL

---

## Regression Tests

### R1: Approved Users Persist
**Issue from previous:** Users drop off after logout

**Steps:**
1. Add user via admin panel: `persist@example.com`
2. Logout as admin
3. Login again as admin
4. Check if user still exists in approved users list

**Expected Result:**
- ✅ User persists
- ✅ Not dropped from system
- ✅ Can still login

**Status:** [ ] PASS [ ] FAIL

---

### R2: Password Field Shows for All Users
**Issue from previous:** Password field only showed for admin email

**Steps:**
1. Go to login page
2. Enter any non-admin email: `test@test.com`
3. Check if password field appears

**Expected Result:**
- ✅ Password field visible for any email
- ✅ Not just for admin (info@fm8.global)

**Status:** [ ] PASS [ ] FAIL

---

### R3: Outcomes Data Type
**Issue from previous:** Outcomes returned empty dicts instead of arrays

**Steps:**
1. Login as approved user
2. Check Outcomes section
3. Open DevTools → Network tab
4. Check API response for `/outcomes` or similar

**Expected Result:**
- ✅ Returns arrays: `[]` not `{}`
- ✅ No type mismatch errors
- ✅ Dashboard loads correctly

**Status:** [ ] PASS [ ] FAIL

---

## Test Summary

### Before Deployment
- [ ] All code committed to GitHub
- [ ] All tests passing locally
- [ ] Deployment guide ready

### During Deployment
- [ ] Follow PYTHONANYWHERE_DEPLOYMENT.md
- [ ] Each step completed
- [ ] App reloaded successfully

### After Deployment
- [ ] Run T1-T10 test cases
- [ ] Run R1-R3 regression tests
- [ ] All tests passing
- [ ] No console errors
- [ ] App stable for 5 minutes

---

## Sign-Off

**Tester:** ________________  
**Date:** ________________  
**Result:** ✅ PASS / ❌ FAIL  
**Notes:** ________________________________________________

---

## Next Steps if Issues Found

1. Check error logs in PythonAnywhere Web tab
2. Check browser console (F12)
3. Check network requests in DevTools
4. Report specific error messages
5. Fix and redeploy

---

## Production Readiness Checklist

- [ ] All E2E tests passing
- [ ] No JavaScript errors in console
- [ ] API responding correctly
- [ ] Session management working
- [ ] Admin panel fully functional
- [ ] New user signup working
- [ ] Age verification working
- [ ] Outcomes loading correctly
- [ ] Predictions loading correctly
- [ ] Database connections stable
- [ ] Environmental variables set
- [ ] HTTPS working (PythonAnywhere default)

**Ready for Production:** ✅ YES / ❌ NO
