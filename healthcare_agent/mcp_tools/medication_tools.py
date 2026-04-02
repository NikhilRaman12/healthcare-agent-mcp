import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def check_drug_drug_interactions(medications: List[Dict[str, Any]]) -> Dict[str, Any]:
    interactions = []
    ddi_database = {
        ("warfarin", "aspirin"): {
            "severity": "high",
            "description": "Increased bleeding risk",
        },
        ("metformin", "contrast_dye"): {
            "severity": "moderate",
            "description": "Lactic acidosis risk",
        },
        ("lisinopril", "potassium"): {
            "severity": "moderate",
            "description": "Hyperkalemia risk",
        },
    }

    med_names = [
        med.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("code", "").lower()
        for med in medications
    ]

    for index, med_one in enumerate(med_names):
        for med_two in med_names[index + 1 :]:
            if (med_one, med_two) in ddi_database:
                interactions.append(
                    {
                        "medication_1": med_one,
                        "medication_2": med_two,
                        **ddi_database[(med_one, med_two)],
                    }
                )

    logger.info("DDI check: %s interactions found", len(interactions))
    return {"interactions": interactions, "interaction_count": len(interactions)}


def check_medication_allergies(
    medications: List[Dict[str, Any]],
    allergies: List[Dict[str, Any]],
) -> Dict[str, Any]:
    conflicts = []
    for medication in medications:
        med_coding = medication.get("medicationCodeableConcept", {}).get("coding", [{}])[0]
        med_code = med_coding.get("code", "")
        med_display = med_coding.get("display", "")

        for allergy in allergies:
            allergy_coding = allergy.get("code", {}).get("coding", [{}])[0]
            allergy_code = allergy_coding.get("code", "")
            allergy_display = allergy_coding.get("display", "")
            reaction = allergy.get("reaction", [{}])[0].get("manifestation", [{}])[0].get("text", "")

            if med_code == allergy_code or med_code.lower() in allergy_display.lower():
                conflicts.append(
                    {
                        "medication": med_display or med_code,
                        "allergen": allergy_display or allergy_code,
                        "reaction": reaction,
                        "severity": allergy.get("criticality", "unknown"),
                    }
                )

    logger.info("Allergy check: %s conflicts found", len(conflicts))
    return {"conflicts": conflicts, "conflict_count": len(conflicts)}
