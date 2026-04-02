from __future__ import annotations

from config import settings


def get_demo_cases() -> list[dict]:
    patient_ids = [item.strip() for item in settings.agent.demo_patient_ids.split(",") if item.strip()]
    if not patient_ids:
        patient_ids = [settings.agent.demo_patient_id]

    scenario_templates = [
        {
            "title": "Respiratory Infection",
            "chief_complaint": "Fever and cough for 3 days",
            "symptoms": ["fever", "cough", "sore throat"],
            "symptom_duration": "3 days",
            "vital_signs": {
                "temperature": 38.5,
                "heart_rate": 95,
                "blood_pressure": "120/80",
                "o2_saturation": 97.0,
            },
        },
        {
            "title": "Chest Pain Review",
            "chief_complaint": "Chest pain with sweating since morning",
            "symptoms": ["chest pain", "sweating", "mild nausea"],
            "symptom_duration": "6 hours",
            "vital_signs": {
                "temperature": 37.0,
                "heart_rate": 108,
                "blood_pressure": "150/95",
                "o2_saturation": 96.0,
            },
        },
        {
            "title": "Breathing Concern",
            "chief_complaint": "Difficulty breathing and fatigue",
            "symptoms": ["difficulty breathing", "fatigue", "cough"],
            "symptom_duration": "1 day",
            "vital_signs": {
                "temperature": 39.8,
                "heart_rate": 126,
                "blood_pressure": "132/86",
                "o2_saturation": 91.0,
            },
        },
        {
            "title": "Headache Evaluation",
            "chief_complaint": "Severe headache with light sensitivity",
            "symptoms": ["severe headache", "nausea", "light sensitivity"],
            "symptom_duration": "12 hours",
            "vital_signs": {
                "temperature": 37.2,
                "heart_rate": 88,
                "blood_pressure": "142/90",
                "o2_saturation": 98.0,
            },
        },
        {
            "title": "Medication Safety Check",
            "chief_complaint": "New rash after taking medicine",
            "symptoms": ["rash", "itching", "mild swelling"],
            "symptom_duration": "2 days",
            "vital_signs": {
                "temperature": 37.6,
                "heart_rate": 82,
                "blood_pressure": "118/76",
                "o2_saturation": 99.0,
            },
        },
    ]

    cases = []
    for index, patient_id in enumerate(patient_ids, start=1):
        scenario = scenario_templates[(index - 1) % len(scenario_templates)]
        cases.append(
            {
                "label": f"Patient {index} - {scenario['title']} ({patient_id})",
                "patient_id": patient_id,
                "encounter_id": settings.agent.demo_encounter_id,
                "org_id": settings.agent.demo_org_id,
                "user_id": settings.agent.demo_user_id,
                "chief_complaint": scenario["chief_complaint"],
                "symptoms": scenario["symptoms"],
                "symptom_duration": scenario["symptom_duration"],
                "vital_signs": scenario["vital_signs"],
            }
        )
    return cases


def get_demo_case(case_label: str | None = None) -> dict:
    cases = get_demo_cases()
    if not case_label:
        return cases[0]
    return next((case for case in cases if case["label"] == case_label), cases[0])
