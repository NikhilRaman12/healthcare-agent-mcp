from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import fhir_tools

logger = logging.getLogger(__name__)

def intake_node(state: PatientWorkflowState, context: SHARPContext) -> Dict[str, Any]:
    logger.info(f"🔵 INTAKE NODE | Patient: {context.patient_id}")
    try:
        patient_summary = fhir_tools.retrieve_patient_summary(context)
        updated_state = {**state, "patient_summary": patient_summary, "workflow_status": "intake"}
        logger.info(f"Intake complete: {len(state.get('symptoms', []))} symptoms recorded")
        return updated_state
    except Exception as e:
        logger.error(f"Intake node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state