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

if __name__ == "__main__":
    main()