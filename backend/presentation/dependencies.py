"""Dependency Injection Container."""
import os
from typing import Optional

# Infrastructure
from backend.infrastructure.http.stackspot_auth_client import StackSpotAuthClient
from backend.infrastructure.http.stackspot_agent_client import StackSpotAgentClient
from backend.infrastructure.http.stackspot_challenge_client import StackSpotChallengeClient
from backend.infrastructure.http.stackspot_chat_client import StackSpotChatClient
from backend.infrastructure.repositories.in_memory_state_repository import InMemoryStateRepository

# Use Cases
from backend.use_cases.auth.authenticate_user import AuthenticateUser
from backend.use_cases.agents.ensure_agent_exists import EnsureAgentExists
from backend.use_cases.challenges.get_daily_challenge import GetDailyChallenge
from backend.use_cases.chat.chat_with_agent import ChatWithAgent


class Container:
    """Dependency Injection Container."""
    
    def __init__(self):
        # Repositories
        self.state_repository = InMemoryStateRepository()
        
        # HTTP Clients
        self.auth_client = StackSpotAuthClient()
        self.agent_client = StackSpotAgentClient(self.auth_client)
        self.challenge_client = StackSpotChallengeClient(self.auth_client)
        self.chat_client = StackSpotChatClient(self.auth_client)
        
        # Use Cases
        self.authenticate_user = AuthenticateUser(self.auth_client)
        
        # Agent Configuration
        self.agent_name = "Flashcards - Java/Python/AWS"
        self.agent_description = "Agent for generating flashcards"
        self.agent_prompt = "You are a helpful assistant."
        
        # Output Schema for Flashcards
        self.flashcard_schema = {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "scenario": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "problem_description": {"type": "string"},
                        "solution_description": {"type": "string"}
                    },
                    "required": ["title", "problem_description", "solution_description"]
                },
                "flashcards": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "question": {"type": "string"},
                            "answer": {"type": "string"},
                            "detailed_explanation": {"type": "string"}
                        },
                        "required": ["id", "question", "answer"]
                    }
                }
            },
            "required": ["date", "scenario", "flashcards"]
        }
        
        self.ensure_agent_exists = EnsureAgentExists(
            agent_client=self.agent_client,
            agent_name=self.agent_name,
            agent_description=self.agent_description,
            agent_prompt=self.agent_prompt,
            output_schema=self.flashcard_schema
        )
        
        self.get_daily_challenge = GetDailyChallenge(
            challenge_client=self.challenge_client,
            ensure_agent_use_case=self.ensure_agent_exists
        )
        
        self.chat_with_agent = ChatWithAgent(self.chat_client)

# Global Container Instance
container = Container()
