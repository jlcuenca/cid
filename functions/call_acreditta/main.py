"""
Cloud Function: Call Acreditta
Calls the Acreditta API to issue digital badges.
"""

import functions_framework
from flask import Request, jsonify
import logging
import sys
import os

# Add parent directory to path for common module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common import (
    Config,
    BadgeIssueRequest,
    BadgeIssueResponse,
    get_secret,
)
from acreditta_handler import AcredittaAPIHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def call_acreditta(request: Request):
    """
    HTTP Cloud Function to issue badges via Acreditta API.
    
    Args:
        request: Flask request object with JSON body containing:
            - student_id: str
            - badge_template_id: str
            - badge_title: str
            - course_id: str
            - evaluation_id: str
            - score: float
            - rule_id: str
    
    Returns:
        JSON response with BadgeIssueResponse
    """
    try:
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return jsonify({"error": "Invalid JSON body"}), 400
        
        logger.info(f"Issuing badge for request: {request_json}")
        
        # Validate input using Pydantic
        badge_request = BadgeIssueRequest(**request_json)
        
        # Get Acreditta API credentials from Secret Manager
        config = Config.from_env()
        api_key = get_secret(os.environ.get("ACREDITTA_SECRET_ID", "acreditta-api-key"))
        api_url = os.environ.get("ACREDITTA_API_URL", "https://api.acreditta.com/v1")
        
        # Initialize Acreditta handler
        acreditta = AcredittaAPIHandler(api_url=api_url, api_key=api_key)
        
        # Issue badge
        badge_response = acreditta.issue_badge(badge_request)
        
        logger.info(f"Badge issued successfully: {badge_response.badge_id}")
        
        return jsonify(badge_response.model_dump(mode="json")), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
