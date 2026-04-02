import logging

from healthcare_agent.agent.node_utils import run_node
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)


def doc_node(state: PatientWorkflowState, context: SHARPContext) -> PatientWorkflowState:
    def action() -> PatientWorkflowState:
        patient_name = state.get("patient_summary", {}).get("name", "Patient")
        chief_complaint = state.get("chief_complaint", "N/A")
        symptoms = ", ".join(state.get("symptoms", [])) or "none reported"
        vital_signs = state.get("vital_signs", {})

        subjective = f"{patient_name} presents with {chief_complaint}. Symptoms: {symptoms}."
        objective = (
            f"Vitals: HR {vital_signs.get('heart_rate', 'N/A')}, "
            f"BP {vital_signs.get('blood_pressure', 'N/A')}, "
            f"Temp {vital_signs.get('temperature', 'N/A')} C, "
            f"O2 {vital_signs.get('o2_saturation', 'N/A')}%."
        )

        assessment = (
            f"Risk Level: {state.get('risk_level', 'unknown')}. "
            f"Triage Priority: {state.get('triage_priority', 'routine')}."
        )
        safety_issues = state.get("safety_issues", [])
        if safety_issues:
            assessment += f" Safety Issues: {'; '.join(safety_issues)}."

        soap_note = (
            f"S: {subjective}\n"
            f"O: {objective}\n"
            f"A: {assessment}\n"
            "P: 1. Continue monitoring. 2. Follow safety alerts. 3. Escalate if needed."
        )
        logger.info("SOAP note generated")
        return {
            **state,
            "soap_note": soap_note,
            "clinical_assessment": assessment,
            "recommended_actions": [
                "Continue monitoring",
                "Alert to safety issues",
                "Escalate if needed",
            ],
        }

    return run_node(state=state, context=context, name="documentation", action=action)
