import os
import requests
import json
import time
from backend.models import DailyChallenge

class StackSpotClient:
    def __init__(self):
        self.reload_credentials()
        self.token = None
        self.token_expires_at = 0
        self.last_error = None

    def reload_credentials(self):
        self.client_id = os.environ.get("STK_CLIENT_ID")
        self.client_key = os.environ.get("STK_CLIENT_KEY")
        self.realm = os.environ.get("STK_REALM")

    def authenticate(self):
        if self.token and self.token_expires_at > time.time():
            return self.token

        if not all([self.client_id, self.client_key, self.realm]):
            self.last_error = "Missing credentials"
            return None

        url = f"https://idm.stackspot.com/{self.realm}/oidc/oauth/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_key,
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            json_response = response.json()
            self.token = json_response['access_token']
            self.token_expires_at = time.time() + json_response['expires_in'] - 60 # Buffer
            return self.token
        except Exception as e:
            self.last_error = f"Authentication failed: {e}"
            print(f"Authentication failed: {e}")
            return None

    def get_daily_challenge(self) -> DailyChallenge | None:
        """
        Fetches the daily challenge from the GenAI Agent.
        
        Returns:
            DailyChallenge: Object containing date, scenario, and flashcards
            None: If authentication or request fails
        """
        self.last_error = None # Reset error
        token = self.authenticate()
        if not token:
            self.last_error = "Failed to authenticate."
            print("Failed to authenticate.")
            return None

        url = 'https://genai-inference-app.stackspot.com/v1/agent/01KB3P9EHER7FCHMPHM0MMYM5D/chat'
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
            
            # Use ascii() to avoid UnicodeEncodeError on Windows consoles
            print(f"DEBUG - Raw API response: {ascii(data)}", flush=True)
            
            # Parse the response to get the actual data
            parsed_data = self._parse_agent_response(data)
            
            print(f"DEBUG - Parsed data: {ascii(parsed_data)}", flush=True)
            
            if parsed_data:
                # Convert to DailyChallenge object
                return DailyChallenge.from_dict(parsed_data)
            
            self.last_error = "Parsed data is None"
            return None

        except Exception as e:
            self.last_error = f"Failed to get daily challenge: {e}"
            print(f"Failed to get daily challenge: {ascii(e)}")
            return None
    
    def _parse_agent_response(self, data: dict) -> dict | None:
        """
        Parses the agent response to extract the actual data.
        Handles different response formats from the GenAI Agent.
        
        Args:
            data: Raw response from the agent
            
        Returns:
            dict: Parsed data or None if parsing fails
        """
            # Handle different response formats
        if 'message' not in data and isinstance(data['message'], str):
            print(f"Failed to parse agent response There is no message attribute: {data}")
            return None
        try:
            return json.loads(data['message'])
        except json.JSONDecodeError:
            print(f"Failed to parse agent response: {e}")
            return None


    def chat_with_agent(self, conversation_id, user_prompt):
        """Sends a message to the GenAI Code Buddy Agent and yields streaming responses."""
        token = self.authenticate()
        if not token:
            print("Failed to authenticate.")
            return

        url = "https://genai-code-buddy-api.stackspot.com/v3/chat"

        data = {
            "context": {
                "conversation_id": conversation_id,
                "stackspot_ai_version": "2.3.0"
            },
            "user_prompt": f"{user_prompt}"
        }

        headers = {
            'Content-Type': 'application/json',
            'authorization': f'Bearer {token}'
        }

        try:
            response = requests.post(url, json=data, headers=headers, stream=True)
            print(f"Chat response status: {response.status_code}")

            if response.status_code == 403 or response.status_code == 401:
                print(f"Erro: Status code {response.status_code} - {response.text}")
                yield {"error": f"Erro: Status code {response.status_code} - {response.text}"}
                return

            if response.status_code != 200:
                print(f"Erro: Status code {response.status_code} - {response.text}")
                yield {"error": f"Erro: Status code {response.status_code} - {response.text}"}
                return

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    
                    if decoded_line.startswith('data: '):
                        try:
                            json_data = decoded_line[6:] # Slice after 'data: '
                            if json_data.strip():
                                data_dict = json.loads(json_data)
                                if "answer" in data_dict:
                                    yield data_dict
                        except Exception as e:
                            print(f"Failed to parse line: {decoded_line}, error: {e}")
                    
                    if 'event: end_event' in decoded_line:
                        break

        except Exception as e:
            print(f"Failed to chat with agent: {e}")
            yield {"error": str(e)}
