import sys
import os
import requests
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.infrastructure.http.stackspot_auth_client import StackSpotAuthClient
from backend.infrastructure.http.stackspot_agent_client import StackSpotAgentClient
from backend.infrastructure.http.stackspot_challenge_client import StackSpotChallengeClient
from backend.domain.entities import AgentCreationRequest

def diagnose():
    print("--- Starting Diagnosis ---")
    
    # 1. Check Credentials
    print("\n1. Checking Credentials...")
    client_id = os.environ.get("STK_CLIENT_ID")
    client_key = os.environ.get("STK_CLIENT_KEY")
    realm = os.environ.get("STK_REALM")
    
    if not all([client_id, client_key, realm]):
        print("FAIL: Missing environment variables.")
        return
    print("PASS: Credentials found in env.")
    
    # 2. Test Authentication
    print("\n2. Testing Authentication...")
    auth_client = StackSpotAuthClient()
    token = auth_client.get_token()
    
    if not token:
        print("FAIL: Could not obtain token.")
        return
    print("PASS: Token obtained successfully.")
    
    # 3. Test Agent Existence
    print("\n3. Testing Agent Existence...")
    agent_client = StackSpotAgentClient(auth_client)
    agent_name = "Flashcards - Java/Python/AWS"
    
    try:
        agent = agent_client.get_by_name(agent_name)
        if agent:
            print(f"PASS: Agent found with ID: {agent.id}")
            agent_id = agent.id
        else:
            print(f"WARN: Agent '{agent_name}' not found. Attempting creation simulation...")
            # We won't actually create to avoid side effects in diagnosis unless needed
            print("SKIP: Creation skipped in diagnosis.")
            return
    except Exception as e:
        print(f"FAIL: Error checking agent: {e}")
        return

    # 4. Test Challenge Fetching
    print("\n4. Testing Challenge Fetching...")
    challenge_client = StackSpotChallengeClient(auth_client)
    
    # Manually constructing request to see raw response
    url = f'{challenge_client.base_url}/{agent_id}/chat'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # payload same as in client but without hardcoded conversation_id if possible, or testing with it
    payload = {
        "streaming": False,
        "user_prompt": "proximo cenário",
        "stackspot_knowledge": False,
        "return_ks_in_response": False,
        "use_conversation": False, # Trying FALSE first to see if it works without history
        # "conversation_id": "..." 
    }
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text[:500]}...") # Print first 500 chars
        
        if response.status_code == 200:
            data = response.json()
            if 'message' in data:
                print("PASS: Received message from agent.")
                try:
                    content = json.loads(data['message'])
                    print("PASS: Message is valid JSON.")
                    print(json.dumps(content, indent=2))
                except:
                    print("WARN: Message is NOT valid JSON.")
            else:
                print("FAIL: No 'message' field in response.")
        else:
            print("FAIL: Non-200 status code.")
            
    except Exception as e:
        print(f"FAIL: Request failed: {e}")

if __name__ == "__main__":
    diagnose()
