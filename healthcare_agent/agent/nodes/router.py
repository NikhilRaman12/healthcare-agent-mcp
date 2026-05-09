from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from config import settings

logger = logging.getLogger(__name__)

def router_node(state: PatientWorkflowState) -> Dict[str, Any]:
    logger.info("🔀 ROUTER NODE")
    try:
        risk_level = state.get("risk_level", "low")
        safety_clear = state.get("safety_clear", True)
        if risk_level == "critical" or not safety_clear:
            output_route = "escalate"
            automation_confidence = 0.0
            notes = "Critical or safety issues detected. Escalating to on-call physician."
        elif risk_level in ["high", "moderate"]:
            output_route = "physician-review"
            automation_confidence = 0.6
            notes = "Moderate-to-high risk case. Requires physician review."
        else:
            output_route = "auto-complete"
            automation_confidence = 0.95
            notes = "Low-risk case. Safe for automated handling."
        updated_state = {**state, "output_route": output_route, "automation_confidence": automation_confidence, "notes_for_reviewer": notes, "workflow_status": "routing"}
        logger.info(f"Routing decision: {output_route} (confidence: {automation_confidence:.2%})")
        return updated_state
    except Exception as e:
        logger.error(f"Router node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state