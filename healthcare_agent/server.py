from __future__ import annotations

from config import settings
from healthcare_agent.app import build_context, build_initial_state, run_patient_workflow
from healthcare_agent.mcp_tools import fhir_tools, medication_tools, triage_tools

try:
    from fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "fastmcp is required to run the MCP server. Install project dependencies first."
    ) from exc


mcp = FastMCP("Healthcare Agent MCP Server")


def _context(
    patient_id: str,
    encounter_id: str,
    org_id: str,
    fhir_token: str = "",
    user_id: str = "",
):
    return build_context(
        patient_id=patient_id,
        encounter_id=encounter_id,
        org_id=org_id,
        fhir_token=fhir_token or settings.fhir.token,
        user_id=user_id,
    )


@mcp.tool
def retrieve_patient_summary(
    patient_id: str,
    encounter_id: str,
    org_id: str,
    fhir_token: str = "",
    user_id: str = "",
) -> dict:
    """Fetch a patient summary using SHARP-style healthcare context."""
    context = _context(patient_id, encounter_id, org_id, fhir_token, user_id)
    return {
        "sharp_context": context.as_dict(),
        "patient_summary": fhir_tools.retrieve_patient_summary(context),
    }


@mcp.tool
def assess_patient_risk(
    symptoms: list[str],
    vital_signs: dict,
    patient_id: str,
    encounter_id: str,
    org_id: str,
    chief_complaint: str = "",
    symptom_duration: str = "",
    fhir_token: str = "",
    user_id: str = "",
) -> dict:
    """Score patient risk and assign triage priority."""
    context = _context(patient_id, encounter_id, org_id, fhir_token, user_id)
    risk_assessment = triage_tools.calculate_risk_score(symptoms, vital_signs)
    triage_priority = triage_tools.determine_triage_priority(context, risk_assessment)
    return {
        "sharp_context": context.as_dict(),
        "chief_complaint": chief_complaint,
        "symptom_duration": symptom_duration,
        "risk_score": risk_assessment["risk_score"],
        "risk_level": risk_assessment["risk_level"],
        "risk_factors": risk_assessment["risk_factors"],
        "triage_priority": triage_priority,
    }


@mcp.tool
def check_medication_safety(
    patient_id: str,
    encounter_id: str,
    org_id: str,
    fhir_token: str = "",
    user_id: str = "",
) -> dict:
    """Check medication interactions and allergy conflicts for a patient."""
    context = _context(patient_id, encounter_id, org_id, fhir_token, user_id)
    medications = fhir_tools.retrieve_patient_medications(context)
    allergies = fhir_tools.retrieve_patient_allergies(context)
    ddi_check = medication_tools.check_drug_drug_interactions(medications)
    allergy_conflicts = medication_tools.check_medication_allergies(medications, allergies)
    return {
        "sharp_context": context.as_dict(),
        "medications": medications,
        "allergies": allergies,
        "ddi_check": ddi_check,
        "allergy_conflicts": allergy_conflicts,
        "safety_clear": ddi_check["interaction_count"] == 0 and allergy_conflicts["conflict_count"] == 0,
    }


@mcp.tool
def run_clinical_workflow(
    patient_id: str,
    encounter_id: str,
    org_id: str,
    chief_complaint: str,
    symptoms: list[str],
    symptom_duration: str,
    vital_signs: dict,
    fhir_token: str = "",
    user_id: str = "",
) -> dict:
    """Run the end-to-end healthcare workflow and return routing plus documentation."""
    context = _context(patient_id, encounter_id, org_id, fhir_token, user_id)
    initial_state = build_initial_state(
        context,
        chief_complaint=chief_complaint,
        symptoms=symptoms,
        symptom_duration=symptom_duration,
        vital_signs=vital_signs,
    )
    return run_patient_workflow(context, initial_state)


if __name__ == "__main__":
    mcp.run()
