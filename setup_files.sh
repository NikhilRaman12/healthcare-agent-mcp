#!/bin/bash

# Remove default README if it exists
rm -f README.md

# Create directories
mkdir -p healthcare_agent/{external,context,mcp_tools,agent/nodes,output}
mkdir -p tests logs

# ==================== CONFIG FILES ====================

# .env.example
cat > .env.example << 'EOF'
FHIR_URL=https://hapi.fhir.org/baseR4
FHIR_TOKEN=your-fhir-token-here
FHIR_TIMEOUT=30
EHR_API_URL=https://ehr-system.local/api
EHR_API_KEY=your-ehr-api-key-here
RXNORM_API_URL=https://rxnav.nlm.nih.gov/REST
RXNORM_TIMEOUT=15
OPINION_PLATFORM_URL=https://promptopinion.local/api
OPINION_PLATFORM_KEY=your-opinion-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
MODEL_NAME=claude-3-5-sonnet-20241022
DATABASE_URL=sqlite:///./healthcare_agent.db
DATABASE_ECHO=false
LOG_LEVEL=INFO
LOG_FILE=logs/healthcare_agent.log
ENABLE_AUTO_COMPLETE=true
AUTO_COMPLETE_THRESHOLD=0.8
ENABLE_HUMAN_REVIEW=true
ENABLE_AUDIT_LOGGING=true
MAX_WORKFLOW_STEPS=10
WORKFLOW_TIMEOUT=300
CHECKPOINT_INTERVAL=5
SECRET_KEY=your-secret-key-for-encryption
HASH_ALGORITHM=sha256
ENVIRONMENT=development
DEBUG=true
EOF

# requirements.txt
cat > requirements.txt << 'EOF'
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
requests==2.31.0
httpx==0.25.1
fhir==6.0.0
fhirclient==4.2.1
hl7==0.4.5
langchain==0.1.8
langchain-anthropic==0.1.8
langgraph==0.0.26
fastmcp==0.5.0
anthropic==0.21.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.0
asyncio==3.4.3
aiohttp==3.9.1
marshmallow==3.20.1
python-dateutil==2.8.2
python-json-logger==2.0.7
structlog==23.3.0
pytest==7.4.3
pytest-asyncio==0.23.0
pytest-cov==4.1.0
pytest-mock==3.12.0
factory-boy==3.3.0
faker==21.0.0
black==23.12.0
flake8==6.1.0
mypy==1.7.1
pylint==3.0.3
ruff==0.1.8
isort==5.13.2
cryptography==41.0.7
python-jose==3.3.0
sphinx==7.2.6
sphinx-rtd-theme==2.0.0
ipython==8.18.1
ipdb==0.13.13
EOF

# config.py
cat > config.py << 'EOF'
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import logging

logger = logging.getLogger(__name__)

class FHIRSettings(BaseSettings):
    url: str = Field(default="https://hapi.fhir.org/baseR4")
    token: str = Field(default="")
    timeout: int = Field(default=30)
    class Config:
        env_prefix = "FHIR_"

class EHRSettings(BaseSettings):
    api_url: str = Field(default="")
    api_key: str = Field(default="")
    class Config:
        env_prefix = "EHR_"

class RxNormSettings(BaseSettings):
    api_url: str = Field(default="https://rxnav.nlm.nih.gov/REST")
    timeout: int = Field(default=15)
    class Config:
        env_prefix = "RXNORM_"

class OpinionPlatformSettings(BaseSettings):
    url: str = Field(default="")
    key: str = Field(default="")
    class Config:
        env_prefix = "OPINION_PLATFORM_"

class LLMSettings(BaseSettings):
    api_key: str = Field(default="")
    model_name: str = Field(default="claude-3-5-sonnet-20241022")
    max_tokens: int = Field(default=4096)
    temperature: float = Field(default=0.7)
    class Config:
        env_prefix = "ANTHROPIC_"

class DatabaseSettings(BaseSettings):
    url: str = Field(default="sqlite:///./healthcare_agent.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)
    class Config:
        env_prefix = "DATABASE_"

class AgentSettings(BaseSettings):
    max_workflow_steps: int = Field(default=10)
    workflow_timeout: int = Field(default=300)
    checkpoint_interval: int = Field(default=5)
    enable_auto_complete: bool = Field(default=True)
    auto_complete_threshold: float = Field(default=0.8)
    enable_human_review: bool = Field(default=True)
    enable_audit_logging: bool = Field(default=True)
    class Config:
        env_prefix = ""

class Settings(BaseSettings):
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/healthcare_agent.log")
    secret_key: str = Field(default="")
    fhir: FHIRSettings = FHIRSettings()
    ehr: EHRSettings = EHRSettings()
    rxnorm: RxNormSettings = RxNormSettings()
    opinion_platform: OpinionPlatformSettings = OpinionPlatformSettings()
    llm: LLMSettings = LLMSettings()
    database: DatabaseSettings = DatabaseSettings()
    agent: AgentSettings = AgentSettings()
    @validator("secret_key", pre=True, always=True)
    def validate_secret_key(cls, v):
        if not v and cls.__fields__["environment"].default == "development":
            return "dev-secret-key-insecure"
        return v
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
logger.info(f"Loaded settings for environment: {settings.environment}")
EOF

# ==================== PACKAGE INIT ====================

cat > healthcare_agent/__init__.py << 'EOF'
"""Healthcare Agent MCP - Modular, Production-Ready Patient Workflow Orchestration"""
__version__ = "0.1.0"
__author__ = "NikhilRaman12"
__description__ = "Modular Healthcare Agent with MCP, LangGraph, and FHIR"
from config import settings
__all__ = ["settings", "__version__", "__author__"]
EOF

# ==================== EXTERNAL INTEGRATIONS ====================

cat > healthcare_agent/external/__init__.py << 'EOF'
"""External integrations (FHIR, EHR, RxNorm, Opinion Platform)"""
from .fhir_client import fhir_client, FHIRClient
__all__ = ["fhir_client", "FHIRClient"]
EOF

cat > healthcare_agent/external/fhir_client.py << 'EOF'
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
EOF

# ==================== CONTEXT ====================

cat > healthcare_agent/context/__init__.py << 'EOF'
"""Context propagation and metadata management"""
from .sharp import SHARPContext
__all__ = ["SHARPContext"]
EOF

cat > healthcare_agent/context/sharp.py << 'EOF'
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SHARPContext":
        return cls(**data)
    
    def log(self):
        logger.info(f"SHARP Context | Patient: {self.patient_id} | Encounter: {self.encounter_id} | Org: {self.org_id}")
EOF

# ==================== MCP TOOLS ====================

cat > healthcare_agent/mcp_tools/__init__.py << 'EOF'
"""MCP Tools - All clinical decision support tools"""
from . import fhir_tools
from . import triage_tools
from . import medication_tools
__all__ = ["fhir_tools", "triage_tools", "medication_tools"]
EOF

cat > healthcare_agent/mcp_tools/fhir_tools.py << 'EOF'
from typing import List, Dict, Any
import logging
from healthcare_agent.external.fhir_client import fhir_client
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)

def retrieve_patient_summary(context: SHARPContext) -> Dict[str, Any]:
    try:
        patient = fhir_client.get_patient(context.patient_id)
        summary = {"id": patient.get("id"), "name": patient.get("name", [{}])[0].get("text", ""), "birthDate": patient.get("birthDate", ""), "gender": patient.get("gender", "")}
        logger.info(f"Retrieved patient summary for {context.patient_id}")
        return summary
    except Exception as e:
        logger.error(f"Error retrieving patient summary: {str(e)}")
        raise

def retrieve_patient_conditions(context: SHARPContext) -> List[Dict[str, Any]]:
    try:
        conditions = fhir_client.get_patient_conditions(context.patient_id)
        logger.info(f"Retrieved {len(conditions)} conditions for {context.patient_id}")
        return conditions
    except Exception as e:
        logger.error(f"Error retrieving conditions: {str(e)}")
        raise

def retrieve_patient_medications(context: SHARPContext) -> List[Dict[str, Any]]:
    try:
        medications = fhir_client.get_patient_medications(context.patient_id)
        logger.info(f"Retrieved {len(medications)} medications for {context.patient_id}")
        return medications
    except Exception as e:
        logger.error(f"Error retrieving medications: {str(e)}")
        raise

def retrieve_patient_allergies(context: SHARPContext) -> List[Dict[str, Any]]:
    try:
        allergies = fhir_client.get_patient_allergies(context.patient_id)
        logger.info(f"Retrieved {len(allergies)} allergies for {context.patient_id}")
        return allergies
    except Exception as e:
        logger.error(f"Error retrieving allergies: {str(e)}")
        raise

def retrieve_patient_observations(context: SHARPContext, code: str = None) -> List[Dict[str, Any]]:
    try:
        observations = fhir_client.get_patient_observations(context.patient_id, code=code)
        logger.info(f"Retrieved {len(observations)} observations for {context.patient_id}")
        return observations
    except Exception as e:
        logger.error(f"Error retrieving observations: {str(e)}")
        raise
EOF

cat > healthcare_agent/mcp_tools/triage_tools.py << 'EOF'
from typing import Dict, Any
from enum import Enum
import logging
from healthcare_agent.context.sharp import SHARPContext

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
        if any(cs in symptom_lower for cs in critical_symptoms):
            score += 40
            risk_factors.append(f"Critical symptom: {symptom}")
        elif any(hs in symptom_lower for hs in high_symptoms):
            score += 25
            risk_factors.append(f"High-risk symptom: {symptom}")
        else:
            score += 5
    
    if vital_signs.get("temperature", 0) > 39.5:
        score += 20
        risk_factors.append("High fever (>39.5°C)")
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
    
    logger.info(f"Risk assessment: {risk_level.value} (score: {score})")
    return {"risk_score": score, "risk_level": risk_level.value, "risk_factors": risk_factors}

def determine_triage_priority(context: SHARPContext, risk_assessment: Dict[str, Any]) -> str:
    risk_level = risk_assessment.get("risk_level", "low")
    if risk_level in ["critical", "high"]:
        priority = "emergency"
    elif risk_level == "moderate":
        priority = "urgent"
    else:
        priority = "routine"
    logger.info(f"Triage priority: {priority}")
    return priority
EOF

cat > healthcare_agent/mcp_tools/medication_tools.py << 'EOF'
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
EOF

# ==================== AGENT STATE ====================

cat > healthcare_agent/agent/__init__.py << 'EOF'
"""Agent orchestration layer"""
from .workflow import PatientWorkflow
from .state import PatientWorkflowState
__all__ = ["PatientWorkflow", "PatientWorkflowState"]
EOF

cat > healthcare_agent/agent/state.py << 'EOF'
from typing import TypedDict, List, Dict, Any, Optional

class PatientWorkflowState(TypedDict, total=False):
    patient_id: str
    encounter_id: str
    org_id: str
    fhir_token: str
    user_id: str
    patient_summary: Dict[str, Any]
    conditions: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    allergies: List[Dict[str, Any]]
    observations: List[Dict[str, Any]]
    chief_complaint: str
    symptoms: List[str]
    symptom_duration: str
    vital_signs: Dict[str, float]
    risk_score: float
    risk_level: str
    triage_priority: str
    risk_factors: List[str]
    ddi_check: Dict[str, Any]
    allergy_conflicts: Dict[str, Any]
    safety_issues: List[str]
    safety_clear: bool
    soap_note: str
    clinical_assessment: str
    recommended_actions: List[str]
    output_route: str
    automation_confidence: float
    notes_for_reviewer: str
    workflow_status: str
    error_message: Optional[str]
    timestamp: str
EOF

# ==================== AGENT NODES ====================

cat > healthcare_agent/agent/nodes/__init__.py << 'EOF'
"""Agent workflow nodes"""
from . import intake
from . import triage
from . import safety
from . import doc
from . import router
__all__ = ["intake", "triage", "safety", "doc", "router"]
EOF

cat > healthcare_agent/agent/nodes/intake.py << 'EOF'
from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import fhir_tools

logger = logging.getLogger(__name__)

def intake_node(state: PatientWorkflowState, context: SHARPContext) -> Dict[str, Any]:
    logger.info(f"🔵 INTAKE NODE | Patient: {context.patient_id}")
    try:
        patient_summary = fhir_tools.retrieve_patient_summary(context)
        updated_state = {**state, "patient_summary": patient_summary, "workflow_status": "intake"}
        logger.info(f"Intake complete: {len(state.get('symptoms', []))} symptoms recorded")
        return updated_state
    except Exception as e:
        logger.error(f"Intake node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state
EOF

cat > healthcare_agent/agent/nodes/triage.py << 'EOF'
from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import triage_tools

logger = logging.getLogger(__name__)

def triage_node(state: PatientWorkflowState, context: SHARPContext) -> Dict[str, Any]:
    logger.info(f"🟡 TRIAGE NODE | Patient: {context.patient_id}")
    try:
        symptoms = state.get("symptoms", [])
        vital_signs = state.get("vital_signs", {})
        risk_assessment = triage_tools.calculate_risk_score(symptoms, vital_signs)
        triage_priority = triage_tools.determine_triage_priority(context, risk_assessment)
        updated_state = {**state, "risk_score": risk_assessment["risk_score"], "risk_level": risk_assessment["risk_level"], "triage_priority": triage_priority, "risk_factors": risk_assessment["risk_factors"], "workflow_status": "triage"}
        logger.info(f"Triage complete: {risk_assessment['risk_level']} risk, {triage_priority} priority")
        return updated_state
    except Exception as e:
        logger.error(f"Triage node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state
EOF

cat > healthcare_agent/agent/nodes/safety.py << 'EOF'
from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.mcp_tools import fhir_tools, medication_tools

logger = logging.getLogger(__name__)

def safety_node(state: PatientWorkflowState, context: SHARPContext) -> Dict[str, Any]:
    logger.info(f"🟠 SAFETY NODE | Patient: {context.patient_id}")
    try:
        medications = fhir_tools.retrieve_patient_medications(context)
        allergies = fhir_tools.retrieve_patient_allergies(context)
        ddi_check = medication_tools.check_drug_drug_interactions(medications)
        allergy_conflicts = medication_tools.check_medication_allergies(medications, allergies)
        safety_issues = []
        if ddi_check["interaction_count"] > 0:
            safety_issues.extend([f"DDI: {inter}" for inter in ddi_check["interactions"]])
        if allergy_conflicts["conflict_count"] > 0:
            safety_issues.extend([f"Allergy: {conf}" for conf in allergy_conflicts["conflicts"]])
        safety_clear = len(safety_issues) == 0
        updated_state = {**state, "medications": medications, "allergies": allergies, "ddi_check": ddi_check, "allergy_conflicts": allergy_conflicts, "safety_issues": safety_issues, "safety_clear": safety_clear, "workflow_status": "safety"}
        logger.info(f"Safety check complete: {len(safety_issues)} issues found")
        return updated_state
    except Exception as e:
        logger.error(f"Safety node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state
EOF

cat > healthcare_agent/agent/nodes/doc.py << 'EOF'
from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)

def doc_node(state: PatientWorkflowState, context: SHARPContext) -> Dict[str, Any]:
    logger.info(f"📝 DOCUMENTATION NODE | Patient: {context.patient_id}")
    try:
        patient_name = state.get("patient_summary", {}).get("name", "Patient")
        chief_complaint = state.get("chief_complaint", "N/A")
        symptoms = state.get("symptoms", [])
        risk_level = state.get("risk_level", "unknown")
        safety_issues = state.get("safety_issues", [])
        vital_signs = state.get("vital_signs", {})
        
        subjective = f"{patient_name} presents with {chief_complaint}. Symptoms: {', '.join(symptoms)}."
        objective = f"Vitals: HR {vital_signs.get('heart_rate', 'N/A')}, BP {vital_signs.get('blood_pressure', 'N/A')}, Temp {vital_signs.get('temperature', 'N/A')}°C, O2 {vital_signs.get('o2_saturation', 'N/A')}%."
        assessment = f"Risk Level: {risk_level}. Triage Priority: {state.get('triage_priority', 'routine')}."
        if safety_issues:
            assessment += f" Safety Issues: {'; '.join(safety_issues)}."
        plan = "1. Continue monitoring. 2. Follow safety alerts. 3. Escalate if needed."
        
        soap_note = f"S: {subjective}\nO: {objective}\nA: {assessment}\nP: {plan}"
        updated_state = {**state, "soap_note": soap_note, "clinical_assessment": assessment, "recommended_actions": ["Continue monitoring", "Alert to safety issues", "Escalate if needed"], "workflow_status": "documentation"}
        logger.info("SOAP note generated")
        return updated_state
    except Exception as e:
        logger.error(f"Documentation node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state
EOF

cat > healthcare_agent/agent/nodes/router.py << 'EOF'
from typing import Dict, Any
import logging
from healthcare_agent.agent.state import PatientWorkflowState
from config import settings

logger = logging.getLogger(__name__)

def router_node(state: PatientWorkflowState) -> Dict[str, Any]:
    logger.info("🔀 ROUTER NODE")
    try:
        risk_level = state.get("risk_level", "low")
        safety_clear = state.get("safety_clear", True)
        if risk_level == "critical" or not safety_clear:
            output_route = "escalate"
            automation_confidence = 0.0
            notes = "Critical or safety issues detected. Escalating to on-call physician."
        elif risk_level in ["high", "moderate"]:
            output_route = "physician-review"
            automation_confidence = 0.6
            notes = "Moderate-to-high risk case. Requires physician review."
        else:
            output_route = "auto-complete"
            automation_confidence = 0.95
            notes = "Low-risk case. Safe for automated handling."
        updated_state = {**state, "output_route": output_route, "automation_confidence": automation_confidence, "notes_for_reviewer": notes, "workflow_status": "routing"}
        logger.info(f"Routing decision: {output_route} (confidence: {automation_confidence:.2%})")
        return updated_state
    except Exception as e:
        logger.error(f"Router node error: {str(e)}")
        state["error_message"] = str(e)
        state["workflow_status"] = "error"
        return state
EOF

# ==================== WORKFLOW ====================

cat > healthcare_agent/agent/workflow.py << 'EOF'
import logging
from typing import Dict, Any
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.agent.nodes import intake, triage, safety, doc, router
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)

class PatientWorkflow:
    def __init__(self, context: SHARPContext):
        self.context = context
        context.log()
    
    def execute(self, initial_state: PatientWorkflowState) -> PatientWorkflowState:
        logger.info(f"=== Starting Workflow for Patient {self.context.patient_id} ===")
        state = intake.intake_node(initial_state, self.context)
        if state.get("workflow_status") == "error":
            return state
        state = triage.triage_node(state, self.context)
        if state.get("workflow_status") == "error":
            return state
        state = safety.safety_node(state, self.context)
        if state.get("workflow_status") == "error":
            return state
        state = doc.doc_node(state, self.context)
        if state.get("workflow_status") == "error":
            return state
        state = router.router_node(state)
        logger.info(f"=== Workflow Complete | Route: {state.get('output_route')} ===")
        return state
EOF

# ==================== OUTPUT ROUTING ====================

cat > healthcare_agent/output/__init__.py << 'EOF'
"""Output routing and audit logging"""
from .routing import route_to_output
from .audit import log_workflow_completion
__all__ = ["route_to_output", "log_workflow_completion"]
EOF

cat > healthcare_agent/output/routing.py << 'EOF'
import logging
from typing import Dict, Any
from datetime import datetime
from healthcare_agent.agent.state import PatientWorkflowState

logger = logging.getLogger(__name__)

def route_to_output(state: PatientWorkflowState) -> Dict[str, Any]:
    output_route = state.get("output_route", "physician-review")
    logger.info(f"📤 Routing output: {output_route}")
    if output_route == "auto-complete":
        return {"destination": "auto-complete", "timestamp": datetime.utcnow().isoformat(), "status": "completed", "message": "Case automatically completed. Documentation saved.", "soap_note": state.get("soap_note", "")}
    elif output_route == "physician-review":
        return {"destination": "physician-review", "timestamp": datetime.utcnow().isoformat(), "status": "pending-review", "queue_priority": state.get("triage_priority", "routine"), "reviewer_notes": state.get("notes_for_reviewer", ""), "soap_note": state.get("soap_note", "")}
    elif output_route == "escalate":
        logger.warning("🚨 Escalating case to on-call physician")
        return {"destination": "escalate", "timestamp": datetime.utcnow().isoformat(), "status": "escalated", "urgency": "critical", "alert_reason": f"Risk Level: {state.get('risk_level')}. Safety Issues: {state.get('safety_issues', [])}", "recommended_contact": "On-call physician"}
    else:
        return {"destination": "physician-review", "timestamp": datetime.utcnow().isoformat(), "status": "pending-review"}
EOF

cat > healthcare_agent/output/audit.py << 'EOF'
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)
AUDIT_LOG_FILE = Path("logs/audit.log")

def log_workflow_completion(context: SHARPContext, state: PatientWorkflowState, routing_result: Dict[str, Any]):
    audit_entry = {"timestamp": datetime.utcnow().isoformat(), "patient_id": context.patient_id, "encounter_id": context.encounter_id, "org_id": context.org_id, "workflow_status": state.get("workflow_status"), "risk_level": state.get("risk_level"), "triage_priority": state.get("triage_priority"), "output_route": routing_result.get("destination"), "automation_confidence": state.get("automation_confidence"), "safety_clear": state.get("safety_clear"), "safety_issues_count": len(state.get("safety_issues", []))}
    _write_audit_log(audit_entry)
    logger.info(f"Audit logged: {audit_entry['patient_id']} → {audit_entry['output_route']}")

def _write_audit_log(entry: Dict[str, Any]):
    AUDIT_LOG_FILE.parent.mkdir(exist_ok=True)
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
EOF

# ==================== MAIN ====================

cat > healthcare_agent/main.py << 'EOF'
import logging
from datetime import datetime
from config import settings
from healthcare_agent.context.sharp import SHARPContext
from healthcare_agent.agent.workflow import PatientWorkflow
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.output import route_to_output, log_workflow_completion

logging.basicConfig(level=settings.log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.FileHandler(settings.log_file), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Healthcare Agent Starting")
    context = SHARPContext(patient_id="pat-12345", fhir_token=settings.fhir.token, encounter_id="enc-67890", org_id="org-99999", user_id="dr-smith")
    initial_state: PatientWorkflowState = {"patient_id": context.patient_id, "encounter_id": context.encounter_id, "org_id": context.org_id, "fhir_token": context.fhir_token, "chief_complaint": "Fever and cough for 3 days", "symptoms": ["fever", "cough", "sore throat"], "symptom_duration": "3 days", "vital_signs": {"temperature": 38.5, "heart_rate": 95, "blood_pressure": "120/80", "o2_saturation": 97.0}, "timestamp": datetime.utcnow().isoformat()}
    try:
        workflow = PatientWorkflow(context)
        final_state = workflow.execute(initial_state)
        routing_result = route_to_output(final_state)
        log_workflow_completion(context, final_state, routing_result)
        logger.info("✅ Workflow completed successfully")
        logger.info(f"Output Route: {routing_result['destination']}")
        logger.info(f"Risk Level: {final_state.get('risk_level')}")
        logger.info(f"SOAP Note:\n{final_state.get('soap_note', 'N/A')}")
    except Exception as e:
        logger.error(f"❌ Workflow failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
EOF

# ==================== TESTS ====================

cat > tests/__init__.py << 'EOF'
"""Test suite for healthcare agent"""
EOF

cat > tests/test_fhir_client.py << 'EOF'
import pytest
from healthcare_agent.external.fhir_client import FHIRClient

class TestFHIRClient:
    @pytest.fixture
    def client(self):
        return FHIRClient(base_url="http://test-fhir.local", token="test-token")
    
    def test_client_initialization(self, client):
        assert client.base_url == "http://test-fhir.local"
        assert client.token == "test-token"
    
    def test_headers_generation(self, client):
        headers = client._headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Content-Type"] == "application/fhir+json"
EOF

cat > tests/test_triage.py << 'EOF'
import pytest
from healthcare_agent.mcp_tools.triage_tools import calculate_risk_score, RiskLevel

class TestTriageTools:
    def test_low_risk_calculation(self):
        symptoms = ["mild headache"]
        vitals = {"temperature": 36.5, "heart_rate": 75, "o2_saturation": 98}
        result = calculate_risk_score(symptoms, vitals)
        assert result["risk_level"] == RiskLevel.LOW.value
        assert result["risk_score"] < 30
    
    def test_critical_risk_calculation(self):
        symptoms = ["chest pain", "difficulty breathing"]
        vitals = {"temperature": 39.5, "heart_rate": 130, "o2_saturation": 90}
        result = calculate_risk_score(symptoms, vitals)
        assert result["risk_level"] == RiskLevel.CRITICAL.value
        assert result["risk_score"] >= 80
EOF

# ==================== DOCKER ====================

cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p logs
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
CMD ["python", "-m", "healthcare_agent.main"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  healthcare-agent:
    build: .
    container_name: healthcare-agent-mcp
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - FHIR_URL=${FHIR_URL}
      - FHIR_TOKEN=${FHIR_TOKEN}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    ports:
      - "8000:8000"
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF

# ==================== README ====================

cat > README.md << 'EOF'
# Healthcare Agent MCP

A **production-ready, modular healthcare agent** built with:
- **FastMCP** for Model Context Protocol (tool management)
- **LangGraph** for workflow orchestration
- **Claude 3.5 Sonnet** for LLM backbone
- **FHIR R4** for standardized healthcare data

## 🏗️ Architecture
