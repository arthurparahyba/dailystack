"""Credentials validation endpoint."""
import os
from flask import Blueprint, jsonify

credentials_bp = Blueprint('credentials', __name__)

@credentials_bp.route('/check-credentials', methods=['GET'])
def check_credentials():
    """Check if required environment variables are set."""
    client_id = os.environ.get("STK_CLIENT_ID")
    client_key = os.environ.get("STK_CLIENT_KEY")
    realm = os.environ.get("STK_REALM")
    
    missing = []
    if not client_id:
        missing.append("STK_CLIENT_ID")
    if not client_key:
        missing.append("STK_CLIENT_KEY")
    if not realm:
        missing.append("STK_REALM")
    
    return jsonify({
        "configured": len(missing) == 0,
        "missing": missing
    })
