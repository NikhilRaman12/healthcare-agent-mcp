import logging
from datetime import datetime
from typing import Any, Dict

from healthcare_agent.agent.state import PatientWorkflowState

logger = logging.getLogger(__name__)


def route_to_output(state: PatientWorkflowState) -> Dict[str, Any]:
    output_route = state.get("output_route", "physician-review")
    logger.info("Routing output to %s", output_route)

    if output_route == "auto-complete":
        return {
            "destination": "auto-complete",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "message": "Case automatically completed. Documentation saved.",
            "soap_note": state.get("soap_note", ""),
        }

    if output_route == "physician-review":
        return {
            "destination": "physician-review",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending-review",
            "queue_priority": state.get("triage_priority", "routine"),
            "reviewer_notes": state.get("notes_for_reviewer", ""),
            "soap_note": state.get("soap_note", ""),
        }

    if output_route == "escalate":
        logger.warning("Escalating case to on-call physician")
        return {
            "destination": "escalate",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "escalated",
            "urgency": "critical",
            "alert_reason": (
                f"Risk Level: {state.get('risk_level')}. "
                f"Safety Issues: {state.get('safety_issues', [])}"
            ),
            "recommended_contact": "On-call physician",
        }

    return {
        "destination": "physician-review",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "pending-review",
    }
