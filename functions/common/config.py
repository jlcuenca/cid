"""
Common configuration module for CCA Cloud Functions.
Handles environment variables and Secret Manager integration.
"""

import os
from dataclasses import dataclass
from typing import Optional
from google.cloud import secretmanager


@dataclass
class Config:
    """Application configuration."""
    project_id: str
    environment: str
    firestore_collection_rules: str = "reglas_emision"
    firestore_collection_events: str = "registro_evento"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            project_id=os.environ.get("GCP_PROJECT_ID", ""),
            environment=os.environ.get("ENVIRONMENT", "dev"),
        )


class SecretManager:
    """Helper class for accessing secrets from Google Secret Manager."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()
    
    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Retrieve a secret value from Secret Manager.
        
        Args:
            secret_id: The ID of the secret
            version: The version of the secret (default: "latest")
            
        Returns:
            The secret value as a string
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
        response = self.client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")


def get_secret(secret_id: str) -> str:
    """
    Convenience function to get a secret value.
    
    Args:
        secret_id: The ID of the secret
        
    Returns:
        The secret value as a string
    """
    config = Config.from_env()
    sm = SecretManager(config.project_id)
    return sm.get_secret(secret_id)
