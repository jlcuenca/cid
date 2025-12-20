"""
Firestore database utilities for Pedagogical data in CID platform.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from .config import Config
from .pedagogical_models import (
    Taxonomy, Competency, LearningPath, PathNode, 
    EvidenceMapping, LearningObjectMetadata
)

class PedagogicalDBClient:
    """Firestore database client for Pedagogical operations."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.from_env()
        self.db = firestore.Client(project=self.config.project_id)
        
        # Collection names
        self.taxonomies_col = "pedagogical_taxonomies"
        self.competencies_col = "pedagogical_competencies"
        self.paths_col = "pedagogical_learning_paths"
        self.evidence_col = "pedagogical_evidence_mappings"
        self.metadata_col = "pedagogical_course_metadata"

    # Taxonomy Operations
    def create_taxonomy(self, taxonomy: Taxonomy) -> str:
        doc_ref = self.db.collection(self.taxonomies_col).document(taxonomy.id)
        doc_ref.set(taxonomy.model_dump(mode="json"))
        return doc_ref.id

    def get_taxonomy(self, taxonomy_id: str) -> Optional[Taxonomy]:
        doc = self.db.collection(self.taxonomies_col).document(taxonomy_id).get()
        if not doc.exists:
            return None
        return Taxonomy(**doc.to_dict())

    # Competency Operations
    def create_competency(self, competency: Competency) -> str:
        doc_ref = self.db.collection(self.competencies_col).document(competency.id)
        doc_ref.set(competency.model_dump(mode="json"))
        return doc_ref.id

    def list_competencies(self, taxonomy_id: Optional[str] = None) -> List[Competency]:
        query = self.db.collection(self.competencies_col)
        if taxonomy_id:
            query = query.where("taxonomy_id", "==", taxonomy_id)
        
        results = []
        for doc in query.stream():
            results.append(Competency(**doc.to_dict()))
        return results

    # Learning Path Operations
    def create_learning_path(self, path: LearningPath) -> str:
        doc_ref = self.db.collection(self.paths_col).document(path.id)
        doc_ref.set(path.model_dump(mode="json"))
        return doc_ref.id

    def get_learning_path(self, path_id: str) -> Optional[LearningPath]:
        doc = self.db.collection(self.paths_col).document(path_id).get()
        if not doc.exists:
            return None
        return LearningPath(**doc.to_dict())

    # Evidence Mapping Operations
    def create_evidence_mapping(self, mapping: EvidenceMapping) -> str:
        doc_ref = self.db.collection(self.evidence_col).document(mapping.id)
        doc_ref.set(mapping.model_dump(mode="json"))
        return doc_ref.id

    def get_evidence_for_course(self, moodle_course_id: str) -> List[EvidenceMapping]:
        # This assumes we might want to find all mappings related to a course
        # We might need to adjust the model to include course_id if not already there
        # For now, let's just query by moodle_activity_id prefix or similar if applicable
        # Or add a course_id field to EvidenceMapping
        pass

    # Metadata Operations
    def save_course_metadata(self, course_id: str, metadata: LearningObjectMetadata) -> str:
        doc_ref = self.db.collection(self.metadata_col).document(course_id)
        doc_ref.set(metadata.model_dump(mode="json"))
        return doc_ref.id

    def get_course_metadata(self, course_id: str) -> Optional[LearningObjectMetadata]:
        doc = self.db.collection(self.metadata_col).document(course_id).get()
        if not doc.exists:
            return None
        return LearningObjectMetadata(**doc.to_dict())
