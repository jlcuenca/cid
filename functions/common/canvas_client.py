"""
Mock Canvas LMS client for CID platform.
"""

from typing import List, Dict, Any, Optional
from .lms_client import LMSClient, LMSResource, LMSCourse

class CanvasClient(LMSClient):
    """Mock client for Canvas LMS interaction."""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def get_course_details(self, course_id: str) -> LMSCourse:
        """
        Mock implementation of fetching course details from Canvas.
        """
        if course_id == "CANVAS-101":
            return LMSCourse(
                id="CANVAS-101",
                fullname="Advanced Data Science",
                shortname="ADS101",
                summary="Mastering data pipelines and machine learning.",
                lms_type="canvas",
                resources=[
                    LMSResource(id="c1", name="Final Project: Predictive Model", type="assignment", description="Build a model using real-world data."),
                    LMSResource(id="c2", name="Quiz: Neural Networks", type="quiz", description="Deep learning fundamentals."),
                    LMSResource(id="c3", name="Discussion: Ethical AI", type="discussion", description="Debate on AI bias.")
                ]
            )
        
        return LMSCourse(
            id=course_id,
            fullname=f"Canvas Course {course_id}",
            shortname=f"CANV{course_id}",
            lms_type="canvas",
            resources=[]
        )

    def get_student_attributes(self, student_id: str) -> Dict[str, Any]:
        return {"lms": "canvas", "active": True}

    def verify_activity_completion(self, student_id: str, activity_id: str) -> bool:
        return True
