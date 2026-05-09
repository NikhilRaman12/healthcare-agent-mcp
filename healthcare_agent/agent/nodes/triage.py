from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import triage_tools

logger = logging.getLogger(__name__)

def triage_node(state: PatientWorkflowState, context: SHARPContext) -> Dict[str, Any]:
    logger.info(f"🟡 TRIAGE NODE | Patient: {context.patient_id}")
    try:
        symptoms = state.get("symptoms", [])
        vital_signs = state.get("vital_signs", {})
        risk_assessment = triage_tools.calculate_risk_score(symptoms, vital_signs)
        triage_priority = triage_tools.determine_triage_priority(context, risk_assessment)
        updated_state = {**state, "risk_score": risk_assessment["risk_score"], "risk_level": risk_assessment["risk_level"], "triage_priority": triage_priority, "risk_factors": risk_assessment["risk_factors"], "workflow_status": "triage"}
        logger.info(f"Triage complete: {risk_assessment['risk_level']} risk, {triage_priority} priority")
        return updated_state
    except Exception as e:
        logger.error(f"Triage node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state