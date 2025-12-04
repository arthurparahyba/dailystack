"""Repository interfaces (abstractions) for the domain layer."""
from typing import Protocol, Optional
from .entities import Agent, DailyChallenge, AppState


class AgentRepository(Protocol):
    """Interface for agent repository operations."""
    
    def get_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name."""
        ...
    
    def create(self, name: str, description: str, prompt: str, output_schema: Optional[dict]) -> Optional[Agent]:
        """Create a new agent."""
        ...


class ChallengeRepository(Protocol):
    """Interface for challenge repository operations."""
    
    def get_daily_challenge(self) -> Optional[DailyChallenge]:
        """Get the daily challenge."""
        ...


class StateRepository(Protocol):
    """Interface for application state repository."""
    
    def get_state(self) -> AppState:
        """Get current application state."""
        ...
    
    def update_state(self, state: AppState) -> None:
        """Update application state."""
        ...
