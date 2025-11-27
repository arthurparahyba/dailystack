import os
import requests
import json
import time

class StackSpotClient:
    def __init__(self):
        self.reload_credentials()
        self.token = None
        self.token_expires_at = 0

    def reload_credentials(self):
        """Reloads credentials from environment variables."""
        self.client_id = os.environ.get("STK_CLIENT_ID")
        self.client_key = os.environ.get("STK_CLIENT_KEY")
        self.realm = os.environ.get("STK_REALM")

    def authenticate(self):
        """Authenticates with the IDM service to get a JWT."""
        if not all([self.client_id, self.client_key, self.realm]):
            print("Missing credentials. Please set STK_CLIENT_ID, STK_CLIENT_KEY, and STK_REALM.")
            return None

        # Check if token is still valid (with 60s buffer)
        if self.token and time.time() < self.token_expires_at - 60:
            return self.token

        url = f"https://idm.stackspot.com/{self.realm}/oidc/oauth/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_key
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            json_response = response.json()
            print(f"Authentication successful: {json_response}")
            self.token = json_response['access_token']
            # Default to 1 hour expiration if not provided, usually expires_in is returned
            expires_in = json_response.get('expires_in', 3600)
            self.token_expires_at = time.time() + expires_in
            return self.token
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None

    def get_daily_challenge(self):
        """Fetches the daily challenge from the GenAI Agent."""
        token = self.authenticate()
        if not token:
            print("Failed to authenticate.")
            return None

        url = 'https://genai-inference-app.stackspot.com/v1/agent/01JZV0C3DT4TM3BYYGAM8RS981/chat'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        payload = {
            "streaming": False,
            "user_prompt": "proximo cenário",
            "stackspot_knowledge": False,
            "return_ks_in_response": False,
            "use_conversation": True,
            "conversation_id": "01KB1ATKQDKNWZXSV3JNCP72KB" 
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response formats
            if 'message' in data and isinstance(data['message'], str):
                try:
                    return json.loads(data['message'])
                except json.JSONDecodeError:
                    return data

            if isinstance(data, str):
                 return json.loads(data)
            
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "")
                elif content.startswith("```"):
                    content = content.replace("```", "")
                return json.loads(content)
                
            return data

        except Exception as e:
            print(f"Failed to get daily challenge: {e}")
            return None
