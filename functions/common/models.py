"""
Data models for CCA system using Pydantic for validation.
Defines API contracts for all Cloud Functions.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class MoodleEvent(BaseModel):
    """Input event from Moodle via Pub/Sub."""
    student_id: str = Field(..., description="Student identifier")
    course_id: str = Field(..., description="Course identifier")
    evaluation_id: str = Field(..., description="Evaluation/assessment identifier")
    score: float = Field(..., ge=0, le=100, description="Score (0-100)")
    timestamp: datetime = Field(..., description="Event timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ValidationRequest(BaseModel):
    """Request to validate badge issuance rule."""
    student_id: str
    course_id: str
    evaluation_id: str
    score: float
    timestamp: datetime


class ValidationResult(BaseModel):
    """Result from rule validation."""
    is_valid: bool = Field(..., description="Whether a rule matched")
    rule_id: Optional[str] = Field(None, description="Matched rule ID")
    badge_template_id: Optional[str] = Field(None, description="Badge template to issue")
    badge_title: Optional[str] = Field(None, description="Badge title")
    reason: Optional[str] = Field(None, description="Validation reason/message")


class BadgeIssueRequest(BaseModel):
    """Request to issue a badge via Acreditta."""
    student_id: str
    badge_template_id: str
    badge_title: str
    course_id: str
    evaluation_id: str
    score: float
    rule_id: str
    metadata: Optional[Dict[str, Any]] = None


class BadgeIssueResponse(BaseModel):
    """Response from Acreditta API."""
    badge_id: str = Field(..., description="Issued badge identifier")
    badge_url: str = Field(..., description="URL to view/share the badge")
    issued_at: datetime = Field(..., description="Issuance timestamp")
    status: str = Field(..., description="Issuance status")


class SISUpdateRequest(BaseModel):
    """Request to update SIS and log event."""
    student_id: str
    badge_id: str
    badge_url: str
    badge_template_id: str
    badge_title: str
    course_id: str
    evaluation_id: str
    score: float
    rule_id: str
    issued_at: datetime
    workflow_execution_id: Optional[str] = None


class SISUpdateResponse(BaseModel):
    """Response from SIS update."""
    updated: bool = Field(..., description="Whether update was successful")
    event_id: str = Field(..., description="Audit event ID")
    message: Optional[str] = Field(None, description="Status message")


class EmissionRule(BaseModel):
    """Badge emission rule stored in Firestore."""
    rule_id: str
    course_id: str
    evaluation_id: Optional[str] = None
    min_score: float = Field(ge=0, le=100)
    badge_template_id: str
    badge_title: str
    active: bool = True
    created_at: datetime
    updated_at: datetime


class AuditEvent(BaseModel):
    """Audit event logged in Firestore."""
    event_id: str
    event_type: str = "badge_issued"
    student_id: str
    badge_id: str
    badge_template_id: str
    course_id: str
    evaluation_id: str
    score: float
    rule_id: str
    workflow_execution_id: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
