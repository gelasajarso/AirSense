# Upload Feature Fix - Instructions

## Issue
Getting 404 error when trying to upload data: `404 Client Error: Not Found for url: http://localhost:8000/upload`

## Root Cause
The `/upload` endpoint was added to the code but the API server needs to be restarted to register the new endpoint.

## Solution

### Step 1: Stop the Current API Server
If the API server is running, stop it by:
- Pressing `Ctrl+C` in the terminal where it's running
- Or close the terminal window

### Step 2: Restart the API Server

**Option A: Using the restart script (Recommended)**
```bash
.\restart_api_for_upload.bat
```

**Option B: Manual restart**
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Verify the Endpoint is Available
Open your browser and go to:
```
http://localhost:8000/docs
```

Look for the `/upload` endpoint in the API documentation. It should be listed under the endpoints.

### Step 4: Test the Upload Feature
1. Open the dashboard: `streamlit run frontend/dashboard.py`
2. Navigate to "Upload Data" in the sidebar
3. Select a CSV file
4. Click "Upload and Process"
5. You should see a success message!

## Changes Made

### 1. Fixed Import Statement
Added `UploadFile` and `File` to the FastAPI imports in `src/api/routes.py`:
```python
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, UploadFile, File
```

### 2. Fixed Upload Endpoint Signature
Changed the endpoint to properly accept file uploads:
```python
@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    process_immediately: bool = Query(True),
    request: Request = None,
    background_tasks: BackgroundTasks = None,
    validator=Depends(get_validator)
):
```

### 3. Simplified File Handling
Removed the form parsing and directly accept the file as a parameter.

## Testing

### Test with a Sample CSV File
Create a test file `test_data.csv`:
```csv
datetime,PM2.5,PM10,NO2,SO2,CO,O3,TEMP,PRES
2024-01-01 00:00:00,35.5,50.2,45.0,10.5,0.8,25.3,5.2,1020.5
2024-01-01 01:00:00,38.2,52.1,47.5,11.0,0.9,23.1,4.8,1021.0
2024-01-01 02:00:00,40.1,55.3,48.2,11.5,1.0,22.5,4.5,1021.5
```

### Upload Steps:
1. Go to "Upload Data" page
2. Click "Browse files" and select `test_data.csv`
3. Preview the data
4. Click "🚀 Upload and Process"
5. Check for success message

## Troubleshooting

### Still Getting 404 Error?
- Make sure you restarted the API server
- Check that the server is running on port 8000
- Verify the endpoint exists at http://localhost:8000/docs

### Upload Button Not Working?
- Check browser console for errors (F12)
- Verify API server is running
- Check that the file is in CSV format

### File Uploads But Shows Error?
- Check the validation report
- Ensure CSV has required columns (datetime + pollutants)
- Verify datetime format is correct

### Processing Not Starting?
- This is normal if PySpark is not installed
- File will still be uploaded and available
- You can process it manually later

## API Endpoint Details

### Endpoint: POST /upload

**Parameters:**
- `file`: CSV file (multipart/form-data) - Required
- `process_immediately`: boolean (default: true) - Optional

**Response:**
```json
{
  "status": "uploaded_and_processing",
  "message": "File uploaded successfully and processing started",
  "file_path": "data/raw/uploaded_20260506_120000.csv",
  "filename": "uploaded_20260506_120000.csv",
  "validation": {
    "total_rows": 100,
    "missing_values_count": 0,
    "has_critical_issues": false
  },
  "timestamp": "2026-05-06T12:00:00"
}
```

**Status Values:**
- `uploaded_and_processing`: File uploaded and processing started
- `uploaded`: File uploaded successfully (not processed)
- `uploaded_with_warnings`: File uploaded but has validation issues
- `uploaded_not_processed`: File uploaded but processor unavailable
- `uploaded_without_validation`: File uploaded but validation failed

## Files Modified

1. **src/api/routes.py**
   - Added `UploadFile` and `File` imports
   - Fixed `/upload` endpoint signature
   - Improved file handling

2. **restart_api_for_upload.bat** (NEW)
   - Quick script to restart API server

## Next Steps

After successfully uploading data:
1. Go to "Dashboard" to see your data
2. Use "Analysis" to analyze patterns
3. Use "Forecasting" to predict future values

## Support

If you continue to have issues:
1. Check the API server logs for errors
2. Verify the file format matches requirements
3. Ensure all dependencies are installed
4. Check that ports 8000 and 8501 are not blocked

## Success Indicators

✅ API server starts without errors
✅ `/upload` endpoint visible in http://localhost:8000/docs
✅ File upload shows success message
✅ Validation report displays
✅ Data appears in dashboard

You're all set! The upload feature should now work correctly. 🎉
