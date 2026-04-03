from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from config import settings

logger = logging.getLogger(__name__)


class FHIRClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.fhir.url).rstrip("/")
        self.token = token or settings.fhir.token
        self.timeout = timeout or settings.fhir.timeout

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/fhir+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, resource_path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = f"?{urlencode(params)}" if params else ""
        url = f"{self.base_url}/{resource_path}{query}"
        request = Request(url, headers=self._headers(), method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                logger.info("FHIR GET %s: %s", resource_path, response.status)
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as exc:
            logger.error("FHIR GET %s failed: %s", resource_path, exc)
            raise

    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        return self.get(f"Patient/{patient_id}")

    def get_patient_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        bundle = self.get("Condition", params={"patient": patient_id})
        return [entry["resource"] for entry in bundle.get("entry", [])]

    def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        bundle = self.get("MedicationStatement", params={"patient": patient_id})
        return [entry["resource"] for entry in bundle.get("entry", [])]

    def get_patient_allergies(self, patient_id: str) -> List[Dict[str, Any]]:
        bundle = self.get("AllergyIntolerance", params={"patient": patient_id})
        return [entry["resource"] for entry in bundle.get("entry", [])]

    def get_patient_observations(
        self,
        patient_id: str,
        code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params = {"patient": patient_id}
        if code:
            params["code"] = code
        bundle = self.get("Observation", params=params)
        return [entry["resource"] for entry in bundle.get("entry", [])]


fhir_client = FHIRClient()
