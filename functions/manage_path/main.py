"""
Cloud Function: Manage Path
Handles CRUD operations for Learning Paths in Firestore.
"""

import functions_framework
from flask import Request, jsonify
import logging
import sys
import os
from datetime import datetime

# Add parent directory to path for common module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common import (
    Config,
    PedagogicalDBClient,
    LearningPath
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def manage_path(request: Request):
    """
    HTTP Cloud Function to manage learning paths.
    """
    try:
        # Handle CORS
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }
            return ('', 204, headers)

        # Set CORS headers for the main request
        headers = {
            'Access-Control-Allow-Origin': '*'
        }

        config = Config.from_env()
        db = PedagogicalDBClient(config)

        if request.method == 'GET':
            path_id = request.args.get('path_id')
            if not path_id:
                return (jsonify({"error": "Missing path_id"}), 400, headers)
            
            path = db.get_learning_path(path_id)
            if not path:
                return (jsonify({"error": "Path not found"}), 404, headers)
            
            return (jsonify(path.model_dump(mode="json")), 200, headers)

        elif request.method == 'POST':
            request_json = request.get_json(silent=True)
            if not request_json:
                return (jsonify({"error": "Invalid JSON"}), 400, headers)
            
            action = request_json.get('action', 'save')
            
            if action == 'save':
                path_data = request_json.get('path')
                if not path_data:
                    return (jsonify({"error": "Missing path data"}), 400, headers)
                
                # Add timestamps if missing
                if 'created_at' not in path_data:
                    path_data['created_at'] = datetime.now().isoformat()
                path_data['updated_at'] = datetime.now().isoformat()
                
                path = LearningPath(**path_data)
                db.create_learning_path(path)
                
                return (jsonify({"message": "Path saved successfully", "path_id": path.id}), 200, headers)
            
            return (jsonify({"error": f"Unsupported action: {action}"}), 400, headers)

        return (jsonify({"error": "Method not allowed"}), 405, headers)

    except Exception as e:
        logger.error(f"Error in manage_path: {str(e)}", exc_info=True)
        return (jsonify({"error": str(e)}), 500, headers)
