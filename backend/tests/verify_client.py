import sys
import os

# Add the workspace root to python path
sys.path.append(os.getcwd())

try:
    from backend.client import StackSpotClient
    print("Successfully imported StackSpotClient")
    
    client = StackSpotClient()
    print("Successfully instantiated StackSpotClient")
    
    if hasattr(client, 'reload_credentials'):
        print("Method 'reload_credentials' exists")
    else:
        print("Method 'reload_credentials' MISSING")
        
    if hasattr(client, 'authenticate'):
        print("Method 'authenticate' exists")
    else:
        print("Method 'authenticate' MISSING")

    # Test reload_credentials (should run without error even with missing env vars)
    client.reload_credentials()
    print("reload_credentials() executed successfully")
    
    # Test authenticate (should return None or fail gracefully if no creds)
    token = client.authenticate()
    print(f"authenticate() returned: {token}")
    
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
