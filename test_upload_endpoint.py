"""Test script to verify the upload endpoint exists."""
import requests

API_BASE_URL = "http://localhost:8000"

print("Testing AirSense API Upload Endpoint")
print("=" * 50)

# Test 1: Check if API is running
print("\n1. Checking if API is running...")
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ API is running")
    else:
        print(f"   ❌ API returned status code: {response.status_code}")
except Exception as e:
    print(f"   ❌ API is not running: {e}")
    print("\n   Please start the API server first:")
    print("   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload")
    exit(1)

# Test 2: Check available endpoints
print("\n2. Checking available endpoints...")
try:
    response = requests.get(f"{API_BASE_URL}/openapi.json", timeout=5)
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get("paths", {})
        
        print(f"   Found {len(paths)} endpoints:")
        for path in sorted(paths.keys()):
            methods = list(paths[path].keys())
            print(f"   - {path} [{', '.join(methods).upper()}]")
        
        # Check if /upload exists
        if "/upload" in paths:
            print("\n   ✅ /upload endpoint EXISTS!")
            print(f"   Methods: {list(paths['/upload'].keys())}")
        else:
            print("\n   ❌ /upload endpoint NOT FOUND!")
            print("\n   The API server needs to be restarted to load the new endpoint.")
            print("   Please restart the API server:")
            print("   1. Stop the current server (Ctrl+C)")
            print("   2. Run: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print(f"   ❌ Could not get OpenAPI spec: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error checking endpoints: {e}")

# Test 3: Try to access the upload endpoint
print("\n3. Testing /upload endpoint accessibility...")
try:
    # Try a GET request (should fail with 405 Method Not Allowed, not 404)
    response = requests.get(f"{API_BASE_URL}/upload", timeout=5)
    
    if response.status_code == 404:
        print("   ❌ Endpoint returns 404 - NOT FOUND")
        print("\n   ACTION REQUIRED:")
        print("   The /upload endpoint is not registered with the API server.")
        print("   You MUST restart the API server for the changes to take effect.")
        print("\n   Steps:")
        print("   1. Stop the API server (Ctrl+C in the terminal where it's running)")
        print("   2. Start it again: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload")
    elif response.status_code == 405:
        print("   ✅ Endpoint exists! (405 Method Not Allowed is expected for GET)")
        print("   The endpoint is properly registered and ready for POST requests.")
    else:
        print(f"   Status code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("Test complete!")
print("\nIf the endpoint is not found, restart the API server.")
