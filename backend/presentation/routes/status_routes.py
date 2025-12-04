"""Status Routes."""
from flask import Blueprint, jsonify
from backend.presentation.dependencies import container

status_bp = Blueprint('status', __name__)

@status_bp.route('/status', methods=['GET'])
def get_status():
    """Returns the current loading status and data availability."""
    state = container.state_repository.get_state()
    return jsonify({
        "loading": state.is_loading,
        "has_data": state.daily_challenge is not None,
        "error": state.error
    })
