from __future__ import annotations

import json


def format_result_summary(result: dict) -> str:
    final_state = result["final_state"]
    routing_result = result["routing_result"]
    return (
        f"Patient: {result['context']['patient_id']}\n"
        f"Risk level: {final_state.get('risk_level')}\n"
        f"Triage priority: {final_state.get('triage_priority')}\n"
        f"Output route: {routing_result.get('destination')}\n"
        f"Automation confidence: {final_state.get('automation_confidence')}\n"
        f"Safety issues: {len(final_state.get('safety_issues', []))}\n\n"
        f"SOAP Note\n{final_state.get('soap_note', 'N/A')}"
    )


def format_result_json(result: dict) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False)
