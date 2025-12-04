import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from backend.domain.entities import AppState

def test_ulid_generation():
    app_state = AppState()
    conv_id = app_state.initialize_conversation(0)
    
    print(f"Generated ID: {conv_id}")
    print(f"Length: {len(conv_id)}")
    
    # Check length
    if len(conv_id) != 26:
        print("FAIL: Length is not 26")
        return
        
    # Check characters (Crockford's Base32)
    valid_chars = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    for char in conv_id:
        if char not in valid_chars:
            print(f"FAIL: Invalid character '{char}'")
            return
            
    print("SUCCESS: ID format appears valid")

if __name__ == "__main__":
    test_ulid_generation()
