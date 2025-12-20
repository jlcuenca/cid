"""
Evidence Verifier for CID platform.
Validates that specific Moodle activities meet the pedagogical criteria for a competency.
"""

from typing import Dict, Any, List
from .pedagogical_models import EvidenceMapping, EvidenceType
from .moodle_client import MoodleClient

class EvidenceVerifier:
    """Verifies evidence from Moodle against pedagogical requirements."""
    
    def __init__(self, moodle_client: MoodleClient):
        self.moodle_client = moodle_client

    def verify_evidence(self, mapping: EvidenceMapping, student_id: str, facts: Dict[str, Any] = {}) -> bool:
        """
        Verify if a student has completed the required evidence in Moodle.
        """
        # In a real scenario, this would call Moodle API to check activity completion/score
        # For simulation, we check the 'facts' provided (mocked scores)
        
        activity_id = mapping.moodle_activity_id
        score = facts.get(f"activity_score_{activity_id}", 0)
        completed = facts.get(f"activity_completed_{activity_id}", False)

        if mapping.moodle_activity_type == EvidenceType.QUIZ:
            # Quizzes usually require a minimum score
            return score >= 80 or completed
        
        if mapping.moodle_activity_type == EvidenceType.ASSIGNMENT:
            # Assignments might require completion
            return completed or score > 0
            
        if mapping.moodle_activity_type == EvidenceType.FORUM:
            return completed
            
        return False

    def get_evidence_narrative(self, mapping: EvidenceMapping) -> str:
        """
        Generates a narrative description of the evidence for Open Badges 3.0.
        """
        return f"El estudiante completó exitosamente la actividad '{mapping.moodle_activity_id}' de tipo {mapping.moodle_activity_type.value} con los criterios: {mapping.rubric_criteria or 'N/A'}."
