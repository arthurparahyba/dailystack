"""Use case: Authenticate User."""
from typing import Optional
from backend.infrastructure.http.stackspot_auth_client import StackSpotAuthClient


class AuthenticateUser:
    """
    Use case for authenticating the user/application.
    """
    
    def __init__(self, auth_client: StackSpotAuthClient):
        self.auth_client = auth_client
    
    def execute(self) -> Optional[str]:
        """
        Execute the use case.
        
        Returns:
            str: Auth token if successful, None otherwise
        """
        return self.auth_client.get_token()
    
    def reload_credentials(self) -> None:
        """Reload credentials from environment."""
        self.auth_client.reload_credentials()
