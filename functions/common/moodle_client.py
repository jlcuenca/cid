"""
Mock Moodle API client for CID platform.
In a real scenario, this would use the Moodle REST API.
"""

from .lms_client import LMSClient, LMSResource, LMSCourse

class MoodleClient(LMSClient):
    """Mock client for Moodle interaction."""
    
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url
        self.token = token

    def get_course_details(self, course_id: str) -> LMSCourse:
        """
        Mock implementation of fetching course details from Moodle.
        """
        # Mock data
        if course_id == "MATH101":
            return LMSCourse(
                id="MATH101",
                fullname="Introducción a las Matemáticas",
                shortname="MATH101",
                summary="Curso básico de álgebra y cálculo.",
                lms_type="moodle",
                resources=[
                    LMSResource(id="q1", name="Examen Final de Cálculo", type="quiz", description="Evaluación integral del curso."),
                    LMSResource(id="f1", name="Foro: Aplicaciones de la Derivada", type="forum", description="Espacio para dudas sobre derivadas."),
                    LMSResource(id="a1", name="Tarea: Optimización", type="assignment", description="Ejercicios de máximos y mínimos."),
                    LMSResource(id="r1", name="Guía de Estudio: Límites", type="resource", description="PDF con ejercicios resueltos.")
                ]
            )
        
        return LMSCourse(
            id=course_id,
            fullname=f"Course {course_id}",
            shortname=f"C{course_id}",
            summary="No summary available.",
            lms_type="moodle",
            resources=[]
        )

    def get_student_attributes(self, student_id: str) -> Dict[str, Any]:
        """
        Mock implementation of fetching student attributes.
        """
        if student_id == "12345":
            return {"becado": True, "promedio": 9.5, "grado": "3ro"}
        return {"becado": False, "promedio": 7.0, "grado": "1ro"}

    def verify_activity_completion(self, student_id: str, activity_id: str) -> bool:
        """Mock verification."""
        return True
