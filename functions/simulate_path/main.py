"""
Cloud Function: Simulate Path
Simulates a student's journey through a learning path to verify rules and triggers.
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
    RuleEvaluator,
    MoodleClient,
    SimulationResult,
    EvidenceVerifier
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def simulate_path(request: Request):
    """
    HTTP Cloud Function to simulate a learning path for a ghost student.
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
        if not request_json or 'path_id' not in request_json:
            return (jsonify({"error": "Missing path_id"}), 400, headers)
        
        path_id = request_json['path_id']
        student_id = request_json.get('student_id', 'ghost-student-001')
        
        logger.info(f"Simulating path {path_id} for student {student_id}")
        
        # Initialize clients
        config = Config.from_env()
        pedagogical_db = PedagogicalDBClient(config)
        moodle = MoodleClient(api_url="https://moodle.example.com", token="mock-token")
        evidence_verifier = EvidenceVerifier(moodle)
        
        # 1. Fetch the learning path
        path = pedagogical_db.get_learning_path(path_id)
        if not path:
            # For demo purposes, create a mock path if not found
            return (jsonify({"error": f"Path {path_id} not found"}), 404, headers)

        # 2. Fetch student facts
        student_attrs = moodle.get_student_attributes(student_id)
        
        # 3. Simulation Logic
        unlocked_nodes = []
        issued_badges = []
        logs = []
        
        # Mocking some scores and completion for the simulation
        mock_scores = request_json.get('mock_scores', {
            "MATH101": 95,
            "activity_score_q1": 85,
            "activity_completed_a1": True
        })
        
        for node in path.nodes:
            logs.append(f"--- Evaluando nodo: {node.label} ({node.id}) ---")
            
            facts = {
                "score": mock_scores.get(node.reference_id, 0),
                "course_id": node.reference_id,
                "attribute": student_attrs,
                **mock_scores # Include activity scores in facts
            }
            
            # 1. Check Advancement Rules (Prerequisites)
            requirements_met = True
            if node.requirements:
                requirements_met = RuleEvaluator.evaluate(node.requirements, facts)
                if requirements_met:
                    logs.append(f"  [OK] Requisitos de avance cumplidos.")
                else:
                    logs.append(f"  [FAIL] Requisitos de avance NO cumplidos.")
            else:
                logs.append(f"  [INFO] Sin requisitos de avance.")

            # 2. Check Evidence (for Competencies)
            evidence_met = True
            if node.type == "competency":
                # Find mappings for this competency
                mappings = [m for m in path.evidence_mappings if m.competency_id == node.id]
                if mappings:
                    logs.append(f"  [INFO] Verificando {len(mappings)} evidencias...")
                    for m in mappings:
                        is_valid = evidence_verifier.verify_evidence(m, student_id, facts)
                        if is_valid:
                            logs.append(f"    - Evidencia '{m.moodle_activity_id}' VALIDADA.")
                        else:
                            logs.append(f"    - Evidencia '{m.moodle_activity_id}' RECHAZADA.")
                            evidence_met = False
                else:
                    logs.append(f"  [WARN] Competencia sin evidencias mapeadas.")
            
            # 3. Final Decision
            if requirements_met and evidence_met:
                unlocked_nodes.append(node.id)
                logs.append(f"  >> NODO DESBLOQUEADO <<")
                if node.type == "competency":
                    issued_badges.append(f"Insignia: {node.label}")
            else:
                logs.append(f"  >> NODO BLOQUEADO <<")

        result = SimulationResult(
            path_id=path_id,
            student_id=student_id,
            unlocked_nodes=unlocked_nodes,
            issued_badges=issued_badges,
            logs=logs,
            success=len(unlocked_nodes) > 0
        )
        
        return (jsonify(result.model_dump(mode="json")), 200, headers)
        
    except Exception as e:
        logger.error(f"Error in simulation: {str(e)}", exc_info=True)
        return (jsonify({"error": str(e)}), 500, headers)
