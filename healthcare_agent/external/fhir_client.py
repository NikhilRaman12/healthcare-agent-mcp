import requests
import logging
from typing import Dict, List, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import settings

logger = logging.getLogger(__name__)

class FHIRClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = base_url or settings.fhir.url
        self.token = token or settings.fhir.token
        self.timeout = timeout or settings.fhir.timeout
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/fhir+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def get(self, resource_path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{resource_path}"
        try:
            resp = self.session.get(url, headers=self._headers(), params=params, timeout=self.timeout)
            resp.raise_for_status()
            logger.info(f"FHIR GET {resource_path}: 200 OK")
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"FHIR GET {resource_path} failed: {str(e)}")
            raise
    
    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        return self.get(f"Patient/{patient_id}")
    
    def get_patient_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        bundle = self.get(f"Condition", params={"patient": patient_id})
        return [entry["resource"] for entry in bundle.get("entry", [])]
    
    def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        bundle = self.get(f"MedicationStatement", params={"patient": patient_id})
        return [entry["resource"] for entry in bundle.get("entry", [])]
    
    def get_patient_allergies(self, patient_id: str) -> List[Dict[str, Any]]:
        bundle = self.get(f"AllergyIntolerance", params={"patient": patient_id})
        return [entry["resource"] for entry in bundle.get("entry", [])]
    
    def get_patient_observations(self, patient_id: str, code: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"patient": patient_id}
        if code:
            params["code"] = code
        bundle = self.get(f"Observation", params=params)
        return [entry["resource"] for entry in bundle.get("entry", [])]

fhir_client = FHIRClient()