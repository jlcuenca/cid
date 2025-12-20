"""
Cloud Function: Analyze Syllabus
Uses AI to extract metadata from Moodle course content.
"""

import functions_framework
from flask import Request, jsonify
import logging
import sys
import os

# Add parent directory to path for common module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.moodle_client import MoodleClient
from common.ai_service import AIService
from common.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def analyze_syllabus(request: Request):
    """
    HTTP Cloud Function to analyze a Moodle course syllabus and suggest metadata.
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
        if not request_json or 'course_id' not in request_json:
            return (jsonify({"error": "Missing course_id"}), 400, headers)
        
        course_id = request_json['course_id']
        logger.info(f"Analyzing syllabus for course: {course_id}")
        
        # Initialize clients
        config = Config.from_env()
        moodle = MoodleClient(api_url="https://moodle.example.com", token="mock-token")
        ai_service = AIService()
        
        # 1. Fetch course details
        course = moodle.get_course_details(course_id)
        
        # 2. Perform AI Analysis
        suggested_metadata = ai_service.analyze_course_content(course)
        
        return (jsonify({
            "metadata": suggested_metadata.model_dump(mode="json"),
            "course": course.model_dump(mode="json")
        }), 200, headers)
        
    except Exception as e:
        logger.error(f"Error analyzing syllabus: {str(e)}", exc_info=True)
        return (jsonify({"error": str(e)}), 500, headers)
