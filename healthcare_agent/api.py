from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from config import settings
from healthcare_agent.app import build_context, build_initial_state, run_patient_workflow
from healthcare_agent.demo_cases import get_demo_case, get_demo_cases

app = FastAPI(title="Healthcare Agent API", version="0.1.0")


class WorkflowRequest(BaseModel):
    patient_id: str
    encounter_id: str
    org_id: str
    chief_complaint: str
    symptoms: list[str] = Field(default_factory=list)
    symptom_duration: str = ""
    vital_signs: dict = Field(default_factory=dict)
    fhir_token: str = ""
    user_id: str = ""


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/demo-cases")
def demo_cases() -> dict:
    return {"cases": get_demo_cases()}


@app.get("/demo-run")
def demo_run(case_label: str | None = None) -> dict:
    case = get_demo_case(case_label)
    context = build_context(
        patient_id=case["patient_id"],
        encounter_id=case["encounter_id"],
        org_id=case["org_id"],
        fhir_token=settings.fhir.token,
        user_id=case["user_id"],
    )
    initial_state = build_initial_state(
        context,
        chief_complaint=case["chief_complaint"],
        symptoms=case["symptoms"],
        symptom_duration=case["symptom_duration"],
        vital_signs=case["vital_signs"],
    )
    return run_patient_workflow(context, initial_state)


@app.post("/run-workflow")
def run_workflow(request: WorkflowRequest) -> dict:
    context = build_context(
        patient_id=request.patient_id,
        encounter_id=request.encounter_id,
        org_id=request.org_id,
        fhir_token=request.fhir_token or settings.fhir.token,
        user_id=request.user_id,
    )
    initial_state = build_initial_state(
        context,
        chief_complaint=request.chief_complaint,
        symptoms=request.symptoms,
        symptom_duration=request.symptom_duration,
        vital_signs=request.vital_signs,
    )
    return run_patient_workflow(context, initial_state)
