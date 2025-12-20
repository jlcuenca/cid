"""
AI Service for CID platform.
Handles interaction with Gemini/Vertex AI for pedagogical analysis.
"""

import os
import logging
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from .pedagogical_models import LearningObjectMetadata, MetadataStandard
from .moodle_client import MoodleCourse

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-assisted pedagogical operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.warning("GEMINI_API_KEY not set. AI Service will run in mock mode.")
            self.model = None

    def analyze_course_content(self, course: MoodleCourse) -> LearningObjectMetadata:
        """
        Analyze course content and suggest metadata using Gemini.
        """
        if not self.model:
            return self._mock_analysis(course)
            
        prompt = f"""
        Analiza el siguiente curso de Moodle y sugiere metadatos pedagógicos bajo el estándar IEEE LOM.
        
        Nombre del curso: {course.fullname}
        Resumen: {course.summary}
        Recursos: {', '.join([r.name + ' (' + r.type + ')' for r in course.resources])}
        
        Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
        {{
            "title": "título sugerido",
            "description": "descripción pedagógica",
            "difficulty": "beginner|intermediate|advanced|expert",
            "typical_learning_time": "ej. 40 hours",
            "keywords": ["tag1", "tag2"],
            "language": "es"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Basic JSON extraction from response
            import json
            import re
            
            # Find JSON block
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return LearningObjectMetadata(
                    standard=MetadataStandard.IEEE_LOM,
                    data=data,
                    difficulty=data.get("difficulty"),
                    typical_learning_time=data.get("typical_learning_time"),
                    keywords=data.get("keywords", [])
                )
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            
        return self._mock_analysis(course)

    def _mock_analysis(self, course: MoodleCourse) -> LearningObjectMetadata:
        """Fallback mock analysis."""
        return LearningObjectMetadata(
            standard=MetadataStandard.IEEE_LOM,
            data={
                "title": course.fullname,
                "description": course.summary or "Sin descripción",
                "language": "es"
            },
            difficulty="intermediate",
            typical_learning_time="20 hours",
            keywords=["moodle", "educación", course.shortname]
        )
