"""Quick test to verify the analysis fix works."""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_time_patterns():
    """Test time patterns endpoint."""
    print("Testing /analysis/time-patterns endpoint...")
    
    url = f"{API_BASE_URL}/analysis/time-patterns"
    params = {
        "pollutant": "PM2.5",
        "analysis_type": "daily"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Time patterns endpoint is working")
            data = response.json()
            print(f"   Analysis type: {data.get('analysis_type')}")
            print(f"   Pollutant: {data.get('pollutant')}")
            print(f"   Engine: {data.get('engine', 'spark')}")
            return True
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API. Is it running?")
        print(f"   Make sure API is running at {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_correlations():
    """Test correlations endpoint."""
    print("\nTesting /analysis/correlations endpoint...")
    
    url = f"{API_BASE_URL}/analysis/correlations"
    params = {
        "analysis_type": "pollutants"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Correlations endpoint is working")
            data = response.json()
            print(f"   Analysis type: {data.get('analysis_type')}")
            print(f"   Engine: {data.get('engine', 'spark')}")
            return True
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API. Is it running?")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_health():
    """Test API health endpoint."""
    print("Testing /health endpoint...")
    
    url = f"{API_BASE_URL}/health"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ API is healthy")
            data = response.json()
            components = data.get('components', {})
            print(f"   Data processor: {'✅' if components.get('data_processor') else '❌ (using pandas fallback)'}")
            print(f"   Forecaster: {'✅' if components.get('forecaster') else '❌'}")
            print(f"   Data available: {'✅' if components.get('data_available') else '❌'}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to API at {API_BASE_URL}")
        print("   Please start the API server:")
        print("   python -m src.main api")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AirSense Analysis Fix Verification")
    print("=" * 60)
    print()
    
    # Test health first
    if not test_health():
        print("\n⚠️  API is not running or not healthy")
        print("   Start the API with: python -m src.main api")
        exit(1)
    
    print()
    
    # Test analysis endpoints
    time_patterns_ok = test_time_patterns()
    correlations_ok = test_correlations()
    
    print()
    print("=" * 60)
    if time_patterns_ok and correlations_ok:
        print("✅ ALL TESTS PASSED!")
        print("   The analysis fix is working correctly.")
        print("   You can now use the Analysis features in the dashboard.")
    else:
        print("❌ SOME TESTS FAILED")
        print("   Please check the API logs for errors.")
        print("   Make sure you restarted the API server after the fix.")
    print("=" * 60)
