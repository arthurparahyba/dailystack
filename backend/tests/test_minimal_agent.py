import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.client import StackSpotClient
from backend.models import AgentCreationRequest

def test_minimal_agent():
    print("Testing minimal agent creation (no output_schema)...")
    client = StackSpotClient()
    
    # Create agent without output_schema
    request = AgentCreationRequest(
        name="Test Agent Minimal",
        description="Test agent without schema",
        prompt="You are a helpful assistant.",
        output_schema=None
    )
    
    print(f"\nAttempting to create agent: {request.name}")
    agent = client.create_agent(request)
    
    if agent:
        print(f"\nSUCCESS! Agent created with ID: {agent.id}")
        print("Now testing with output_schema...")
        
        # Try with schema
        schema_request = AgentCreationRequest(
            name="Test Agent With Schema",
            description="Test agent with schema",
            prompt="You are a helpful assistant.",
            output_schema={"type": "object", "properties": {"answer": {"type": "string"}}}
        )
        
        agent2 = client.create_agent(schema_request)
        if agent2:
            print(f"SUCCESS with schema! Agent ID: {agent2.id}")
        else:
            print("FAILED with schema")
    else:
        print("\nFAILED: Could not create minimal agent")

if __name__ == "__main__":
    test_minimal_agent()
