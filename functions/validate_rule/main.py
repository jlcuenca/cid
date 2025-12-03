"""
Cloud Function: Validate Rule
Validates badge issuance rules from Firestore based on Moodle evaluation events.
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
    ValidationRequest,
    ValidationResult,
    FirestoreClient,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def validate_rule(request: Request):
    """
    HTTP Cloud Function to validate badge issuance rules.
    
    Args:
        request: Flask request object with JSON body containing:
            - student_id: str
            - course_id: str
            - evaluation_id: str
            - score: float
            - timestamp: str (ISO format)
    
    Returns:
        JSON response with ValidationResult
    """
    try:
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return jsonify({"error": "Invalid JSON body"}), 400
        
        logger.info(f"Validating rule for request: {request_json}")
        
        # Validate input using Pydantic
        validation_request = ValidationRequest(**request_json)
        
        # Initialize Firestore client
        config = Config.from_env()
        db_client = FirestoreClient(config)
        
        # Find matching rule
        matching_rule = db_client.get_matching_rule(
            course_id=validation_request.course_id,
            evaluation_id=validation_request.evaluation_id,
            score=validation_request.score
        )
        
        if matching_rule:
            logger.info(f"Found matching rule: {matching_rule.rule_id}")
            result = ValidationResult(
                is_valid=True,
                rule_id=matching_rule.rule_id,
                badge_template_id=matching_rule.badge_template_id,
                badge_title=matching_rule.badge_title,
                reason=f"Score {validation_request.score} meets minimum {matching_rule.min_score}"
            )
        else:
            logger.info("No matching rule found")
            result = ValidationResult(
                is_valid=False,
                reason="No rule matched the criteria"
            )
        
        return jsonify(result.model_dump(mode="json")), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
