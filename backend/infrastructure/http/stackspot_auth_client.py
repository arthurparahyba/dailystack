"""StackSpot Authentication Client - Handles OAuth authentication."""
import os
import requests
import time
from typing import Optional


class StackSpotAuthClient:
    """Client for StackSpot OAuth authentication."""
    
    def __init__(self):
        self.client_id = os.environ.get("STK_CLIENT_ID")
        self.client_key = os.environ.get("STK_CLIENT_KEY")
        self.realm = os.environ.get("STK_REALM")
        self.token: Optional[str] = None
        self.token_expires_at: float = 0
    
    def reload_credentials(self) -> None:
        """Reload credentials from environment variables."""
        self.client_id = os.environ.get("STK_CLIENT_ID")
        self.client_key = os.environ.get("STK_CLIENT_KEY")
        self.realm = os.environ.get("STK_REALM")
    
    def get_token(self) -> Optional[str]:
        """
        Get a valid authentication token, refreshing if necessary.
        
        Returns:
            str: Valid JWT token or None if authentication fails
        """
        # Return cached token if still valid
        if self.token and self.token_expires_at > time.time():
            return self.token
        
        # Authenticate to get new token
        if not all([self.client_id, self.client_key, self.realm]):
            print("Missing credentials. Please set STK_CLIENT_ID, STK_CLIENT_KEY, and STK_REALM.")
            return None
        
        url = f"https://idm.stackspot.com/{self.realm}/oidc/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": self.client_id,
            "grant_type": "client_credentials",
            "client_secret": self.client_key
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.token = token_data["access_token"]
            # Set expiration with 60 second buffer
            self.token_expires_at = time.time() + token_data.get("expires_in", 300) - 60
            
            return self.token
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None
