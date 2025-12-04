"""Flashcard Routes."""
from flask import Blueprint, jsonify
from backend.presentation.dependencies import container

flashcard_bp = Blueprint('flashcard', __name__)

@flashcard_bp.route('/scenario', methods=['GET'])
def get_scenario():
    state = container.state_repository.get_state()
    scenario = state.get_scenario()
    if scenario:
        return jsonify(scenario.to_dict())
    return jsonify({})

@flashcard_bp.route('/flashcard/current', methods=['GET'])
def get_current_flashcard():
    state = container.state_repository.get_state()
    flashcard = state.get_current_flashcard()
    if flashcard:
        return jsonify(flashcard.to_dict())
    return jsonify({})

@flashcard_bp.route('/flashcard/next', methods=['POST'])
def next_flashcard():
    state = container.state_repository.get_state()
    flashcard = state.next_flashcard()
    if flashcard:
        return jsonify(flashcard.to_dict())
    return jsonify({"status": "no flashcards"})
