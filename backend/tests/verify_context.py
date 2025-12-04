import sys
import os
from dataclasses import asdict

# Add the workspace root to python path
sys.path.append(os.getcwd())

try:
    from backend.domain.entities import Scenario
    print("Successfully imported Scenario")
    
    # Test instantiation
    try:
        scenario = Scenario(title="Test", description="Test Desc", context="Should fail")
        print("ERROR: Scenario accepted 'context' argument")
        sys.exit(1)
    except TypeError:
        print("SUCCESS: Scenario correctly rejected 'context' argument")
        
    scenario = Scenario(title="Test", description="Test Desc")
    print("Successfully instantiated Scenario without context")
    
    # Test to_dict
    data = scenario.to_dict()
    if 'context' in data:
        print("ERROR: 'context' found in to_dict output")
        sys.exit(1)
    else:
        print("SUCCESS: 'context' NOT found in to_dict output")
        
    # Test from_dict with extra field (should be ignored)
    input_data = {
        'title': 'From Dict',
        'problem_description': 'Desc',
        'architectural_overview': 'Context should be ignored'
    }
    scenario_from_dict = Scenario.from_dict(input_data)
    if hasattr(scenario_from_dict, 'context'):
        print("ERROR: Scenario object has 'context' attribute")
        sys.exit(1)
    else:
        print("SUCCESS: Scenario object does NOT have 'context' attribute")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
