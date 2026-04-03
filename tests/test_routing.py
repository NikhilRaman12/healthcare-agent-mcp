import unittest

from healthcare_agent.output.routing import route_to_output


class RoutingTests(unittest.TestCase):
    def test_escalates_when_safety_issue_exists(self) -> None:
        result = route_to_output(
            {
                "output_route": "escalate",
                "risk_level": "critical",
                "safety_issues": ["DDI: warfarin + aspirin"],
            }
        )

        self.assertEqual(result["destination"], "escalate")
        self.assertEqual(result["status"], "escalated")
        self.assertEqual(result["urgency"], "critical")

    def test_physician_review_route_contains_priority(self) -> None:
        result = route_to_output(
            {
                "output_route": "physician-review",
                "triage_priority": "urgent",
                "notes_for_reviewer": "Needs clinician sign-off.",
            }
        )

        self.assertEqual(result["destination"], "physician-review")
        self.assertEqual(result["queue_priority"], "urgent")
        self.assertIn("reviewer_notes", result)


if __name__ == "__main__":
    unittest.main()
