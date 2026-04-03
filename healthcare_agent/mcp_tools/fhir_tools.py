from __future__ import annotations

import logging
from typing import Any, Dict, List

from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.external.fhir_client import fhir_client

logger = logging.getLogger(__name__)


def retrieve_patient_summary(context: SHARPContext) -> Dict[str, Any]:
    patient = _safe_fetch(lambda: fhir_client.get_patient(context.patient_id), _fallback_patient(context))
    name = patient.get("name", [{}])[0]
    given = [_normalize_text(part) for part in name.get("given", [])]
    family = _normalize_text(name.get("family", ""))
    full_name = " ".join([*given, family]).strip() or context.patient_id
    return {
        "id": patient.get("id", context.patient_id),
        "name": full_name,
        "gender": patient.get("gender", "unknown"),
        "birth_date": patient.get("birthDate", "unknown"),
    }


def retrieve_patient_medications(context: SHARPContext) -> List[Dict[str, Any]]:
    return _safe_fetch(
        lambda: fhir_client.get_patient_medications(context.patient_id),
        _fallback_medications(),
    )


def retrieve_patient_allergies(context: SHARPContext) -> List[Dict[str, Any]]:
    return _safe_fetch(
        lambda: fhir_client.get_patient_allergies(context.patient_id),
        _fallback_allergies(),
    )


def _safe_fetch(fetcher, fallback):
    try:
        return fetcher()
    except Exception as exc:  # pragma: no cover
        logger.warning("FHIR lookup failed, using fallback data: %s", exc)
        return fallback


def _normalize_text(value: str) -> str:
    if not isinstance(value, str):
        return value
    if not any(marker in value for marker in ("Ã", "Â", "â")):
        return value
    try:
        repaired = value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value
    return repaired if repaired else value


def _fallback_patient(context: SHARPContext) -> Dict[str, Any]:
    return {
        "id": context.patient_id,
        "name": [{"given": ["Demo"], "family": "Patient"}],
        "gender": "unknown",
        "birthDate": "unknown",
    }


def _fallback_medications() -> List[Dict[str, Any]]:
    return [
        {
            "medicationCodeableConcept": {
                "coding": [{"code": "aspirin", "display": "Aspirin"}]
            }
        }
    ]


def _fallback_allergies() -> List[Dict[str, Any]]:
    return []
