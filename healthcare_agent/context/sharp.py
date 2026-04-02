from dataclasses import dataclass, asdict
from typing import Dict, Any
from datetime import datetime
import json
import logging

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
    
    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def as_json(self) -> str:
        return json.dumps(self.as_dict(), default=str)

    def log(self) -> None:
        logger.info("Context loaded: %s", self.as_json())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SHARPContext":
        return cls(**data)
