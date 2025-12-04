"""StackSpot Chat Client."""
import sys
import json
import requests
from typing import Generator, Dict, Any
from .stackspot_auth_client import StackSpotAuthClient


class StackSpotChatClient:
    """Client for chatting with StackSpot GenAI Agent."""
    
    def __init__(self, auth_client: StackSpotAuthClient):
        self.auth_client = auth_client
        self.base_url = "https://genai-code-buddy-api.stackspot.com/v3/chat"
    
    def chat_with_agent(self, conversation_id: str, user_prompt: str) -> Generator[Dict[str, Any], None, None]:
        """
        Sends a message to the GenAI Code Buddy Agent and yields streaming responses.
        
        Args:
            conversation_id: ID of the conversation
            user_prompt: User's message
            
        Yields:
            dict: Parsed JSON chunks from the stream
        """
        token = self.auth_client.get_token()
        if not token:
            print("Failed to authenticate.", file=sys.stderr)
            yield {"error": "Failed to authenticate"}
            return

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
            response = requests.post(self.base_url, json=data, headers=headers, stream=True)
            
            if response.status_code != 200:
                error_msg = f"Erro: Status code {response.status_code} - {response.text}"
                print(error_msg, file=sys.stderr)
                yield {"error": error_msg}
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
                            print(f"Failed to parse line: {decoded_line}, error: {e}", file=sys.stderr)
                    
                    if 'event: end_event' in decoded_line:
                        break

        except Exception as e:
            print(f"Failed to chat with agent: {e}", file=sys.stderr)
            yield {"error": str(e)}
