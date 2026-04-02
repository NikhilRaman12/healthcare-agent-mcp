import logging
from pathlib import Path
import sys

from config import settings
from healthcare_agent.app import build_context, build_initial_state, run_patient_workflow

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(settings.log_file), logging.StreamHandler()],
    )


def main() -> None:
    configure_logging()
    logger.info("Healthcare agent starting")

    context = build_context(
        patient_id=settings.agent.demo_patient_id,
        encounter_id=settings.agent.demo_encounter_id,
        org_id=settings.agent.demo_org_id,
        fhir_token=settings.fhir.token,
        user_id=settings.agent.demo_user_id,
    )

    try:
        initial_state = build_initial_state(
            context,
            chief_complaint=settings.agent.demo_chief_complaint,
            symptoms=[item.strip() for item in settings.agent.demo_symptoms.split(",") if item.strip()],
            symptom_duration=settings.agent.demo_symptom_duration,
            vital_signs={
                "temperature": settings.agent.demo_temperature,
                "heart_rate": settings.agent.demo_heart_rate,
                "blood_pressure": settings.agent.demo_blood_pressure,
                "o2_saturation": settings.agent.demo_o2_saturation,
            },
        )
        result = run_patient_workflow(context, initial_state)
        final_state = result["final_state"]
        routing_result = result["routing_result"]

        logger.info("Workflow completed successfully")
        logger.info("Output route: %s", routing_result["destination"])
        logger.info("Risk level: %s", final_state.get("risk_level"))
        logger.info("SOAP note:\n%s", final_state.get("soap_note", "N/A"))
    except Exception as exc:
        logger.error("Workflow failed: %s", exc, exc_info=True)


if __name__ == "__main__":
    main()
