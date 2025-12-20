"""
Abstract Base Class for LMS integration.
Allows the CID platform to connect to Moodle, Canvas, Blackboard, etc.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class LMSResource(BaseModel):
    id: str
    name: str
    type: str  # quiz, forum, resource, assignment, etc.
    description: Optional[str] = None
    url: Optional[str] = None

class LMSCourse(BaseModel):
    id: str
    fullname: str
    shortname: str
    summary: Optional[str] = None
    resources: List[LMSResource] = []
    lms_type: str  # moodle, canvas, etc.

class LMSClient(ABC):
    """Interface for all LMS clients."""

    @abstractmethod
    def get_course_details(self, course_id: str) -> LMSCourse:
        """Fetch course metadata and resources."""
        pass

    @abstractmethod
    def get_student_attributes(self, student_id: str) -> Dict[str, Any]:
        """Fetch student-specific data (grades, completion, etc.)."""
        pass

    @abstractmethod
    def verify_activity_completion(self, student_id: str, activity_id: str) -> bool:
        """Check if a specific activity is completed by a student."""
        pass
