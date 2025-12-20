"""
SIS (Student Information System) Client for CID platform.
Handles retrieval and filtering of student demographic and academic data.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class StudentProfile(BaseModel):
    id: str
    first_name: str
    last_name: str
    age: int
    grade: str
    gpa: float
    scholarship_status: bool = False
    attributes: Dict[str, Any] = {}

class SISClient:
    """Client to interact with the school's SIS."""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """
        Fetch full student profile from SIS.
        """
        # Mock data
        if student_id == "12345":
            return StudentProfile(
                id="12345",
                first_name="Juan",
                last_name="Pérez",
                age=20,
                grade="3ro de Ingeniería",
                gpa=9.2,
                scholarship_status=True,
                attributes={"becado": True, "programa": "Excelencia"}
            )
        return None

    def filter_students_by_criteria(self, criteria: Dict[str, Any]) -> List[str]:
        """
        Filter students based on pedagogical criteria (e.g., age > 18, gpa > 8.5).
        """
        # Mock filtering logic
        logger_info = f"Filtering students with criteria: {criteria}"
        return ["12345", "67890"]  # Returns list of student IDs
