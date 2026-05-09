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