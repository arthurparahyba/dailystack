import requests
import sys
import time

def test_scenario():
    url = "http://127.0.0.1:5000/api/scenario"
    print(f"Testing {url}...")
    
    try:
        response = requests.get(url)
        
        # 1. Check Headers
        cache_control = response.headers.get('Cache-Control', '')
        print(f"Cache-Control: {cache_control}")
        
        if 'no-store' not in cache_control:
            print("FAIL: Cache-Control header missing or incorrect")
        else:
            print("SUCCESS: Cache-Control header present")
            
        # 2. Check Data
        data = response.json()
        print(f"Scenario Title: {data.get('title')}")
        
        if "Debug Scenario" in data.get('title', ''):
            print("FAIL: Returned MOCK data")
        elif data.get('title'):
            print("SUCCESS: Returned REAL data")
        else:
            print("WARNING: No title returned (empty?)")
            
    except Exception as e:
        print(f"Exception: {e}")
        print("Backend might not be running.")

if __name__ == "__main__":
    test_scenario()
