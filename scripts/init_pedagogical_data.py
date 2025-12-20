"""
Script to initialize pedagogical test data in Firestore.
"""

import os
import sys
from datetime import datetime

# Add functions directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'functions')))

from common import (
    Config,
    PedagogicalDBClient,
    Taxonomy,
    TaxonomyType,
    Competency,
    CompetencyLevel,
    LearningPath,
    PathNode,
    AdvancementRule,
    Condition,
    RuleOperator
)

def init_data():
    config = Config.from_env()
    db = PedagogicalDBClient(config)
    
    print("Initializing Pedagogical Data...")
    
    # 1. Create a Taxonomy (Bloom)
    bloom = Taxonomy(
        id="bloom-revised",
        name="Bloom's Revised Taxonomy",
        type=TaxonomyType.BLOOM,
        description="Taxonomy for educational learning objectives.",
        version="2.0",
        tags=["educación", "pedagogía"],
        metadata={"source": "Anderson & Krathwohl"}
    )
    db.create_taxonomy(bloom)
    print(f"Created Taxonomy: {bloom.name}")
    
    # 2. Create Competencies
    comp1 = Competency(
        id="comp-math-001",
        name="Derivadas Básicas",
        description="Capacidad para calcular derivadas de funciones polinómicas.",
        taxonomy_id=bloom.id,
        level=CompetencyLevel.INTERMEDIATE,
        tags=["matemáticas", "cálculo"],
        metadata={"area": "STEM"}
    )
    db.create_competency(comp1)
    print(f"Created Competency: {comp1.name}")
    
    # 3. Create a Learning Path
    rule = AdvancementRule(
        id="rule-math-path",
        name="Math Path Requirement",
        logic_operator=RuleOperator.AND,
        conditions=[
            Condition(field="score", operator=">=", value=80),
            Condition(field="attribute.becado", operator="==", value=True)
        ]
    )
    
    path = LearningPath(
        id="path-math-excellence",
        name="Ruta de Excelencia Matemática",
        description="Ruta avanzada para alumnos becados.",
        nodes=[
            PathNode(
                id="node-1",
                type="course",
                reference_id="MATH101",
                label="Matemáticas I",
                requirements=rule
            ),
            PathNode(
                id="node-2",
                type="competency",
                reference_id=comp1.id,
                label="Certificación en Derivadas"
            )
        ],
        edges=[{"from": "node-1", "to": "node-2"}],
        created_by="doctor-001",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tags=["excelencia", "becados"],
        metadata={"priority": "high"}
    )
    db.create_learning_path(path)
    print(f"Created Learning Path: {path.name}")

if __name__ == "__main__":
    # Mock GCP Project ID for local run if not set
    if not os.environ.get("GCP_PROJECT_ID"):
        os.environ["GCP_PROJECT_ID"] = "mock-project"
    
    try:
        init_data()
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This script requires a valid GCP project or a local Firestore emulator.")
