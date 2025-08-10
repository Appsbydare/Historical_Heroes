# API Connection Error Fix

## Problem:
The frontend is deployed successfully but getting "Connection Error" because the API can't find the CSV file or has CORS issues.

## Solution Applied:

1. **Added CORS Support:**
   - Added `flask-cors` to requirements
   - Enabled CORS for all API routes

2. **Improved CSV File Path Resolution:**
   - Added multiple possible paths for CSV file
   - Added better error handling and logging
   - Added fallback paths for Vercel environment

3. **Enhanced Error Handling:**
   - Added detailed error logging
   - Better error messages for debugging
   - Graceful handling when CSV is not found

4. **Added Debug Logging:**
   - Log CSV file path when found
   - Log number of nodes loaded
   - Log specific errors for each endpoint

## Files Modified:
- `api/csv_reader.py` - Added CORS, better path resolution, error handling
- `api/requirements.txt` - Added flask-cors dependency

## Expected Result:
- API should find and load the CSV file
- CORS errors should be resolved
- Frontend should successfully load session data
- Network visualization should display Korean War data

## Next Steps:
1. Commit these changes
2. Push to GitHub
3. Vercel will redeploy with fixed API
4. Test the live application 