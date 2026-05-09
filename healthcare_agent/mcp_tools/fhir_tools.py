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