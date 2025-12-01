"""
Test script for the refactored backend client.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.client import StackSpotClient
from backend.models import DailyChallenge, Flashcard, Scenario

def test_models():
    """Test the data models."""
    print("Testing data models...")
    
    # Test Flashcard
    flashcard_data = {
        "question": "What is Python?",
        "answer": "A programming language",
        "category": "Programming",
        "detailed_explanation": "Python is a high-level programming language.",
        "code_example": "print('Hello, World!')"
    }
    flashcard = Flashcard.from_dict(flashcard_data)
    assert flashcard.question == "What is Python?"
    assert flashcard.to_dict() == flashcard_data
    print("[OK] Flashcard model works correctly")
    
    # Test Scenario
    scenario_data = {
        "title": "Test Scenario",
        "description": "A test scenario",
        "context": "Testing context"
    }
    scenario = Scenario.from_dict(scenario_data)
    assert scenario.title == "Test Scenario"
    assert scenario.to_dict() == scenario_data
    print("[OK] Scenario model works correctly")
    
    # Test DailyChallenge
    challenge_data = {
        "date": "2025-11-29",
        "scenario": scenario_data,
        "flashcards": [flashcard_data]
    }
    challenge = DailyChallenge.from_dict(challenge_data)
    assert challenge.date == "2025-11-29"
    assert len(challenge.flashcards) == 1
    assert challenge.flashcards[0].question == "What is Python?"
    print("[OK] DailyChallenge model works correctly")
    
    print("\n[OK] All model tests passed!\n")

def test_client():
    """Test the StackSpot client."""
    print("Testing StackSpot client...")
    
    client = StackSpotClient()
    
    # Check if credentials are set
    if not all([client.client_id, client.client_key, client.realm]):
        print("[WARN] Credentials not set. Skipping client test.")
        print("       Set STK_CLIENT_ID, STK_CLIENT_KEY, and STK_REALM to test.")
        return
    
    # Test get_daily_challenge
    print("Fetching daily challenge...")
    daily_challenge = client.get_daily_challenge()
    
    if daily_challenge:
        print(f"[OK] Got daily challenge for date: {daily_challenge.date}")
        print(f"     Scenario: {daily_challenge.scenario.title}")
        print(f"     Flashcards: {len(daily_challenge.flashcards)}")
        
        if daily_challenge.flashcards:
            first_card = daily_challenge.flashcards[0]
            print(f"     First card question: {first_card.question[:50]}...")
    else:
        print("[FAIL] Failed to get daily challenge")

if __name__ == "__main__":
    print("=" * 60)
    print("Backend Refactoring Test Suite")
    print("=" * 60)
    print()
    
    test_models()
    test_client()
    
    print()
    print("=" * 60)
    print("Test suite completed!")
    print("=" * 60)

    
    print()
    print("=" * 60)
    print("Test suite completed!")
    print("=" * 60)
