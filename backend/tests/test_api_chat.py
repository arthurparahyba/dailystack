import requests
import json
import sys

def test_api_chat():
    url = "http://127.0.0.1:5000/api/ask-llm"
    payload = {"question": "oi"}
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return

        print("Streaming response...")
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(f"Received: {decoded_line}")
                if "error_type" in decoded_line and "CODEBUDDY_5000" in decoded_line:
                    print("FAIL: Received capacity error!")
                    return
                if "answer" in decoded_line:
                    print("SUCCESS: Received answer chunk")
                    # We can stop after receiving some data to confirm it works
                    return
                    
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_api_chat()
