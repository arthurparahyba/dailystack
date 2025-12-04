import os
import threading
import time
import sys
from flask import Flask
import webview
from backend.api import api_bp, init_app_state, app_state

# Initialize Flask
server = Flask(__name__, static_folder='frontend/build', static_url_path='')
server.register_blueprint(api_bp, url_prefix='/api')

@server.route('/')
def index():
    return server.send_static_file('index.html')

def verify_date_loop():
    """Background thread to check for date changes."""
    while True:
        time.sleep(300)  # Check every 5 minutes
        # In a real app, we would check if the date has changed.
        # For this prototype, we'll just print a heartbeat.
        #print("Checking date...", file=sys.stderr)
        # Logic to reload if date changed:
        # current_day = str(datetime.date.today())
        # if current_day != app_state.get_current_date():
        #     init_app_state()

def start_server():
    """Starts the Flask server."""
    # Run on a specific port, e.g., 5000. 
    # Threaded=True is important for pywebview to work smoothly if not using the built-in server bridge in a complex way,
    # but pywebview often runs the server in a separate thread or process.
    # Here we run Flask in a thread.
    server.run(host='127.0.0.1', port=5000, threaded=True)

if __name__ == '__main__':
    # Detect if running as PyInstaller bundle
    is_packaged = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    
    # Load initial data in background
    print("Starting background data load...", file=sys.stderr)
    t_load = threading.Thread(target=init_app_state, daemon=True)
    t_load.start()

    # Start date verification thread
    t = threading.Thread(target=verify_date_loop, daemon=True)
    t.start()

    # Start Flask in a separate thread
    t_server = threading.Thread(target=start_server, daemon=True)
    t_server.start()

    # Create WebView window
    webview.create_window('Dailystack', 'http://127.0.0.1:5000', width=1200, height=800, resizable=True)
    # Disable debug mode when running as packaged executable
    webview.start(debug=not is_packaged)
