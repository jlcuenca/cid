"""
Pedagogical data models for the CID platform.
These models support advanced learning paths, competencies, and metadata.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class TaxonomyType(str, Enum):
    BLOOM = "bloom"
    DIGCOMP = "digcomp"
    ESCO = "esco"
    EUROPASS = "europass"
    CUSTOM = "custom"

class CompetencyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Competency(BaseModel):
    """Represents a skill or knowledge area within a taxonomy."""
    id: str
    name: str
    description: str
    taxonomy_id: str
    level: Optional[CompetencyLevel] = None
    parent_id: Optional[str] = None  # For hierarchical competencies
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Taxonomy(BaseModel):
    """A collection of related competencies."""
    id: str
    name: str
    type: TaxonomyType
    description: str
    version: str
    competencies: List[Competency] = []
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MetadataStandard(str, Enum):
    IEEE_LOM = "ieee_lom"
    DUBLIN_CORE = "dublin_core"
    OPEN_BADGES_3 = "open_badges_3.0"

class LearningObjectMetadata(BaseModel):
    """Advanced metadata for courses or learning objects."""
    standard: MetadataStandard
    data: Dict[str, Any]
    difficulty: Optional[str] = None
    typical_learning_time: Optional[str] = None
    keywords: List[str] = []

class RuleOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

class Condition(BaseModel):
    """A single condition for advancement."""
    field: str  # e.g., "score", "attribute.becado", "course_completed"
    operator: str  # e.g., ">", "==", "contains"
    value: Any

class AdvancementRule(BaseModel):
    """Complex boolean logic for unlocking nodes or badges."""
    id: str
    name: str
    logic_operator: RuleOperator = RuleOperator.AND
    conditions: List[Union[Condition, 'AdvancementRule']] = []

class EvidenceType(str, Enum):
    QUIZ = "quiz"
    FORUM = "forum"
    ASSIGNMENT = "assignment"
    EXTERNAL = "external"

class EvidenceMapping(BaseModel):
    """Links a Moodle activity to a competency/badge."""
    id: str
    moodle_activity_id: str
    moodle_activity_type: EvidenceType
    competency_id: str
    rubric_criteria: Optional[str] = None
    weight: float = 1.0  # How much this evidence counts towards the competency

class PathNode(BaseModel):
    """A node in a learning path."""
    id: str
    type: str  # "course", "competency", "sub_path"
    reference_id: str  # Moodle course ID or Competency ID
    label: str
    position: Dict[str, float] = {"x": 0, "y": 0}  # For visual builder
    requirements: Optional[AdvancementRule] = None
    metadata: Optional[LearningObjectMetadata] = None

class LearningPath(BaseModel):
    """A structured sequence of learning nodes."""
    id: str
    name: str
    description: str
    nodes: List[PathNode]
    edges: List[Dict[str, str]]  # List of {"from": node_id, "to": node_id}
    evidence_mappings: List[EvidenceMapping] = Field(default_factory=list)
    created_by: str  # Doctor ID
    created_at: datetime
    updated_at: datetime
    status: str = "draft"  # draft, published, archived
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SimulationResult(BaseModel):
    """Result of a path simulation for a ghost student."""
    path_id: str
    student_id: str
    unlocked_nodes: List[str]
    issued_badges: List[str]
    logs: List[str]
    success: bool
