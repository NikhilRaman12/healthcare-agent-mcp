from typing import TypedDict, List, Dict, Any, Optional

class PatientWorkflowState(TypedDict, total=False):
    patient_id: str
    encounter_id: str
    org_id: str
    fhir_token: str
    user_id: str
    patient_summary: Dict[str, Any]
    conditions: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    allergies: List[Dict[str, Any]]
    observations: List[Dict[str, Any]]
    chief_complaint: str
    symptoms: List[str]
    symptom_duration: str
    vital_signs: Dict[str, float]
    risk_score: float
    risk_level: str
    triage_priority: str
    risk_factors: List[str]
    ddi_check: Dict[str, Any]
    allergy_conflicts: Dict[str, Any]
    safety_issues: List[str]
    safety_clear: bool
    soap_note: str
    clinical_assessment: str
    recommended_actions: List[str]
    output_route: str
    automation_confidence: float
    notes_for_reviewer: str
    workflow_status: str
    error_message: Optional[str]
    timestamp: str