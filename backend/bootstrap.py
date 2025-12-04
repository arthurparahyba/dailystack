"""Legacy API entry point (Refactored to use Clean Architecture)."""
from backend.presentation.dependencies import container

# Export app_state for compatibility (though not strictly needed if app.py doesn't use it)
app_state = container.state_repository.get_state()

def init_app_state():
    """Initialize the application state on startup."""
    print("Initializing application state...", flush=True)
    state = container.state_repository.get_state()
    state.is_loading = True
    state.error = None
    
    try:
        # Use the GetDailyChallenge use case
        challenge = container.get_daily_challenge.execute()
        
        if challenge:
             state.daily_challenge = challenge
             state.current_flashcard_index = 0
             state.conversations = {}
             state.initialize_conversation(0)
             state.is_loading = False
             print("Daily challenge loaded successfully.", flush=True)
        else:
             state.error = "Failed to load daily challenge"
             state.is_loading = False
             print("Failed to load daily challenge.", flush=True)
             
    except Exception as e:
        state.error = str(e)
        state.is_loading = False
        print(f"Error initializing state: {e}", flush=True)
