"""
Development script to run only the Flask backend server.
Use this for local development when you want to run the frontend separately.
"""
import threading
import sys
import os

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api import api_bp, load_daily_challenge
from flask import Flask

# Initialize Flask
server = Flask(__name__, static_folder='../frontend/build', static_url_path='')
server.register_blueprint(api_bp, url_prefix='/api')

@server.route('/')
def index():
    return server.send_static_file('index.html')

if __name__ == '__main__':
    # Load initial data in background
    print("Starting background data load...")
    t_load = threading.Thread(target=load_daily_challenge, daemon=True)
    t_load.start()
    
    # Run Flask server with CORS enabled for development
    from flask_cors import CORS
    CORS(server)  # Enable CORS for frontend dev server
    
    print("Backend server running on http://127.0.0.1:5000")
    server.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
