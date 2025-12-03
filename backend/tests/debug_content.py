import sys
import os
import io
import time
import random

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add current directory to path so we can import backend modules
sys.path.append(os.getcwd())

from backend.client import StackSpotClient

# Crockford's Base32
CROCKFORD_BASE32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

def generate_ulid():
    """Generates a ULID-like string (26 chars)."""
    t = int(time.time() * 1000)
    
    # Timestamp (10 chars)
    timestamp_str = ""
    for _ in range(10):
        timestamp_str = CROCKFORD_BASE32[t % 32] + timestamp_str
        t //= 32
        
    # Randomness (16 chars)
    random_str = ""
    for _ in range(16):
        random_str += random.choice(CROCKFORD_BASE32)
        
    return timestamp_str + random_str

def test_chat():
    client = StackSpotClient()
    
    # Test 2: Use a ULID-like string
    conv_id = generate_ulid()
    print(f"\n--- Testing with ULID-like ID: {conv_id} ---")
    
    user_prompt = "oi"
    print(f"Sending prompt: {user_prompt}")
    
    try:
        # We need to consume the generator
        for response in client.chat_with_agent(conv_id, user_prompt):
            if "answer" in response:
                print(f"Success! Answer received: {response['answer'][:50]}...")
                break
            elif "error" in response:
                print(f"Error received: {response['error']}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_chat()
