"""In-memory State Repository."""
from backend.domain.entities import AppState
from backend.domain.repositories import StateRepository


class InMemoryStateRepository:
    """In-memory implementation of StateRepository."""
    
    def __init__(self):
        self._state = AppState()
    
    def get_state(self) -> AppState:
        """Get current application state."""
        return self._state
    
    def update_state(self, state: AppState) -> None:
        """Update application state."""
        self._state = state
