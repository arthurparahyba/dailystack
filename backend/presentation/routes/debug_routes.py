"""Debug Routes."""
import os
from flask import Blueprint, jsonify, request
from backend.presentation.dependencies import container

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Checks if the necessary credentials are set."""
    # We can check directly from the auth client or environment
    # Using auth client to check if token is retrievable would be better, 
    # but for now checking env vars as per original logic
    is_authenticated = all([
        os.environ.get("STK_CLIENT_ID"),
        os.environ.get("STK_CLIENT_KEY"),
        os.environ.get("STK_REALM")
    ])
    return jsonify({"authenticated": is_authenticated})

@debug_bp.route('/save-credentials', methods=['POST'])
def save_credentials():
    """Saves credentials to .env and updates environment."""
    data = request.json
    client_id = data.get("stk_client_id")
    client_key = data.get("stk_client_key")
    realm = data.get("stk_realm")
    
    if not all([client_id, client_key, realm]):
        return jsonify({"error": "Missing fields"}), 400
        
    # Update process environment
    os.environ["STK_CLIENT_ID"] = client_id
    os.environ["STK_CLIENT_KEY"] = client_key
    os.environ["STK_REALM"] = realm
    
    # Save to .env file
    env_path = os.path.join(os.getcwd(), '.env')
    with open(env_path, 'w') as f:
        f.write(f"STK_CLIENT_ID={client_id}\n")
        f.write(f"STK_CLIENT_KEY={client_key}\n")
        f.write(f"STK_REALM={realm}\n")
        
    # Reload credentials in auth client
    container.authenticate_user.reload_credentials()
    
    # Trigger load of daily challenge
    # We need to call the load logic. Ideally this should be a use case or function we can call.
    # For now, we can trigger it via a helper or directly if we expose it.
    # Let's import the load function from api.py (circular import risk) or move it to a use case.
    # To avoid circular import, we'll rely on the client reloading on next request or 
    # we can re-instantiate the container components if needed.
    # Better approach: The state loading logic should be in a use case.
    
    # Re-executing the daily challenge fetch
    try:
        challenge = container.get_daily_challenge.execute()
        if challenge:
             state = container.state_repository.get_state()
             state.daily_challenge = challenge
             state.current_flashcard_index = 0
             state.conversations = {}
             state.initialize_conversation(0)
             state.is_loading = False
             state.error = None
        else:
             state = container.state_repository.get_state()
             state.error = "Failed to load daily challenge after saving credentials"
    except Exception as e:
        pass

    return jsonify({"status": "success"})

@debug_bp.route('/debug/state', methods=['GET'])
def debug_state():
    """Returns the current app state for debugging."""
    state = container.state_repository.get_state()
    scenario = state.get_scenario()
    return jsonify({
        "current_date": state.get_current_date(),
        "scenario": scenario.to_dict() if scenario else None,
        "flashcards_count": state.get_flashcard_count(),
        "current_flashcard_index": state.current_flashcard_index,
        "has_credentials": all([
            os.environ.get("STK_CLIENT_ID"),
            os.environ.get("STK_CLIENT_KEY"),
            os.environ.get("STK_REALM")
        ])
    })

@debug_bp.route('/debug/reload', methods=['POST'])
def debug_reload():
    """Manually triggers a reload of the daily challenge."""
    state = container.state_repository.get_state()
    state.is_loading = True
    
    try:
        challenge = container.get_daily_challenge.execute()
        if challenge:
             state.daily_challenge = challenge
             state.current_flashcard_index = 0
             state.conversations = {}
             state.initialize_conversation(0)
             state.is_loading = False
             state.error = None
        else:
             state.error = "Failed to reload daily challenge"
             state.is_loading = False
    except Exception as e:
        state.error = str(e)
        state.is_loading = False
        
    return jsonify({"status": "reload triggered"})

@debug_bp.route('/debug/fetch', methods=['GET'])
def debug_fetch():
    """Debug endpoint to try fetching data and return result/error."""
    try:
        # Check Auth first
        token = container.authenticate_user.execute()
        if not token:
             return jsonify({
                 "status": "failed", 
                 "reason": "Authentication failed"
             })

        # Try fetch
        challenge = container.get_daily_challenge.execute()
        if challenge:
            return jsonify({"status": "success", "title": challenge.scenario.title})
        else:
            return jsonify({
                "status": "failed", 
                "reason": "get_daily_challenge returned None (Auth successful)"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
