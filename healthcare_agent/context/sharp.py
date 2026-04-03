import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class SHARPContext:
    patient_id: str
    fhir_token: str
    encounter_id: str
    org_id: str
    user_id: str = ""
    timestamp: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def as_dict(self, *, redact_secrets: bool = True) -> Dict[str, Any]:
        payload = asdict(self)
        if redact_secrets and payload.get("fhir_token"):
            payload["fhir_token"] = "[redacted]"
        return payload

    def as_json(self, *, redact_secrets: bool = True) -> str:
        return json.dumps(self.as_dict(redact_secrets=redact_secrets), default=str)

    def log(self) -> None:
        logger.info("Context loaded: %s", self.as_json())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SHARPContext":
        return cls(**data)
