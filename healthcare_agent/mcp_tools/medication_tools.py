from typing import Dict, List, Any
import logging
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)

def check_drug_drug_interactions(medications: List[Dict[str, Any]]) -> Dict[str, Any]:
    interactions = []
    ddi_database = {
        ("warfarin", "aspirin"): {"severity": "high", "description": "Increased bleeding risk"},
        ("metformin", "contrast_dye"): {"severity": "moderate", "description": "Lactic acidosis risk"},
        ("lisinopril", "potassium"): {"severity": "moderate", "description": "Hyperkalemia risk"},
    }
    med_names = [med.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("code", "").lower() for med in medications]
    for i, med1 in enumerate(med_names):
        for med2 in med_names[i+1:]:
            if (med1, med2) in ddi_database:
                interactions.append({"medication_1": med1, "medication_2": med2, **ddi_database[(med1, med2)]})
    logger.info(f"DDI check: {len(interactions)} interactions found")
    return {"interactions": interactions, "interaction_count": len(interactions)}

def check_medication_allergies(medications: List[Dict[str, Any]], allergies: List[Dict[str, Any]]) -> Dict[str, Any]:
    conflicts = []
    for med in medications:
        med_code = med.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("code", "")
        med_display = med.get("medicationCodeableConcept", {}).get("coding", [{}])[0].get("display", "")
        for allergy in allergies:
            allergy_code = allergy.get("code", {}).get("coding", [{}])[0].get("code", "")
            allergy_display = allergy.get("code", {}).get("coding", [{}])[0].get("display", "")
            reaction = allergy.get("reaction", [{}])[0].get("manifestation", [{}])[0].get("text", "")
            if med_code == allergy_code or med_code.lower() in allergy_display.lower():
                conflicts.append({"medication": med_display or med_code, "allergen": allergy_display or allergy_code, "reaction": reaction, "severity": allergy.get("criticality", "unknown")})
    logger.warning(f"Allergy check: {len(conflicts)} conflicts found")
    return {"conflicts": conflicts, "conflict_count": len(conflicts)}