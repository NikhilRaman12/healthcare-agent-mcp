# Submission Checklist

## What You Built

This project is a healthcare workflow agent exposed as MCP-compatible tools with SHARP-style healthcare context and optional FHIR-backed retrieval.

Core tools:

- `retrieve_patient_summary`
- `assess_patient_risk`
- `check_medication_safety`
- `run_clinical_workflow`

## Before You Submit

- Confirm `.env` has the right `FHIR_URL` and `FHIR_TOKEN`
- Run the workflow locally:
  - `venv\Scripts\python -m healthcare_agent.main`
- Run tests:
  - `venv\Scripts\python -m unittest discover -s tests -p "test_*.py"`
- Start the MCP server:
  - `venv\Scripts\python -m healthcare_agent.server`
- Verify Prompt Opinion can discover or invoke the MCP tools
- Make sure your demo shows SHARP context fields:
  - `patient_id`
  - `encounter_id`
  - `org_id`
  - `fhir_token`

## Demo Video Outline

Keep it under 3 minutes.

### 1. Problem

"Clinicians need interoperable AI tools that can safely triage patients, use healthcare context, and produce actionable output instead of isolated chat responses."

### 2. What This Project Does

"This submission exposes interoperable healthcare capabilities through MCP tools. It accepts SHARP-style context, optionally retrieves FHIR data, performs triage and medication safety checks, and returns routing plus clinical documentation."

### 3. Show The Tools

Mention these tools on screen:

- `retrieve_patient_summary`
- `assess_patient_risk`
- `check_medication_safety`
- `run_clinical_workflow`

### 4. Show SHARP Context

Point out:

- `patient_id`
- `encounter_id`
- `org_id`
- `fhir_token`

Explain that context is preserved and reused across tool calls.

### 5. Show The End-To-End Result

Run a sample case and show:

- patient summary
- risk score and triage priority
- medication safety output
- final route
- generated SOAP note

### 6. Close

"This project demonstrates how interoperable healthcare agents can turn context-aware intelligence into actionable clinical workflow outputs using MCP, SHARP context, and FHIR-aware tooling."

## Recommended Submission Packaging

Include:

- `healthcare_agent/`
- `tests/`
- `config.py`
- `.env.example`
- `requirements.txt`
- `README.md`
- `SUBMISSION_CHECKLIST.md`

Exclude:

- `venv/`
- `__pycache__/`
- `.pytest_cache/`
- `logs/`
- nested legacy folder `healthcare-agent-mcp/`
