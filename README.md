# Healthcare Agent MCP

A small, modular healthcare workflow agent that:

- gathers patient context
- performs simple triage
- runs medication and allergy safety checks
- generates a SOAP note
- routes the case to auto-complete, physician review, or escalation
- can now be exposed as MCP tools for hackathon-style interoperability

## Project Structure

`healthcare_agent/`

- `agent/`: workflow orchestration and nodes
- `context/`: shared request context
- `external/`: FHIR client
- `mcp_tools/`: domain-specific helper logic
- `output/`: routing and audit logging

## How To Run

```powershell
venv\Scripts\python -m healthcare_agent.main
```

## Run FastAPI

```powershell
venv\Scripts\python -m uvicorn healthcare_agent.api:app --reload
```

## Run Gradio Demo

```powershell
venv\Scripts\python -m healthcare_agent.gradio_app
```

## Run With Docker

Build:

```powershell
docker build -t healthcare-agent-mcp .
```

Run FastAPI in Docker:

```powershell
docker run --env-file .env -p 8000:8000 healthcare-agent-mcp
```

## Run As MCP Server

```powershell
venv\Scripts\python -m healthcare_agent.server
```

If you have the FastMCP CLI installed, you can also run:

```powershell
fastmcp run healthcare_agent/server.py:mcp
```

The app will try to call the configured FHIR endpoint. If network access is blocked or the patient cannot be fetched, it falls back to safe demo data so the workflow still completes.

## Configuration

Example values are in [.env.example](C:/Users/Nikhil%20Raman%20K/OneDrive/Documents/Raman_Py_Vscode/GenAi_Projects/healthcare-agent-mcp/.env.example).

The config loader supports both:

- `LLM_API_KEY` / `LLM_MODEL_NAME`
- `ANTHROPIC_API_KEY` / `MODEL_NAME`
- `DEMO_PATIENT_IDS` for a 5-patient demo selector

## Run Tests

```powershell
venv\Scripts\python -m unittest discover -s tests -p "test_*.py"
```

## Submission Notes

- The workflow runs end to end from [healthcare_agent/main.py](C:/Users/Nikhil%20Raman%20K/OneDrive/Documents/Raman_Py_Vscode/GenAi_Projects/healthcare-agent-mcp/healthcare_agent/main.py).
- The MCP server entrypoint is [healthcare_agent/server.py](C:/Users/Nikhil%20Raman%20K/OneDrive/Documents/Raman_Py_Vscode/GenAi_Projects/healthcare-agent-mcp/healthcare_agent/server.py).
- Exposed MCP tools:
- `retrieve_patient_summary`
- `assess_patient_risk`
- `check_medication_safety`
- `run_clinical_workflow`
- Audit entries are written to `logs/audit.log`.
- In restricted environments, live FHIR calls may fail and the app will use fallback data instead.
- Submission steps and demo guidance are in [SUBMISSION_CHECKLIST.md](C:/Users/Nikhil%20Raman%20K/OneDrive/Documents/Raman_Py_Vscode/GenAi_Projects/healthcare-agent-mcp/SUBMISSION_CHECKLIST.md).
