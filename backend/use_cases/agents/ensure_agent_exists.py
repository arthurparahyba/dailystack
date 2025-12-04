"""Use case: Ensure Agent Exists."""
from typing import Optional
from backend.domain.entities import Agent, AgentCreationRequest
from backend.infrastructure.http.stackspot_agent_client import StackSpotAgentClient


class EnsureAgentExists:
    """
    Use case for ensuring an agent exists, creating it if necessary.
    
    This encapsulates the business logic of checking for an agent
    and creating it with the proper configuration if not found.
    """
    
    def __init__(
        self,
        agent_client: StackSpotAgentClient,
        agent_name: str,
        agent_description: str,
        agent_prompt: str,
        output_schema: Optional[dict] = None
    ):
        self.agent_client = agent_client
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.agent_prompt = agent_prompt
        self.output_schema = output_schema
        self._cached_agent_id: Optional[str] = None
    
    def execute(self) -> Optional[str]:
        """
        Execute the use case.
        
        Returns:
            Agent ID if successful, None otherwise
        """
        # Return cached ID if available
        if self._cached_agent_id:
            return self._cached_agent_id
        
        # Try to get existing agent
        agent = self.agent_client.get_by_name(self.agent_name)
        
        if agent:
            self._cached_agent_id = agent.id
            return self._cached_agent_id
        
        # Agent doesn't exist, create it
        print(f"Agent '{self.agent_name}' not found. Creating...")
        
        request = AgentCreationRequest(
            name=self.agent_name,
            description=self.agent_description,
            prompt=self.agent_prompt,
            output_schema=self.output_schema
        )
        
        agent = self.agent_client.create(request)
        
        if agent:
            self._cached_agent_id = agent.id
            return self._cached_agent_id
        
        return None
