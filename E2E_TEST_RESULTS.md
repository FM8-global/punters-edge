# E2E Test Results & Bug Report

**Test Date**: 2026-09-13  
**Environment**: Production (Railway)  
**App URL**: https://punters-edge-production.up.railway.app  
**Status**: ⚠️ **FAILURES DETECTED**

---

## Test Summary

| Component | Status | Details |
|-----------|--------|---------|
| **Authentication** | ✅ PASS | Login working, session persistence confirmed |
| **Admin Dashboard** | ✅ PASS | All tabs accessible |
| **Predictions Section** | 🔴 FAIL | Horse names showing as placeholders (Horse 2 A, Horse 3 A, etc.) |
| **Outcomes Dashboard** | ✅ PASS | Page loads, tabs accessible |
| **Horse Performance** | ✅ PASS | Page loads (no data yet) |
| **Outcomes Report** | 🔴 FAIL | Report generation crashes with JavaScript error |

**Overall Status**: 🔴 **4/6 PASS** - 2 Critical Issues Found

---

## Critical Issues

### BUG #1: Horse Names Showing as Placeholders ❌

**Severity**: HIGH  
**Component**: Predictions Dashboard  
**Status**: CONFIRMED

**Observed Behavior**:
- Predictions are displayed but show placeholder horse names
- Examples: "Horse 2 A", "Horse 3 A", "Horse 4 A", "Horse 6 A", "Horse 7 A", "Horse 1 B", "Horse 2 B"
- Race shows as "mock-race-0", "mock-race-1" instead of real race names
- All predictions show same score: 60/100

**Expected Behavior**:
- Horse names should be real horse identifiers (e.g., "Thunder", "Midnight", "Blazer")
- Race information should show actual track and race details
- Scores should vary by prediction accuracy

**Root Cause**:
- Application is using MOCK DATA instead of real/normalized data
- Field names are likely not normalized from API response
- Backend field normalization may not be working for predictions

**Impact**:
- Users cannot identify which horses are being predicted
- Cannot properly evaluate prediction quality
- Data quality is unacceptable for production use

**Files to Check**:
- `backend/main.py` - Predictions API endpoint (lines around `/predictions`)
- `backend/mock_data.py` - Mock data generation
- `backend/static/outcomes.html` - Frontend rendering logic for predictions
- API response field mapping (horse_name vs horse, etc.)

**Fix Required**:
1. Verify API endpoint returns properly normalized field names
2. Check if using mock data that needs to be replaced with real data
3. Frontend should display normalized field names from API
4. Consider adding field name mapping if API doesn't match frontend expectations

---

### BUG #2: Report Generation Crashes ❌

**Severity**: CRITICAL  
**Component**: Outcomes Report Tab  
**Status**: CONFIRMED

**Error Message**:
```
Error generating report: Cannot read properties of undefined (reading 'toFixed')
```

**Observed Behavior**:
1. User navigates to Outcomes Report tab
2. Form shows fields: Start Date, End Date, Min Score (default: 50)
3. User clicks "Generate Report" button
4. Red error box appears with above message

**Expected Behavior**:
- Report should generate and display table of outcomes
- Financial metrics should be formatted with `.toFixed()` for display
- No JavaScript errors

**Root Cause Analysis**:
- JavaScript code tries to call `.toFixed()` on an undefined value
- Likely cause: Report data array is undefined or empty
- The code assumes data exists and has numeric fields but receives undefined
- May be issue with date filtering logic returning undefined data structure

**Problematic Code Pattern**:
```javascript
// This is likely what's failing:
const roi = data.roi.toFixed(2);  // Error: data.roi is undefined
```

**Impact**:
- Users cannot generate reports at all
- Feature is completely broken
- High priority: This is core functionality

**Files to Check**:
- `backend/static/outcomes.html` - Report generation JavaScript
- Look for `.toFixed()` calls on potentially undefined values
- Check report data fetching/filtering logic
- Verify API endpoint returns proper data structure

**Fix Required**:
1. Add null/undefined checks before calling `.toFixed()`
2. Ensure report data is properly fetched and has expected structure
3. Debug what structure is returned from the outcomes API
4. Add fallback values for missing numeric fields

---

## Test Log

### Test 1: Login & Authentication
**Status**: ✅ PASS

Steps:
1. Navigate to https://punters-edge-production.up.railway.app
2. Login with: info@fm8.global / admin123
3. Verify: "Logged in as info@fm8.global" message appears
4. Verify: Session persists after page reload

Result: PASS - Authentication working correctly

---

### Test 2: Predictions Dashboard
**Status**: 🔴 FAIL

Steps:
1. From admin dashboard, click "VIEW PREDICTIONS"
2. Verify predictions display with correct fields
3. Verify horse names are actual identifiers

Result: FAIL - Horse names are placeholders (Horse 2 A, Horse 3 A, etc.)

Findings:
- 10+ predictions displayed
- All show mock race names: "mock-race-0", "mock-race-1"
- Score: all showing 60/100
- Odds: vary (7.02, 5.26, 7.90, 5.18, etc.)
- Overlay %: vary (29.6%, 34.5%, 32.6%, 47.9%, etc.)

---

### Test 3: Outcomes Dashboard
**Status**: ✅ PASS (partially)

Steps:
1. From admin dashboard, click "OUTCOMES DASHBOARD"
2. Verify page loads with three tabs: Horse Performance, User Performance, Outcomes Report

Result: PASS - Dashboard loads correctly, tabs accessible

---

### Test 4: Outcomes Report Generation
**Status**: 🔴 FAIL

Steps:
1. In Outcomes Dashboard, click "Outcomes Report" tab
2. See form with: Start Date, End Date, Min Score fields
3. Click "Generate Report" button

Result: FAIL - JavaScript error appears

Error:
```
Error generating report: Cannot read properties of undefined (reading 'toFixed')
```

---

## Non-Critical Issues

### Data State
**Observation**: Most dashboards show "No data yet" for actual outcomes, which is expected since no predictions have been completed.

**Status**: ACCEPTABLE - Expected for fresh deployment

---

## Recommendations

### Priority 1 (Critical - Block Release):
1. **Fix Report Generation** - The `.toFixed()` error must be fixed before release
   - Add null checks before calling `.toFixed()`
   - Debug the outcomes API response structure
   - Implement fallback handling for missing data

### Priority 2 (High - Fix Before Production):
2. **Fix Horse Names** - Placeholder names must be replaced
   - Switch from mock data to real data
   - Verify API field normalization is working
   - Ensure horse names are properly mapped from API to frontend

### Priority 3 (Before Release):
3. **Data Population** - Ensure data flows from real source
   - Connect to real prediction/outcome data sources
   - Verify mock data mode is disabled in production
   - Test with real data end-to-end

---

## Code Locations to Investigate

### Backend Files:
- `backend/main.py` - API endpoints
- `backend/mock_data.py` - Mock data generation (should be disabled)
- `backend/outcomes.py` - Outcomes logic

### Frontend Files:
- `backend/static/outcomes.html` - Report generation JavaScript
  - Line: Look for `.toFixed()` calls
  - Check data structure assumptions
  - Add error handling

---

## Next Steps

1. **Developer**: Investigate the `.toFixed()` error in outcomes.html
2. **Developer**: Check if using mock data vs. real data source
3. **Developer**: Fix horse name field mapping
4. **QA**: Re-run E2E tests after fixes
5. **Release**: Only proceed after both critical issues are resolved

---

## Conclusion

The application is **NOT READY FOR RELEASE** due to two critical issues:

1. ❌ Report generation fails with JavaScript error
2. ❌ Predictions showing placeholder horse names instead of real data

Both must be fixed before the application can be released to FM8 team.

Estimated fix time: 1-2 hours for developer to diagnose and resolve both issues.

**Recommended Action**: Do NOT release to team until these issues are fixed.

---

**Report Generated By**: Automated E2E Testing  
**Test Environment**: Production Railway Deployment  
**Recommended Review**: Developer review of backend/main.py and backend/static/outcomes.html
