from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)

def doc_node(state: PatientWorkflowState, context: SHARPContext) -> Dict[str, Any]:
    logger.info(f"📝 DOCUMENTATION NODE | Patient: {context.patient_id}")
    try:
        patient_name = state.get("patient_summary", {}).get("name", "Patient")
        chief_complaint = state.get("chief_complaint", "N/A")
        symptoms = state.get("symptoms", [])
        risk_level = state.get("risk_level", "unknown")
        safety_issues = state.get("safety_issues", [])
        vital_signs = state.get("vital_signs", {})
        
        subjective = f"{patient_name} presents with {chief_complaint}. Symptoms: {', '.join(symptoms)}."
        objective = f"Vitals: HR {vital_signs.get('heart_rate', 'N/A')}, BP {vital_signs.get('blood_pressure', 'N/A')}, Temp {vital_signs.get('temperature', 'N/A')}°C, O2 {vital_signs.get('o2_saturation', 'N/A')}%."
        assessment = f"Risk Level: {risk_level}. Triage Priority: {state.get('triage_priority', 'routine')}."
        if safety_issues:
            assessment += f" Safety Issues: {'; '.join(safety_issues)}."
        plan = "1. Continue monitoring. 2. Follow safety alerts. 3. Escalate if needed."
        
        soap_note = f"S: {subjective}\nO: {objective}\nA: {assessment}\nP: {plan}"
        updated_state = {**state, "soap_note": soap_note, "clinical_assessment": assessment, "recommended_actions": ["Continue monitoring", "Alert to safety issues", "Escalate if needed"], "workflow_status": "documentation"}
        logger.info("SOAP note generated")
        return updated_state
    except Exception as e:
        logger.error(f"Documentation node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state