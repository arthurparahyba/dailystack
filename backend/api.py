from flask import Blueprint, jsonify, request, Response, stream_with_context
import requests
import datetime
import os
import json

api_bp = Blueprint('api', __name__)

from backend.client import StackSpotClient
from backend.models import AppState, Scenario, Flashcard, DailyChallenge

# Global State - Typed AppState instance
app_state: AppState = AppState()

# Initialize Client
client = StackSpotClient()

def load_daily_challenge():
    """Loads the daily challenge from the GenAI Agent."""
    app_state.is_loading = True
    app_state.error = None
    print("Fetching daily challenge from GenAI Agent...", flush=True)
    daily_challenge = client.get_daily_challenge()
    
    if daily_challenge:
        # Store the typed DailyChallenge object directly
        print(f"DEBUG - Loaded challenge for date: {daily_challenge.date}", flush=True)
        # Use repr() to avoid UnicodeEncodeError
        print(f"DEBUG - Scenario: {repr(daily_challenge.scenario.title)}", flush=True)
        print(f"DEBUG - Flashcard count: {len(daily_challenge.flashcards)}", flush=True)
        
        app_state.daily_challenge = daily_challenge
        app_state.current_flashcard_index = 0
        app_state.conversations = {}  # Reset conversations on new challenge
        
        # Initialize conversation for first card
        app_state.initialize_conversation(0)
        
        app_state.is_loading = False
        print("Daily challenge loaded successfully.", flush=True)
    else:
        print("Failed to load daily challenge.", flush=True)
        app_state.error = client.last_error or "Failed to load daily challenge"
        app_state.is_loading = False


@api_bp.after_request
def add_header(response):
    """Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Returns the current loading status and data availability."""
    return jsonify({
        "loading": app_state.is_loading,
        "has_data": app_state.daily_challenge is not None,
        "error": app_state.error
    })


@api_bp.route('/scenario', methods=['GET'])
def get_scenario():
    scenario = app_state.get_scenario()
    if scenario:
        print(f"DEBUG - Scenario data: {scenario.title}")
        return jsonify(scenario.to_dict())
    return jsonify({})

@api_bp.route('/flashcard/current', methods=['GET'])
def get_current_flashcard():
    flashcard = app_state.get_current_flashcard()
    if flashcard:
        return jsonify(flashcard.to_dict())
    return jsonify({})

@api_bp.route('/flashcard/next', methods=['POST'])
def next_flashcard():
    flashcard = app_state.next_flashcard()
    if flashcard:
        return jsonify(flashcard.to_dict())
    return jsonify({"status": "no flashcards"})

@api_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    idx = app_state.current_flashcard_index
    conversation = app_state.get_conversation(idx)
    if conversation:
        return jsonify(conversation.messages)
    return jsonify([])

@api_bp.route('/ask-llm', methods=['POST'])
def ask_llm():
    data = request.json
    question = data.get("question")
    is_hidden = data.get("hidden", False)
    print(f"pergunta do usuário: {question} (hidden={is_hidden})")
    
    idx = app_state.current_flashcard_index
    
    # Ensure conversation exists (should be handled by load/next, but safety check)
    if idx not in app_state.conversations:
         app_state.initialize_conversation(idx)
    
    # Save user message ONLY if not hidden
    if not is_hidden:
        app_state.conversations[idx].messages.append({"role": "user", "content": question})
    
    if not app_state.current_conversation_id:
        app_state.current_conversation_id = app_state.conversations[idx].id
    print(f"id da conversa: {app_state.current_conversation_id}")
    
    # Build user prompt
    if app_state.is_first_message_for_card:
        flashcard = app_state.get_current_flashcard()
        if flashcard:
            flashcard_question = flashcard.question
            flashcard_answer = flashcard.detailed_explanation or flashcard.answer
            
            user_prompt = f"dada a questão: {flashcard_question} e dada a resposta {flashcard_answer} Responda a mensagem do usuário: {question}"
            app_state.is_first_message_for_card = False
            app_state.conversations[idx].is_first = False
        else:
            user_prompt = question
    else:
        user_prompt = question
    
    def generate():
        full_answer = ""
        for event_data in client.chat_with_agent(app_state.current_conversation_id, user_prompt):
            if "answer" in event_data:
                answer_chunk = event_data["answer"]
                full_answer += answer_chunk
                chunk = f"data: {json.dumps(event_data)}\n\n"
                print(f"Yielding chunk: {chunk.strip()}", flush=True) # Debug
                yield chunk
            elif "error" in event_data:
                chunk = f"data: {json.dumps(event_data)}\n\n"
                print(f"Yielding error chunk: {chunk.strip()}", flush=True) # Debug
                yield chunk
                break
        
        # Save bot message after streaming is complete
        if full_answer:
            app_state.conversations[idx].messages.append({"role": "bot", "content": full_answer})
    
    return Response(stream_with_context(generate()), content_type='text/event-stream')

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
        f.write(f"STK_CLIENT_ID={client_id}\\n")
        f.write(f"STK_CLIENT_KEY={client_key}\\n")
        f.write(f"STK_REALM={realm}\\n")
        
    # Reload client credentials
    client.reload_credentials()
    
    # Trigger load of daily challenge
    load_daily_challenge()
    
    return jsonify({"status": "success"})

@api_bp.route('/debug/state', methods=['GET'])
def debug_state():
    """Returns the current app state for debugging."""
    scenario = app_state.get_scenario()
    return jsonify({
        "current_date": app_state.get_current_date(),
        "scenario": scenario.to_dict() if scenario else None,
        "flashcards_count": app_state.get_flashcard_count(),
        "current_flashcard_index": app_state.current_flashcard_index,
        "has_credentials": all([
            os.environ.get("STK_CLIENT_ID"),
            os.environ.get("STK_CLIENT_KEY"),
            os.environ.get("STK_REALM")
        ])
    })

@api_bp.route('/debug/reload', methods=['POST'])
def debug_reload():
    """Manually triggers a reload of the daily challenge."""
    load_daily_challenge()
    return jsonify({"status": "reload triggered"})

@api_bp.route('/debug/fetch', methods=['GET'])
def debug_fetch():
    """Debug endpoint to try fetching data and return result/error."""
    try:
        # Check Auth first
        token = client.authenticate()
        if not token:
             return jsonify({
                 "status": "failed", 
                 "reason": "Authentication failed",
                 "client_id": client.client_id,
                 "has_key": bool(client.client_key),
                 "realm": client.realm
             })

        # Try fetch
        challenge = client.get_daily_challenge()
        if challenge:
            return jsonify({"status": "success", "title": challenge.scenario.title})
        else:
            return jsonify({
                "status": "failed", 
                "reason": "client.get_daily_challenge returned None (Auth successful)",
                "last_error": client.last_error
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def init_app_state():
    """Initialize the application state on startup."""
    print("Initializing application state...", flush=True)
    load_daily_challenge()
