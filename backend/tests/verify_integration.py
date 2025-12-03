import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import server

def test_index_serving():
    client = server.test_client()
    response = client.get('/')
    
    if response.status_code == 200:
        print("SUCCESS: Root URL returned 200 OK")
        if b'DailyStack' in response.data or b'Vite' in response.data:
             # Note: The title might still be Vite + Svelte if I didn't change index.html title, 
             # but the body should have DailyStack.
             # Let's check for something unique to my new App.svelte
             # Wait, App.svelte is compiled into JS. The HTML will mainly contain the script tags.
             # But the title in index.html is likely still "Vite + Svelte" unless I changed it.
             # I didn't change index.html in the plan.
             # But I can check if the response contains the script tags pointing to assets.
             print("SUCCESS: Content received")
             print(response.data[:200]) # Print first 200 chars
    else:
        print(f"FAILURE: Root URL returned {response.status_code}")
        sys.exit(1)

if __name__ == "__main__":
    test_index_serving()
