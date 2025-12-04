"""Use case: Get Daily Challenge."""
from typing import Optional
from backend.domain.entities import DailyChallenge
from backend.infrastructure.http.stackspot_challenge_client import StackSpotChallengeClient
from backend.use_cases.agents.ensure_agent_exists import EnsureAgentExists


class GetDailyChallenge:
    """
    Use case for retrieving the daily challenge.
    
    Orchestrates the flow of ensuring the agent exists and then
    fetching the challenge from it.
    """
    
    def __init__(
        self,
        challenge_client: StackSpotChallengeClient,
        ensure_agent_use_case: EnsureAgentExists
    ):
        self.challenge_client = challenge_client
        self.ensure_agent = ensure_agent_use_case
    
    def execute(self) -> Optional[DailyChallenge]:
        """
        Execute the use case.
        
        Returns:
            DailyChallenge object if successful, None otherwise
        """
        # Step 1: Ensure agent exists and get its ID
        agent_id = self.ensure_agent.execute()
        
        if not agent_id:
            print("Could not get agent ID for daily challenge.")
            return None
            
        # Step 2: Fetch challenge using the agent ID
        return self.challenge_client.get_daily_challenge(agent_id)
