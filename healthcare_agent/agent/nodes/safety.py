from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import fhir_tools, medication_tools

logger = logging.getLogger(__name__)

def safety_node(state: PatientWorkflowState, context: SHARPContext) -> Dict[str, Any]:
    logger.info(f"🟠 SAFETY NODE | Patient: {context.patient_id}")
    try:
        medications = fhir_tools.retrieve_patient_medications(context)
        allergies = fhir_tools.retrieve_patient_allergies(context)
        ddi_check = medication_tools.check_drug_drug_interactions(medications)
        allergy_conflicts = medication_tools.check_medication_allergies(medications, allergies)
        safety_issues = []
        if ddi_check["interaction_count"] > 0:
            safety_issues.extend([f"DDI: {inter}" for inter in ddi_check["interactions"]])
        if allergy_conflicts["conflict_count"] > 0:
            safety_issues.extend([f"Allergy: {conf}" for conf in allergy_conflicts["conflicts"]])
        safety_clear = len(safety_issues) == 0
        updated_state = {**state, "medications": medications, "allergies": allergies, "ddi_check": ddi_check, "allergy_conflicts": allergy_conflicts, "safety_issues": safety_issues, "safety_clear": safety_clear, "workflow_status": "safety"}
        logger.info(f"Safety check complete: {len(safety_issues)} issues found")
        return updated_state
    except Exception as e:
        logger.error(f"Safety node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state