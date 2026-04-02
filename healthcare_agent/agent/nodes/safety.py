import logging

from healthcare_agent.agent.node_utils import run_node
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import fhir_tools, medication_tools

logger = logging.getLogger(__name__)


def safety_node(state: PatientWorkflowState, context: SHARPContext) -> PatientWorkflowState:
    def action() -> PatientWorkflowState:
        medications = fhir_tools.retrieve_patient_medications(context)
        allergies = fhir_tools.retrieve_patient_allergies(context)
        ddi_check = medication_tools.check_drug_drug_interactions(medications)
        allergy_conflicts = medication_tools.check_medication_allergies(medications, allergies)

        safety_issues = []
        if ddi_check["interaction_count"] > 0:
            safety_issues.extend([f"DDI: {item}" for item in ddi_check["interactions"]])
        if allergy_conflicts["conflict_count"] > 0:
            safety_issues.extend([f"Allergy: {item}" for item in allergy_conflicts["conflicts"]])

        logger.info("Safety check complete: %s issue(s) found", len(safety_issues))
        return {
            **state,
            "medications": medications,
            "allergies": allergies,
            "ddi_check": ddi_check,
            "allergy_conflicts": allergy_conflicts,
            "safety_issues": safety_issues,
            "safety_clear": not safety_issues,
        }

    return run_node(state=state, context=context, name="safety", action=action)
