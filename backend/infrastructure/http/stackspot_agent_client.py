"""StackSpot Agent Management Client."""
import sys
import re
from typing import Optional
from backend.domain.entities import Agent, AgentCreationRequest
from .stackspot_auth_client import StackSpotAuthClient


class StackSpotAgentClient:
    """Client for StackSpot Agent Management API."""
    
    def __init__(self, auth_client: StackSpotAuthClient):
        self.auth_client = auth_client
        self.base_url = "https://genai-agent-tools-api.stackspot.com/v1/agents"
    
    def get_by_name(self, agent_name: str) -> Optional[Agent]:
        """
        Get agent by name.
        
        Args:
            agent_name: Name of the agent to search for
            
        Returns:
            Agent object if found, None otherwise
        """
        import requests
        
        token = self.auth_client.get_token()
        if not token:
            return None
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(f"{self.base_url}?visibility=personal", headers=headers)
            response.raise_for_status()
            
            agents = response.json()
            for agent in agents:
                if agent.get('name') == agent_name:
                    print(f"Found agent '{agent_name}' with ID: {agent['id']}", file=sys.stderr)
                    return Agent(id=agent['id'], name=agent['name'])
            
            print(f"Agent '{agent_name}' not found.", file=sys.stderr)
            return None
            
        except Exception as e:
            print(f"Error getting agent by name: {e}", file=sys.stderr)
            return None
    
    def create(self, request: AgentCreationRequest) -> Optional[Agent]:
        """
        Create a new agent.
        
        Args:
            request: AgentCreationRequest with agent configuration
            
        Returns:
            Agent object if created successfully, None otherwise
        """
        import requests
        import json
        
        token = self.auth_client.get_token()
        if not token:
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Generate URL-safe slug
        slug = re.sub(r'[^a-z0-9]+', '-', request.name.lower()).strip('-')
        
        body = {
            "type": "CONVERSATIONAL",
            "name": request.name,
            "system_prompt": request.prompt,
            "suggested_prompts": [],
            "slug": slug,
            "knowledge_sources_config": {
                "max_number_of_kos": 4,
                "relevancy_threshold": 40,
                "knowledge_sources": []
            },
            "tools": [],
            "mode": "autonomous",
            "enabled_tools": True,
            "memory": "buffer",
            "model_id": "01JZTZQFP4QHTB1500FFW5KT08",
            "model_name": "gpt-4.1",
            "llm_settings": {
                "temperature": 0.4,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            },
            "builtin_tools_ids": [],
            "custom_tools": []
        }
        
        # Add structured output if provided
        if request.output_schema:
            body["enabled_structured_outputs"] = True
            body["structured_output"] = request.output_schema
        else:
            body["enabled_structured_outputs"] = False
            body["structured_output"] = None
        
        try:
            response = requests.post(self.base_url, headers=headers, json=body)
            
            if response.status_code == 201:
                agent_data = response.json()
                agent_id = agent_data["id"]
                print(f"Agent created successfully with ID: {agent_id}", file=sys.stderr)
                return Agent(id=agent_id, name=request.name)
            else:
                print(f"Failed to create agent: {response.status_code}", file=sys.stderr)
                print(f"Response: {response.text}", file=sys.stderr)
                return None
                
        except Exception as e:
            print(f"Error creating agent: {e}", file=sys.stderr)
            return None
