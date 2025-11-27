from flask import Blueprint, jsonify, request
import requests
import datetime
import os

api_bp = Blueprint('api', __name__)

from backend.client import StackSpotClient

# Global State
app_state = {
    "current_date": None,
    "scenario": None,
    "flashcards": [],
    "current_flashcard_index": 0
}

# Initialize Client
client = StackSpotClient()

def load_daily_challenge():
    """Loads the daily challenge from the GenAI Agent."""
    print("Fetching daily challenge from GenAI Agent...", flush=True)
    data = client.get_daily_challenge()
    
    if data:
        app_state["current_date"] = data.get("date")
        app_state["scenario"] = data.get("scenario")
        app_state["flashcards"] = data.get("flashcards", [])
        app_state["current_flashcard_index"] = 0
        print("Daily challenge loaded successfully.", flush=True)
    else:
        print("Failed to load daily challenge. Using fallback/empty state.", flush=True)
        # Optional: Keep mock data as fallback or leave empty
        # For now, we'll leave it empty or maybe set an error state in a real app


@api_bp.route('/scenario', methods=['GET'])
def get_scenario():
    return jsonify(app_state["scenario"])

@api_bp.route('/flashcard/current', methods=['GET'])
def get_current_flashcard():
    if not app_state["flashcards"]:
        return jsonify({})
    
    idx = app_state["current_flashcard_index"]
    # Safety check
    if idx >= len(app_state["flashcards"]):
        app_state["current_flashcard_index"] = 0
        idx = 0
        
    return jsonify(app_state["flashcards"][idx])

@api_bp.route('/flashcard/next', methods=['POST'])
def next_flashcard():
    if not app_state["flashcards"]:
        return jsonify({"status": "no flashcards"})
        
    app_state["current_flashcard_index"] += 1
    
    # Loop back to 0 if we exceed the list
    if app_state["current_flashcard_index"] >= len(app_state["flashcards"]):
        app_state["current_flashcard_index"] = 0
        
    # Return the new current flashcard
    return get_current_flashcard()

@api_bp.route('/ask-llm', methods=['POST'])
def ask_llm():
    data = request.json
    question = data.get("question")
    
    # Mock LLM interaction
    # In real app: response = requests.post(LLM_URL, json={"question": question})
    
    mock_answer = f"This is a mock explanation for: '{question}'. In a real scenario, the LLM would explain the concept in depth based on the current context."
    
    return jsonify({"answer": mock_answer})

@api_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Checks if the necessary credentials are set."""
    is_authenticated = all([
        os.environ.get("STK_CLIENT_ID"),
        os.environ.get("STK_CLIENT_KEY"),
        os.environ.get("STK_REALM")
    ])
    return jsonify({"authenticated": is_authenticated})

@api_bp.route('/save-credentials', methods=['POST'])
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
        
    # Reload client credentials
    client.reload_credentials()
    
    # Trigger load of daily challenge
    load_daily_challenge()
    
    return jsonify({"status": "success"})
