"""
Cloud Function: Issue Badge OB3
Generates an Open Badges 3.0 compliant JSON-LD assertion.
"""

import functions_framework
from flask import Request, jsonify
import logging
import sys
import os

# Add parent directory to path for common module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common import BadgeService, Competency, EvidenceMapping, EvidenceType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def issue_badge_ob3(request: Request):
    """
    HTTP Cloud Function to generate an OB3 badge.
    """
    try:
        # Handle CORS
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }
            return ('', 204, headers)

        # Set CORS headers for the main request
        headers = {
            'Access-Control-Allow-Origin': '*'
        }

        request_json = request.get_json(silent=True)
        if not request_json:
            return (jsonify({"error": "Missing request body"}), 400, headers)
        
        # Extract data
        competency_data = request_json.get('competency')
        student_email = request_json.get('student_email', 'student@example.edu')
        evidence_data = request_json.get('evidence_mappings', [])
        narratives = request_json.get('narratives', [])

        if not competency_data:
            return (jsonify({"error": "Missing competency data"}), 400, headers)

        # Initialize Badge Service
        badge_service = BadgeService(
            issuer_id="https://cid.example.edu/issuers/cid-platform",
            issuer_name="CID Pedagogical Platform",
            issuer_url="https://cid.example.edu"
        )

        # Reconstruct models
        competency = Competency(**competency_data)
        evidence_mappings = [EvidenceMapping(**m) for m in evidence_data]

        # Generate OB3 Package
        badge_package = badge_service.generate_complete_badge_package(
            competency=competency,
            student_email=student_email,
            evidence_mappings=evidence_mappings,
            narratives=narratives
        )

        return (jsonify(badge_package), 200, headers)
        
    except Exception as e:
        logger.error(f"Error issuing OB3 badge: {str(e)}", exc_info=True)
        return (jsonify({"error": str(e)}), 500, headers)
