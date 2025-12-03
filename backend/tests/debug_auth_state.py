import requests
import sys

def debug_check():
    base_url = "http://127.0.0.1:5000/api"
    
    print("--- Checking Auth ---")
    try:
        res = requests.get(f"{base_url}/check-auth")
        print(f"Auth Status: {res.json()}")
    except Exception as e:
        print(f"Auth Check Failed: {e}")

    print("\n--- Checking Debug State ---")
    try:
        res = requests.get(f"{base_url}/debug/state")
        state = res.json()
        print(f"Has Credentials: {state.get('has_credentials')}")
        print(f"Current Date: {state.get('current_date')}")
        scenario = state.get('scenario')
        if scenario:
            print(f"Scenario Title: {scenario.get('title')}")
        else:
            print("Scenario: None")
    except Exception as e:
        print(f"State Check Failed: {e}")

if __name__ == "__main__":
    debug_check()
