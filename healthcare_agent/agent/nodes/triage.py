import logging

from healthcare_agent.agent.node_utils import run_node
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import triage_tools

logger = logging.getLogger(__name__)


def triage_node(state: PatientWorkflowState, context: SHARPContext) -> PatientWorkflowState:
    def action() -> PatientWorkflowState:
        risk_assessment = triage_tools.calculate_risk_score(
            state.get("symptoms", []),
            state.get("vital_signs", {}),
        )
        triage_priority = triage_tools.determine_triage_priority(context, risk_assessment)
        logger.info(
            "Triage complete: %s risk, %s priority",
            risk_assessment["risk_level"],
            triage_priority,
        )
        return {
            **state,
            "risk_score": risk_assessment["risk_score"],
            "risk_level": risk_assessment["risk_level"],
            "triage_priority": triage_priority,
            "risk_factors": risk_assessment["risk_factors"],
        }

    return run_node(state=state, context=context, name="triage", action=action)
