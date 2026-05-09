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