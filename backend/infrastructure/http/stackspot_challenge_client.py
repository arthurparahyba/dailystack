"""StackSpot Challenge Client."""
import sys
import json
import requests
from typing import Optional, Dict, Any
from backend.domain.entities import DailyChallenge
from .stackspot_auth_client import StackSpotAuthClient


class StackSpotChallengeClient:
    """Client for fetching daily challenges from StackSpot GenAI Agent."""
    
    def __init__(self, auth_client: StackSpotAuthClient):
        self.auth_client = auth_client
        self.base_url = "https://genai-inference-app.stackspot.com/v1/agent"
    
    def get_daily_challenge(self, agent_id: str) -> Optional[DailyChallenge]:
        """
        Fetch the daily challenge from the GenAI Agent.
        
        Args:
            agent_id: ID of the agent to query
            
        Returns:
            DailyChallenge object if successful, None otherwise
        """
        token = self.auth_client.get_token()
        if not token:
            return None
        
        url = f'{self.base_url}/{agent_id}/chat'
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
            # Timeout of 60 seconds to accommodate LLM generation time
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Parse the response to get the actual data
            parsed_data = self._parse_agent_response(data)
            
            if parsed_data:
                return DailyChallenge.from_dict(parsed_data)
            
            return None
            
        except Exception as e:
            print(f"Failed to get daily challenge: {e}", file=sys.stderr)
            return None

    def _parse_agent_response(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parses the agent response to extract the actual data.
        
        Args:
            data: Raw response from the agent
            
        Returns:
            dict: Parsed data or None if parsing fails
        """
        if 'message' not in data or not isinstance(data['message'], str):
            print(f"Failed to parse agent response: missing or invalid 'message' field", file=sys.stderr)
            return None
            
        try:
            return json.loads(data['message'])
        except json.JSONDecodeError as e:
            print(f"Failed to parse agent response JSON: {e}", file=sys.stderr)
            return None
