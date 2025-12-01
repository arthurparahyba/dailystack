from flask import Blueprint, jsonify, request, Response, stream_with_context
import requests
import datetime
import os
import json

api_bp = Blueprint('api', __name__)

from backend.client import StackSpotClient
from backend.models import AppState, Scenario, Flashcard, DailyChallenge

# Global State - Typed AppState instance
app_state = AppState()

# Initialize Client
client = StackSpotClient()

def load_daily_challenge():
    """Loads the daily challenge from the GenAI Agent."""
    print("Fetching daily challenge from GenAI Agent...", flush=True)
    daily_challenge = client.get_daily_challenge()
    
    if daily_challenge:
        # Store the typed DailyChallenge object directly
        print(f"DEBUG - Loaded challenge for date: {daily_challenge.date}", flush=True)
        print(f"DEBUG - Scenario: {daily_challenge.scenario.title}", flush=True)
        print(f"DEBUG - Flashcard count: {len(daily_challenge.flashcards)}", flush=True)
        
        app_state.daily_challenge = daily_challenge
        app_state.current_flashcard_index = 0
        app_state.conversations = {}  # Reset conversations on new challenge
        
        # Initialize conversation for first card
        app_state.initialize_conversation(0)
        
        print("Daily challenge loaded successfully.", flush=True)
    else:
        print("Failed to load daily challenge. Using fallback/mock data.", flush=True)
        # Create mock data using typed objects
        mock_scenario = Scenario(
            title="Debug Scenario",
            description="This is a mock scenario for debugging purposes.",
            context="You are debugging a Python application that is missing API credentials."
        )
        
        mock_flashcards = [
            Flashcard(
                question="Why is the API returning null?",
                answer="Because the credentials are missing.",
                category="Debugging",
                detailed_explanation="The application requires STK_CLIENT_ID, STK_CLIENT_KEY, and STK_REALM environment variables to fetch real data.",
                code_example="os.environ.get('STK_CLIENT_ID')"
            )
        ]
        
        app_state.daily_challenge = DailyChallenge(
            date=str(datetime.date.today()),
            scenario=mock_scenario,
            flashcards=mock_flashcards
        )
        app_state.current_flashcard_index = 0
        app_state.conversations = {}
        app_state.initialize_conversation(0)
        
        print("Mock data loaded successfully.", flush=True)


@api_bp.route('/scenario', methods=['GET'])
def get_scenario():
    scenario = app_state.get_scenario()
    if scenario:
        print(f"DEBUG - Scenario data: {scenario.title}", flush=True)
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
    print(f"pergunta do usuário: {question}")
    
    idx = app_state.current_flashcard_index
    
    # Ensure conversation exists (should be handled by load/next, but safety check)
    if idx not in app_state.conversations:
         app_state.initialize_conversation(idx)
    
    # Save user message
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


def init_app_state():
    """Initialize the application state on startup."""
    print("Initializing application state...", flush=True)
    load_daily_challenge()
