from __future__ import annotations

import logging
from typing import Callable

from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)


def run_node(
    *,
    state: PatientWorkflowState,
    context: SHARPContext,
    name: str,
    action: Callable[[], PatientWorkflowState],
) -> PatientWorkflowState:
    logger.info("%s node started for patient %s", name, context.patient_id)
    try:
        next_state = action()
        next_state["workflow_status"] = name
        return next_state
    except Exception as exc:
        logger.exception("%s node failed", name)
        state["error_message"] = str(exc)
        state["workflow_status"] = "error"
        return state
