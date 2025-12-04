"""Use case: Chat With Agent."""
from typing import Generator, Dict, Any
from backend.infrastructure.http.stackspot_chat_client import StackSpotChatClient


class ChatWithAgent:
    """
    Use case for chatting with the agent.
    
    Encapsulates the logic of sending messages and streaming responses.
    """
    
    def __init__(self, chat_client: StackSpotChatClient):
        self.chat_client = chat_client
    
    def execute(self, conversation_id: str, user_prompt: str) -> Generator[Dict[str, Any], None, None]:
        """
        Execute the use case.
        
        Args:
            conversation_id: ID of the conversation
            user_prompt: User's message
            
        Yields:
            dict: Response chunks
        """
        return self.chat_client.chat_with_agent(conversation_id, user_prompt)
