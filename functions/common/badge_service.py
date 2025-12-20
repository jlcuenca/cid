"""
Open Badges 3.0 Service.
Generates compliant JSON-LD for achievements and assertions.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from .pedagogical_models import Competency, EvidenceMapping, EvidenceType

class BadgeService:
    """Handles Open Badges 3.0 (OB3) generation."""

    def __init__(self, issuer_id: str, issuer_name: str, issuer_url: str):
        self.issuer_id = issuer_id
        self.issuer_name = issuer_name
        self.issuer_url = issuer_url

    def create_achievement(self, competency: Competency, alignment_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an OB3 Achievement object from a Competency.
        """
        achievement = {
            "id": f"https://cid.example.edu/achievements/{competency.id}",
            "type": ["Achievement"],
            "name": competency.name,
            "description": competency.description,
            "achievementType": "Badge",
            "issuer": {
                "id": self.issuer_id,
                "type": "Profile",
                "name": self.issuer_name,
                "url": self.issuer_url
            },
            "criteria": {
                "narrative": f"El estudiante ha demostrado dominio en {competency.name} al nivel {competency.level.value if competency.level else 'N/A'}."
            }
        }

        if alignment_url:
            achievement["alignment"] = [{
                "type": "Alignment",
                "targetName": competency.name,
                "targetUrl": alignment_url,
                "targetFramework": "CID Pedagogical Framework"
            }]

        return achievement

    def create_assertion(self, 
                         student_email: str, 
                         achievement_id: str, 
                         evidence_mappings: List[EvidenceMapping],
                         narratives: List[str]) -> Dict[str, Any]:
        """
        Creates an OB3 Assertion (the actual badge issued to a student).
        """
        assertion_id = str(uuid.uuid4())
        
        evidence_list = []
        for i, mapping in enumerate(evidence_mappings):
            narrative = narratives[i] if i < len(narratives) else f"Completó actividad {mapping.moodle_activity_id}"
            evidence_list.append({
                "id": f"https://moodle.example.edu/mod/{mapping.moodle_activity_type.value}/view.php?id={mapping.moodle_activity_id}",
                "type": ["Evidence"],
                "narrative": narrative
            })

        assertion = {
            "id": f"https://cid.example.edu/assertions/{assertion_id}",
            "type": ["Assertion"],
            "recipient": {
                "type": "id",
                "identity": student_email,
                "hashed": False
            },
            "issuedOn": datetime.utcnow().isoformat() + "Z",
            "achievement": achievement_id,
            "evidence": evidence_list
        }

        return assertion

    def generate_complete_badge_package(self, 
                                       competency: Competency, 
                                       student_email: str, 
                                       evidence_mappings: List[EvidenceMapping],
                                       narratives: List[str]) -> Dict[str, Any]:
        """
        Generates a combined JSON-LD package for the achievement and the assertion.
        """
        achievement = self.create_achievement(competency)
        assertion = self.create_assertion(student_email, achievement["id"], evidence_mappings, narratives)
        
        return {
            "@context": [
                "https://w3id.org/openbadges/v3",
                "https://w3id.org/blockcerts/v3"
            ],
            "type": "Assertion",
            **assertion,
            "achievement": achievement
        }
