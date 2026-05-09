# ⚠️ CRITICAL: You MUST Restart the API Server

## The Problem
You're getting a **404 error** because the API server is running with the OLD code that doesn't have the `/upload` endpoint.

## Why This Happens
When you start the API server, it loads all the routes into memory. Even though we added the `/upload` endpoint to the code, the running server doesn't know about it yet.

## The Solution: RESTART THE API SERVER

### Step-by-Step Instructions:

#### 1. **Stop the Current API Server**

Find the terminal/command prompt window where the API server is running. You'll see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Press `Ctrl+C`** to stop it.

If you can't find the window or it won't stop:
- Open Task Manager (Ctrl+Shift+Esc)
- Find "Python" processes
- End the one running uvicorn/API server

#### 2. **Start the API Server Again**

Open a NEW command prompt/terminal in your project directory and run:

```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Wait for this message:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### 3. **Verify the Endpoint is Available**

Open your web browser and go to:
```
http://localhost:8000/docs
```

**Look for `/upload` in the list of endpoints.** It should be there now!

You should see:
- POST /upload - Upload air quality data file (CSV format)

#### 4. **Try Uploading Again**

Now go back to your dashboard and try uploading a file again. It should work!

---

## Alternative: Use the Restart Script

I created a batch file to make this easier. Just run:

```bash
.\restart_api_for_upload.bat
```

This will:
1. Stop any running API servers
2. Start a fresh API server with the new code
3. The `/upload` endpoint will be available

---

## How to Verify It's Working

### Test 1: Check the API Docs
Go to: http://localhost:8000/docs

You should see the `/upload` endpoint listed.

### Test 2: Check the Health Endpoint
Go to: http://localhost:8000/health

You should see a JSON response with status "healthy".

### Test 3: Try the Upload
1. Open dashboard: `streamlit run frontend/dashboard.py`
2. Go to "Upload Data"
3. Select a CSV file
4. Click "Upload and Process"
5. Should see success message (not 404 error)

---

## Still Not Working?

### Check if the API is Running on the Right Port

Run this command:
```bash
netstat -ano | findstr :8000
```

You should see something like:
```
TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING    12345
```

If you don't see anything, the API server is not running.

### Check for Port Conflicts

If port 8000 is already in use by something else:
1. Stop the other application using port 8000
2. Or change the API port in the startup command:
   ```bash
   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
   ```
3. Update the dashboard to use the new port (edit `API_BASE_URL` in `frontend/dashboard.py`)

### Check the API Logs

Look at the terminal where the API server is running. You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If you see errors, read them carefully - they'll tell you what's wrong.

---

## Quick Checklist

- [ ] Stopped the old API server (Ctrl+C)
- [ ] Started the API server again
- [ ] Saw "Application startup complete" message
- [ ] Checked http://localhost:8000/docs
- [ ] Saw `/upload` endpoint in the docs
- [ ] Tried uploading a file from dashboard
- [ ] Got success message (not 404)

---

## Why Can't the Server Auto-Reload?

Even though we use `--reload` flag, FastAPI/Uvicorn sometimes doesn't detect changes to route definitions properly. A manual restart ensures the new endpoint is definitely loaded.

---

## Summary

**The fix is simple: RESTART THE API SERVER**

1. Stop it (Ctrl+C)
2. Start it again (same command)
3. Verify `/upload` exists in http://localhost:8000/docs
4. Try uploading again

That's it! The 404 error will be gone. 🎉
