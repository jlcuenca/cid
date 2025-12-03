"""
Firestore database utilities for CCA system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from google.cloud import firestore
from .config import Config
from .models import EmissionRule, AuditEvent


class FirestoreClient:
    """Firestore database client for CCA operations."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize Firestore client.
        
        Args:
            config: Application configuration (loads from env if not provided)
        """
        self.config = config or Config.from_env()
        self.db = firestore.Client(project=self.config.project_id)
        self.rules_collection = self.config.firestore_collection_rules
        self.events_collection = self.config.firestore_collection_events
    
    def get_matching_rule(
        self,
        course_id: str,
        evaluation_id: str,
        score: float
    ) -> Optional[EmissionRule]:
        """
        Find a matching emission rule for the given criteria.
        
        Args:
            course_id: Course identifier
            evaluation_id: Evaluation identifier
            score: Student score
            
        Returns:
            Matching EmissionRule or None if no match found
        """
        # Query for active rules matching course and evaluation
        query = (
            self.db.collection(self.rules_collection)
            .where("active", "==", True)
            .where("course_id", "==", course_id)
        )
        
        # If evaluation_id is specified in the rule, it must match
        # Otherwise, the rule applies to all evaluations in the course
        rules = query.stream()
        
        for doc in rules:
            rule_data = doc.to_dict()
            
            # Check if evaluation matches (if specified in rule)
            if rule_data.get("evaluation_id") and rule_data["evaluation_id"] != evaluation_id:
                continue
            
            # Check if score meets minimum requirement
            if score >= rule_data.get("min_score", 0):
                # Convert Firestore document to EmissionRule
                return EmissionRule(
                    rule_id=doc.id,
                    course_id=rule_data["course_id"],
                    evaluation_id=rule_data.get("evaluation_id"),
                    min_score=rule_data["min_score"],
                    badge_template_id=rule_data["badge_template_id"],
                    badge_title=rule_data["badge_title"],
                    active=rule_data["active"],
                    created_at=rule_data.get("created_at", datetime.now()),
                    updated_at=rule_data.get("updated_at", datetime.now()),
                )
        
        return None
    
    def log_event(self, event: AuditEvent) -> str:
        """
        Log an audit event to Firestore.
        
        Args:
            event: AuditEvent to log
            
        Returns:
            Document ID of the logged event
        """
        event_dict = event.model_dump(mode="json")
        
        # Convert datetime to Firestore timestamp
        if isinstance(event_dict.get("timestamp"), str):
            event_dict["timestamp"] = firestore.SERVER_TIMESTAMP
        
        doc_ref = self.db.collection(self.events_collection).document(event.event_id)
        doc_ref.set(event_dict)
        
        return doc_ref.id
    
    def create_rule(self, rule: EmissionRule) -> str:
        """
        Create a new emission rule.
        
        Args:
            rule: EmissionRule to create
            
        Returns:
            Document ID of the created rule
        """
        rule_dict = rule.model_dump(mode="json")
        doc_ref = self.db.collection(self.rules_collection).document(rule.rule_id)
        doc_ref.set(rule_dict)
        return doc_ref.id
    
    def get_rule(self, rule_id: str) -> Optional[EmissionRule]:
        """
        Get a specific emission rule by ID.
        
        Args:
            rule_id: Rule identifier
            
        Returns:
            EmissionRule or None if not found
        """
        doc = self.db.collection(self.rules_collection).document(rule_id).get()
        
        if not doc.exists:
            return None
        
        rule_data = doc.to_dict()
        return EmissionRule(
            rule_id=doc.id,
            **rule_data
        )
    
    def list_rules(self, course_id: Optional[str] = None, active_only: bool = True) -> List[EmissionRule]:
        """
        List emission rules with optional filtering.
        
        Args:
            course_id: Filter by course ID (optional)
            active_only: Only return active rules
            
        Returns:
            List of EmissionRule objects
        """
        query = self.db.collection(self.rules_collection)
        
        if active_only:
            query = query.where("active", "==", True)
        
        if course_id:
            query = query.where("course_id", "==", course_id)
        
        rules = []
        for doc in query.stream():
            rule_data = doc.to_dict()
            rules.append(EmissionRule(rule_id=doc.id, **rule_data))
        
        return rules
