from __future__ import annotations

from datetime import datetime
from typing import Any

from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.agent.workflow import PatientWorkflow
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.output import log_workflow_completion, route_to_output


def build_context(
    *,
    patient_id: str,
    encounter_id: str,
    org_id: str,
    fhir_token: str,
    user_id: str = "",
    metadata: dict | None = None,
) -> SHARPContext:
    return SHARPContext(
        patient_id=patient_id,
        encounter_id=encounter_id,
        org_id=org_id,
        fhir_token=fhir_token,
        user_id=user_id,
        metadata=metadata or {},
    )


def build_initial_state(
    context: SHARPContext,
    *,
    chief_complaint: str,
    symptoms: list[str],
    symptom_duration: str,
    vital_signs: dict,
) -> PatientWorkflowState:
    return {
        "patient_id": context.patient_id,
        "encounter_id": context.encounter_id,
        "org_id": context.org_id,
        "fhir_token": context.fhir_token,
        "chief_complaint": chief_complaint,
        "symptoms": symptoms,
        "symptom_duration": symptom_duration,
        "vital_signs": vital_signs,
        "timestamp": datetime.utcnow().isoformat(),
    }


def _sanitize_state(state: PatientWorkflowState) -> dict[str, Any]:
    sanitized = dict(state)
    if sanitized.get("fhir_token"):
        sanitized["fhir_token"] = "[redacted]"
    return sanitized


def run_patient_workflow(
    context: SHARPContext,
    initial_state: PatientWorkflowState,
) -> dict:
    workflow = PatientWorkflow(context)
    final_state = workflow.execute(initial_state)
    routing_result = route_to_output(final_state)
    log_workflow_completion(context, final_state, routing_result)
    return {
        "context": context.as_dict(),
        "final_state": _sanitize_state(final_state),
        "routing_result": routing_result,
    }
