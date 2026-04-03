import unittest
from unittest.mock import patch

from healthcare_agent.app import build_initial_state
from healthcare_agent.agent.workflow import PatientWorkflow
from healthcare_agent.context.sharp import SHARPContext


class WorkflowTests(unittest.TestCase):
    @patch("healthcare_agent.agent.nodes.safety.fhir_tools.retrieve_patient_allergies")
    @patch("healthcare_agent.agent.nodes.safety.fhir_tools.retrieve_patient_medications")
    @patch("healthcare_agent.agent.nodes.intake.fhir_tools.retrieve_patient_summary")
    def test_workflow_completes_with_demo_state(
        self,
        retrieve_patient_summary_mock,
        retrieve_patient_medications_mock,
        retrieve_patient_allergies_mock,
    ) -> None:
        retrieve_patient_summary_mock.return_value = {
            "id": "pat-12345",
            "name": "Demo Patient",
            "gender": "unknown",
            "birth_date": "unknown",
        }
        retrieve_patient_medications_mock.return_value = [
            {
                "medicationCodeableConcept": {
                    "coding": [{"code": "aspirin", "display": "Aspirin"}]
                }
            }
        ]
        retrieve_patient_allergies_mock.return_value = []

        context = SHARPContext(
            patient_id="pat-12345",
            fhir_token="demo-token",
            encounter_id="enc-67890",
            org_id="org-99999",
            user_id="dr-smith",
        )
        initial_state = build_initial_state(
            context,
            chief_complaint="Fever and cough for 3 days",
            symptoms=["fever", "cough", "sore throat"],
            symptom_duration="3 days",
            vital_signs={
                "temperature": 38.5,
                "heart_rate": 95,
                "blood_pressure": "120/80",
                "o2_saturation": 97.0,
            },
        )

        final_state = PatientWorkflow(context).execute(initial_state)

        self.assertEqual(final_state["workflow_status"], "routing")
        self.assertEqual(final_state["output_route"], "auto-complete")
        self.assertIn("soap_note", final_state)
        self.assertEqual(final_state["risk_level"], "low")


if __name__ == "__main__":
    unittest.main()
