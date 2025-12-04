"""Chat Routes."""
import json
from flask import Blueprint, jsonify, request, Response, stream_with_context
from backend.presentation.dependencies import container

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    state = container.state_repository.get_state()
    idx = state.current_flashcard_index
    conversation = state.get_conversation(idx)
    if conversation:
        return jsonify(conversation.messages)
    return jsonify([])

@chat_bp.route('/ask-llm', methods=['POST'])
def ask_llm():
    data = request.json
    question = data.get("question")
    is_hidden = data.get("hidden", False)
    
    state = container.state_repository.get_state()
    idx = state.current_flashcard_index
    
    # Ensure conversation exists
    if idx not in state.conversations:
         state.initialize_conversation(idx)
    
    # Save user message ONLY if not hidden
    if not is_hidden:
        state.conversations[idx].messages.append({"role": "user", "content": question})
    
    if not state.current_conversation_id:
        state.current_conversation_id = state.conversations[idx].id
    
    # Build user prompt
    if state.is_first_message_for_card:
        flashcard = state.get_current_flashcard()
        if flashcard:
            flashcard_question = flashcard.question
            flashcard_answer = flashcard.detailed_explanation or flashcard.answer
            
            user_prompt = f"dada a questão: {flashcard_question} e dada a resposta {flashcard_answer} Responda a mensagem do usuário: {question}"
            state.is_first_message_for_card = False
            state.conversations[idx].is_first = False
        else:
            user_prompt = question
    else:
        user_prompt = question
    
    def generate():
        full_answer = ""
        # Use the chat use case from container
        for event_data in container.chat_with_agent.execute(state.current_conversation_id, user_prompt):
            if "answer" in event_data:
                answer_chunk = event_data["answer"]
                full_answer += answer_chunk
                chunk = f"data: {json.dumps(event_data)}\n\n"
                yield chunk
            elif "error" in event_data:
                chunk = f"data: {json.dumps(event_data)}\n\n"
                yield chunk
                break
        
        # Save bot message after streaming is complete
        if full_answer:
            state.conversations[idx].messages.append({"role": "bot", "content": full_answer})
    
    return Response(stream_with_context(generate()), content_type='text/event-stream')
