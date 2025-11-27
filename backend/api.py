from flask import Blueprint, jsonify, request, Response, stream_with_context
import requests
import datetime
import os
import json
import uuid

api_bp = Blueprint('api', __name__)

from backend.client import StackSpotClient

# Global State
app_state = {
    "current_date": None,
    "scenario": None,
    "flashcards": [],
    "current_flashcard_index": 0,
    "current_conversation_id": None,
    "is_first_message_for_card": True,
    "conversations": {} # { flashcard_index: { "id": "...", "messages": [], "is_first": bool } }
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
        app_state["conversations"] = {} # Reset conversations on new challenge
        
        # Initialize conversation for first card
        conv_id = uuid.uuid4().hex[:26]
        app_state["current_conversation_id"] = conv_id
        app_state["is_first_message_for_card"] = True
        app_state["conversations"][0] = {
            "id": conv_id,
            "messages": [],
            "is_first": True
        }
        
        print("Daily challenge loaded successfully.", flush=True)
    else:
        print("Failed to load daily challenge. Using fallback/empty state.", flush=True)


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
    
    idx = app_state["current_flashcard_index"]
    
    # Check if we have a conversation for this card
    if idx in app_state["conversations"]:
        # Restore conversation
        conv_data = app_state["conversations"][idx]
        app_state["current_conversation_id"] = conv_data["id"]
        app_state["is_first_message_for_card"] = conv_data["is_first"]
    else:
        # Create new conversation
        conv_id = uuid.uuid4().hex[:26]
        app_state["current_conversation_id"] = conv_id
        app_state["is_first_message_for_card"] = True
        app_state["conversations"][idx] = {
            "id": conv_id,
            "messages": [],
            "is_first": True
        }
        
    # Return the new current flashcard
    return get_current_flashcard()

@api_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    idx = app_state["current_flashcard_index"]
    if idx in app_state["conversations"]:
        return jsonify(app_state["conversations"][idx]["messages"])
    return jsonify([])

@api_bp.route('/ask-llm', methods=['POST'])
def ask_llm():
    data = request.json
    question = data.get("question")
    print(f"pergunta do usuário: {question}")
    
    idx = app_state["current_flashcard_index"]
    
    # Ensure conversation exists (should be handled by load/next, but safety check)
    if idx not in app_state["conversations"]:
         conv_id = uuid.uuid4().hex[:26]
         app_state["conversations"][idx] = {
            "id": conv_id,
            "messages": [],
            "is_first": True
         }
         app_state["current_conversation_id"] = conv_id
         app_state["is_first_message_for_card"] = True
    
    # Save user message
    app_state["conversations"][idx]["messages"].append({"role": "user", "content": question})
    
    if not app_state["current_conversation_id"]:
        app_state["current_conversation_id"] = app_state["conversations"][idx]["id"]
    print(f"id da conversa: {app_state['current_conversation_id']}")
    
    # Build user prompt
    if app_state["is_first_message_for_card"] and app_state["flashcards"]:
        if idx < len(app_state["flashcards"]):
            flashcard = app_state["flashcards"][idx]
            flashcard_question = flashcard.get("question", "")
            flashcard_answer = flashcard.get("detailed_explanation", "")
            
            user_prompt = f"dada a questão: {flashcard_question} e dada a resposta {flashcard_answer} Responda a mensagem do usuário: {question}"
            app_state["is_first_message_for_card"] = False
            app_state["conversations"][idx]["is_first"] = False
        else:
            user_prompt = question
    else:
        user_prompt = question
    
    def generate():
        full_answer = ""
        for event_data in client.chat_with_agent(app_state["current_conversation_id"], user_prompt):
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
            app_state["conversations"][idx]["messages"].append({"role": "bot", "content": full_answer})
    
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
