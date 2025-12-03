"""
Acreditta API Handler
Manages communication with the Acreditta digital badge platform.
"""

import requests
from datetime import datetime
from typing import Dict, Any
import logging
import sys
import os

# Add parent directory to path for common module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common import BadgeIssueRequest, BadgeIssueResponse

logger = logging.getLogger(__name__)


class AcredittaAPIHandler:
    """Handler for Acreditta API interactions."""
    
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize Acreditta API handler.
        
        Args:
            api_url: Base URL for Acreditta API
            api_key: API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'CCA-System/1.0'
        })
    
    def issue_badge(self, request: BadgeIssueRequest) -> BadgeIssueResponse:
        """
        Issue a digital badge via Acreditta API.
        
        Args:
            request: BadgeIssueRequest with badge details
            
        Returns:
            BadgeIssueResponse with issued badge information
            
        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = f"{self.api_url}/badges/issue"
        
        # Prepare payload for Acreditta API
        payload = {
            "recipient": {
                "identifier": request.student_id,
                "type": "student_id"
            },
            "badge": {
                "template_id": request.badge_template_id,
                "title": request.badge_title,
            },
            "evidence": {
                "course_id": request.course_id,
                "evaluation_id": request.evaluation_id,
                "score": request.score,
                "rule_id": request.rule_id,
            },
            "metadata": request.metadata or {}
        }
        
        logger.info(f"Calling Acreditta API: {endpoint}")
        
        try:
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Map Acreditta response to our model
            return BadgeIssueResponse(
                badge_id=data.get("badge_id", data.get("id")),
                badge_url=data.get("badge_url", data.get("url")),
                issued_at=datetime.fromisoformat(data.get("issued_at", datetime.now().isoformat())),
                status=data.get("status", "issued")
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Acreditta API error: {str(e)}")
            raise
    
    def verify_badge(self, badge_id: str) -> Dict[str, Any]:
        """
        Verify a badge's authenticity.
        
        Args:
            badge_id: Badge identifier
            
        Returns:
            Badge verification information
        """
        endpoint = f"{self.api_url}/badges/{badge_id}/verify"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Badge verification error: {str(e)}")
            raise
    
    def revoke_badge(self, badge_id: str, reason: str) -> bool:
        """
        Revoke a previously issued badge.
        
        Args:
            badge_id: Badge identifier
            reason: Reason for revocation
            
        Returns:
            True if revocation successful
        """
        endpoint = f"{self.api_url}/badges/{badge_id}/revoke"
        
        payload = {"reason": reason}
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Badge revocation error: {str(e)}")
            raise
