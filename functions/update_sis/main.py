"""
Cloud Function: Update SIS
Updates the Student Information System and logs audit events.
"""

import functions_framework
from flask import Request, jsonify
import logging
import sys
import os
from datetime import datetime
import uuid

# Add parent directory to path for common module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common import (
    Config,
    SISUpdateRequest,
    SISUpdateResponse,
    AuditEvent,
    FirestoreClient,
    get_secret,
)
from sis_connector import SISConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@functions_framework.http
def update_sis(request: Request):
    """
    HTTP Cloud Function to update SIS and log audit events.
    
    Args:
        request: Flask request object with JSON body containing:
            - student_id: str
            - badge_id: str
            - badge_url: str
            - badge_template_id: str
            - badge_title: str
            - course_id: str
            - evaluation_id: str
            - score: float
            - rule_id: str
            - issued_at: str (ISO format)
            - workflow_execution_id: str (optional)
    
    Returns:
        JSON response with SISUpdateResponse
    """
    try:
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return jsonify({"error": "Invalid JSON body"}), 400
        
        logger.info(f"Updating SIS for request: {request_json}")
        
        # Validate input using Pydantic
        sis_request = SISUpdateRequest(**request_json)
        
        # Initialize Firestore client for audit logging
        config = Config.from_env()
        db_client = FirestoreClient(config)
        
        # Get SIS database credentials from Secret Manager
        sis_user = get_secret(os.environ.get("SIS_USER_SECRET_ID", "sis-db-user"))
        sis_pass = get_secret(os.environ.get("SIS_PASS_SECRET_ID", "sis-db-pass"))
        sis_host = os.environ.get("SIS_DB_HOST", "")
        sis_db = os.environ.get("SIS_DB_NAME", "sis_production")
        
        # Initialize SIS connector
        sis = SISConnector(
            host=sis_host,
            database=sis_db,
            user=sis_user,
            password=sis_pass
        )
        
        # Update SIS database
        sis_updated = False
        if sis_host:  # Only update if SIS host is configured
            try:
                sis.update_student_badge(
                    student_id=sis_request.student_id,
                    badge_id=sis_request.badge_id,
                    badge_url=sis_request.badge_url,
                    badge_title=sis_request.badge_title
                )
                sis_updated = True
                logger.info(f"SIS updated for student {sis_request.student_id}")
            except Exception as e:
                logger.warning(f"SIS update failed: {str(e)}")
                # Continue to log audit event even if SIS update fails
        else:
            logger.info("SIS host not configured, skipping SIS update")
        
        # Create audit event
        event_id = str(uuid.uuid4())
        audit_event = AuditEvent(
            event_id=event_id,
            event_type="badge_issued",
            student_id=sis_request.student_id,
            badge_id=sis_request.badge_id,
            badge_template_id=sis_request.badge_template_id,
            course_id=sis_request.course_id,
            evaluation_id=sis_request.evaluation_id,
            score=sis_request.score,
            rule_id=sis_request.rule_id,
            workflow_execution_id=sis_request.workflow_execution_id,
            timestamp=datetime.now(),
            metadata={
                "badge_url": sis_request.badge_url,
                "badge_title": sis_request.badge_title,
                "issued_at": sis_request.issued_at.isoformat(),
                "sis_updated": sis_updated
            }
        )
        
        # Log audit event to Firestore
        logged_event_id = db_client.log_event(audit_event)
        logger.info(f"Audit event logged: {logged_event_id}")
        
        # Prepare response
        response = SISUpdateResponse(
            updated=sis_updated,
            event_id=event_id,
            message="SIS updated and event logged successfully" if sis_updated else "Event logged (SIS update skipped)"
        )
        
        return jsonify(response.model_dump(mode="json")), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
