import logging
from typing import Callable

from healthcare_agent.agent.nodes import doc, intake, router, safety, triage
from healthcare_agent.agent.state import PatientWorkflowState
from healthcare_agent.context.sharp import SHARPContext

logger = logging.getLogger(__name__)


class PatientWorkflow:
    def __init__(self, context: SHARPContext):
        self.context = context
        self.context.log()
        self.steps: tuple[Callable[[PatientWorkflowState, SHARPContext], PatientWorkflowState], ...] = (
            intake.intake_node,
            triage.triage_node,
            safety.safety_node,
            doc.doc_node,
        )

    def execute(self, initial_state: PatientWorkflowState) -> PatientWorkflowState:
        logger.info("Starting workflow for patient %s", self.context.patient_id)
        state = initial_state
        for step in self.steps:
            state = step(state, self.context)
            if state.get("workflow_status") == "error":
                return state

        state = router.router_node(state)
        logger.info("Workflow complete. Route=%s", state.get("output_route"))
        return state
