import logging
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


def calculate_risk_score(symptoms: list, vital_signs: Dict[str, Any]) -> Dict[str, Any]:
    score = 0.0
    risk_factors = []
    critical_symptoms = ["chest pain", "difficulty breathing", "loss of consciousness"]
    high_symptoms = ["severe headache", "high fever", "severe pain"]

    for symptom in symptoms:
        symptom_lower = symptom.lower()
        if any(item in symptom_lower for item in critical_symptoms):
            score += 40
            risk_factors.append(f"Critical symptom: {symptom}")
        elif any(item in symptom_lower for item in high_symptoms):
            score += 25
            risk_factors.append(f"High-risk symptom: {symptom}")
        else:
            score += 5

    if vital_signs.get("temperature", 0) > 39.5:
        score += 20
        risk_factors.append("High fever (>39.5 C)")
    if vital_signs.get("heart_rate", 0) > 120 or vital_signs.get("heart_rate", 0) < 50:
        score += 15
        risk_factors.append("Abnormal heart rate")
    if vital_signs.get("o2_saturation", 100) < 94:
        score += 25
        risk_factors.append("Low oxygen saturation (<94%)")

    if score >= 80:
        risk_level = RiskLevel.CRITICAL
    elif score >= 60:
        risk_level = RiskLevel.HIGH
    elif score >= 30:
        risk_level = RiskLevel.MODERATE
    else:
        risk_level = RiskLevel.LOW

    logger.info("Risk assessment: %s (score: %s)", risk_level.value, score)
    return {
        "risk_score": score,
        "risk_level": risk_level.value,
        "risk_factors": risk_factors,
    }


def determine_triage_priority(_context, risk_assessment: Dict[str, Any]) -> str:
    risk_level = risk_assessment.get("risk_level", "low")
    if risk_level in ["critical", "high"]:
        priority = "emergency"
    elif risk_level == "moderate":
        priority = "urgent"
    else:
        priority = "routine"
    logger.info("Triage priority: %s", priority)
    return priority
