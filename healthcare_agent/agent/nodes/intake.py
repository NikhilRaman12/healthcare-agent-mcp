import logging

from healthcare_agent.agent.node_utils import run_node
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import fhir_tools

logger = logging.getLogger(__name__)


def intake_node(state: PatientWorkflowState, context: SHARPContext) -> PatientWorkflowState:
    def action() -> PatientWorkflowState:
        patient_summary = fhir_tools.retrieve_patient_summary(context)
        logger.info("Intake captured %s symptom(s)", len(state.get("symptoms", [])))
        return {**state, "patient_summary": patient_summary}

    return run_node(state=state, context=context, name="intake", action=action)
