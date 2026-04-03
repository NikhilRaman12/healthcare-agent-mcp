import json
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)


def _default_audit_log_file() -> Path:
    configured = os.getenv("AUDIT_LOG_FILE", "").strip()
    if configured:
        return Path(configured)
    return Path(tempfile.gettempdir()) / "healthcare-agent-mcp" / "audit.log"


AUDIT_LOG_FILE = _default_audit_log_file()


def log_workflow_completion(
    context: SHARPContext,
    state: PatientWorkflowState,
    routing_result: Dict[str, Any],
) -> None:
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "patient_id": context.patient_id,
        "encounter_id": context.encounter_id,
        "org_id": context.org_id,
        "workflow_status": state.get("workflow_status"),
        "risk_level": state.get("risk_level"),
        "triage_priority": state.get("triage_priority"),
        "output_route": routing_result.get("destination"),
        "automation_confidence": state.get("automation_confidence"),
        "safety_clear": state.get("safety_clear"),
        "safety_issues_count": len(state.get("safety_issues", [])),
    }
    _write_audit_log(audit_entry)
    logger.info("Audit logged: %s -> %s", audit_entry["patient_id"], audit_entry["output_route"])


def _write_audit_log(entry: Dict[str, Any]) -> None:
    try:
        AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as file_handle:
            file_handle.write(json.dumps(entry) + "\n")
    except OSError as exc:
        logger.warning("Audit logging skipped: %s", exc)
